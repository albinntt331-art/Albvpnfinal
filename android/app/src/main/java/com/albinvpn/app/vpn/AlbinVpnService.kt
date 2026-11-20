package com.albinvpn.app.vpn

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.content.ComponentName
import android.content.Intent
import android.net.TrafficStats as AndroidTrafficStats
import android.net.VpnService
import android.os.Build
import android.os.ParcelFileDescriptor
import android.service.quicksettings.TileService
import com.albinvpn.app.data.*
import kotlinx.coroutines.*
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import okhttp3.OkHttpClient
import okhttp3.Request
import java.net.InetAddress
import java.net.InetSocketAddress
import java.net.Proxy
import java.util.concurrent.TimeUnit

class AlbinVpnService : VpnService() {

    companion object {
        const val ACTION_START = "com.albinvpn.START"
        const val ACTION_STOP = "com.albinvpn.STOP"
        const val EXTRA_PROFILE_ID = "profile_id"
        private const val CHANNEL_ID = "albinvpn_channel"

        private val _state = MutableStateFlow(ConnectionState.DISCONNECTED)
        val state: StateFlow<ConnectionState> = _state

        private val _stats = MutableStateFlow(TrafficStats())
        val stats: StateFlow<TrafficStats> = _stats

        private val _logs = MutableStateFlow(listOf("Albin-vpn v7 готов к работе."))
        val logs: StateFlow<List<String>> = _logs

        fun appendLog(msg: String) { _logs.value = (_logs.value + msg).takeLast(250) }
        fun clearLogs() { _logs.value = listOf("Журнал очищен.") }
        fun setIps(directIp: String?, exitIp: String?) {
            _stats.value = _stats.value.copy(directIpInfo = directIp, exitIpInfo = exitIp)
        }
    }

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var tunInterface: ParcelFileDescriptor? = null
    private var activeEngine: VpnCoreEngine? = null
    private var activeProfile: VpnProfile? = null
    private var monitorJob: Job? = null
    private var pingJob: Job? = null

    private val socksHttp by lazy {
        OkHttpClient.Builder()
            .proxy(Proxy(Proxy.Type.SOCKS, InetSocketAddress("127.0.0.1", 10808)))
            .connectTimeout(3, TimeUnit.SECONDS)
            .readTimeout(3, TimeUnit.SECONDS)
            .build()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_STOP -> { stopVpn(); stopSelf() }
            ACTION_START -> startVpn(intent.getStringExtra(EXTRA_PROFILE_ID))
        }
        return START_STICKY
    }

    private fun refreshQsTile() {
        runCatching {
            TileService.requestListeningState(this, ComponentName(this, AlbinTileService::class.java))
        }
    }

    private fun startVpn(requestedId: String?) {
        val repo = ProfileRepository(this)
        val allProfiles = repo.loadProfiles()
        if (allProfiles.isEmpty()) {
            val err = "Нет серверов. Добавьте подписку или ключ."
            appendLog("[VPN ERROR] $err")
            _stats.value = _stats.value.copy(errorMessage = err)
            _state.value = ConnectionState.ERROR
            refreshQsTile()
            return
        }

        val settings = repo.loadSettings()

        // STRICT Proxy Apps check: if ONLY_SELECTED has zero apps, warn clearly instead of silently wrapping all apps
        if (settings.vpnMode == VpnMode.PROXY_APPS &&
            settings.perAppPolicy == PerAppPolicy.ONLY_SELECTED &&
            settings.selectedPackages.none { it != packageName }
        ) {
            val err = "Выберите хотя бы одно приложение во вкладке Приложения (или переключитесь на TUN)."
            appendLog("[VPN ERROR] $err")
            _stats.value = _stats.value.copy(errorMessage = err)
            _state.value = ConnectionState.ERROR
            refreshQsTile()
            return
        }

        // Cleanly tear down any existing tunnel before rebuilding (e.g. switching Proxy Apps <-> TUN)
        monitorJob?.cancel(); pingJob?.cancel()
        activeEngine?.stop(); activeEngine = null
        runCatching { tunInterface?.close() }; tunInterface = null

        _state.value = ConnectionState.CONNECTING
        _stats.value = _stats.value.copy(errorMessage = null, exitIpInfo = null)
        refreshQsTile()
        startForeground(1, buildNotification("Подключение Albin-vpn..."))

        scope.launch {
            val targetProfile = if (requestedId == null || requestedId == AUTO_PROFILE_ID) {
                pickBestAutoProfile(repo, allProfiles)
            } else {
                allProfiles.firstOrNull { it.id == requestedId } ?: pickBestAutoProfile(repo, allProfiles)
            }

            if (targetProfile == null) {
                val err = "Сервер не отвечает. Проверьте ключи и интернет."
                appendLog("[VPN ERROR] $err")
                _stats.value = _stats.value.copy(errorMessage = err)
                _state.value = ConnectionState.ERROR
                stopVpn(keepError = true)
                return@launch
            }

            activeProfile = targetProfile
            val displayName = if (requestedId == null || requestedId == AUTO_PROFILE_ID) {
                "Авто → ${targetProfile.name}"
            } else targetProfile.name
            appendLog("[Albin-vpn] Сервер: $displayName (${targetProfile.protocol.uppercase()})")

            val resolvedIp = runCatching { InetAddress.getByName(targetProfile.address).hostAddress }.getOrNull()

            val builder = Builder()
                .setSession("Albin-vpn")
                .setMtu(settings.tunMtu.coerceIn(1280, 1500))
                .addAddress("10.0.0.2", 30)
                .addRoute("0.0.0.0", 0)
                // Always capture IPv6 route too so dual-stack LTE/Wi-Fi never leaks outside VPN!
                .addAddress("fd00::2", 126)
                .addRoute("::", 0)
                .addDnsServer("1.1.1.1")
                .addDnsServer("8.8.8.8")
                .setBlocking(false)

            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) builder.setMetered(false)

            // CRITICAL FIX: NEVER mix addDisallowedApplication() and addAllowedApplication() on the same Builder!
            if (settings.vpnMode == VpnMode.PROXY_APPS) {
                when (settings.perAppPolicy) {
                    PerAppPolicy.ONLY_SELECTED -> {
                        val allowed = settings.selectedPackages.filter { it != packageName }
                        allowed.forEach { pkg ->
                            runCatching { builder.addAllowedApplication(pkg) }
                        }
                        appendLog("[Mode] Proxy Apps (СТРОГО только выбранные: ${allowed.size}, остальные напрямую)")
                    }
                    PerAppPolicy.EXCLUDE_SELECTED -> {
                        runCatching { builder.addDisallowedApplication(packageName) }
                        settings.selectedPackages.forEach { pkg ->
                            runCatching { builder.addDisallowedApplication(pkg) }
                        }
                        appendLog("[Mode] Proxy Apps (исключено напрямую: ${settings.selectedPackages.size}, остальные в VPN)")
                    }
                }
            } else {
                // STRICT TUN: ONLY exclude Albin-vpn itself (prevent loop), 100% of all other traffic forced into VPN!
                runCatching { builder.addDisallowedApplication(packageName) }
                appendLog("[Mode] TUN (СТРОГО 100% трафика устройства в VPN)")
            }

            tunInterface = builder.establish()
            val tunFd = tunInterface?.fd ?: -1
            if (tunFd < 0) {
                val err = "Не удалось открыть TUN-интерфейс."
                appendLog("[VPN ERROR] $err")
                _stats.value = _stats.value.copy(errorMessage = err)
                _state.value = ConnectionState.ERROR
                stopVpn(keepError = true)
                return@launch
            }

            val configJson = ConfigBuilder.buildXrayConfig(targetProfile, settings, resolvedIp)
            val engine = XrayCoreEngine()
            activeEngine = engine

            val started = engine.start(
                context = this@AlbinVpnService,
                configJson = configJson,
                tunFd = tunFd,
                protectFd = { fd -> protect(fd) },
                onLog = { appendLog(it) }
            )

            if (started) {
                _state.value = ConnectionState.CONNECTED
                _stats.value = _stats.value.copy(activeServerName = displayName, errorMessage = null)
                refreshQsTile()
                startForeground(1, buildNotification("Защищено: $displayName"))
                startMonitors(repo, targetProfile)
                launch {
                    delay(800)
                    val directIp = repo.fetchIpInfo(viaLocalSocks = false)
                    val exitIp = repo.fetchIpInfo(viaLocalSocks = true)
                    setIps(directIp, exitIp)
                    appendLog("[IP] Вход: $directIp | Выход (VPN): $exitIp")
                }
            } else {
                val err = "Ядро Xray не запустилось. Откройте Logs."
                _stats.value = _stats.value.copy(errorMessage = err)
                _state.value = ConnectionState.ERROR
                stopVpn(keepError = true)
            }
        }
    }

    private suspend fun pickBestAutoProfile(repo: ProfileRepository, profiles: List<VpnProfile>): VpnProfile? = coroutineScope {
        val priority = profiles.filter { it.isPriority }
        val pool = if (priority.isNotEmpty()) priority else profiles
        val measured = pool.map { p -> async { p to repo.measureTcpPing(p.address, p.port) } }.awaitAll()
        val best = measured.filter { it.second != null }.minByOrNull { it.second!! }?.first
        if (best != null) return@coroutineScope best
        if (priority.isNotEmpty()) {
            val rest = profiles.filterNot { it.isPriority }.map { p -> async { p to repo.measureTcpPing(p.address, p.port) } }.awaitAll()
            rest.filter { it.second != null }.minByOrNull { it.second!! }?.first ?: profiles.firstOrNull()
        } else profiles.firstOrNull()
    }

    private fun startMonitors(repo: ProfileRepository, profile: VpnProfile) {
        monitorJob?.cancel()
        pingJob?.cancel()
        val startMs = System.currentTimeMillis()
        val uid = android.os.Process.myUid()
        var lastTotalRx = AndroidTrafficStats.getTotalRxBytes().coerceAtLeast(0L)
        var lastTotalTx = AndroidTrafficStats.getTotalTxBytes().coerceAtLeast(0L)
        var lastUidRx = AndroidTrafficStats.getUidRxBytes(uid).coerceAtLeast(0L)
        var lastUidTx = AndroidTrafficStats.getUidTxBytes(uid).coerceAtLeast(0L)
        var accRx = 0L; var accTx = 0L; var peakRx = 0L
        var saveCounter = 0; var unsavedRx = 0L; var unsavedTx = 0L

        monitorJob = scope.launch {
            while (isActive && _state.value == ConnectionState.CONNECTED) {
                delay(1000)
                val nowTotalRx = AndroidTrafficStats.getTotalRxBytes().coerceAtLeast(0L)
                val nowTotalTx = AndroidTrafficStats.getTotalTxBytes().coerceAtLeast(0L)
                val nowUidRx = AndroidTrafficStats.getUidRxBytes(uid).coerceAtLeast(0L)
                val nowUidTx = AndroidTrafficStats.getUidTxBytes(uid).coerceAtLeast(0L)

                val dUidRx = (nowUidRx - lastUidRx).coerceAtLeast(0L)
                val dUidTx = (nowUidTx - lastUidTx).coerceAtLeast(0L)
                val dTotRx = (nowTotalRx - lastTotalRx).coerceAtLeast(0L)
                val dTotTx = (nowTotalTx - lastTotalTx).coerceAtLeast(0L)

                val rxBps = if (dUidRx > 0L) dUidRx else dTotRx
                val txBps = if (dUidTx > 0L) dUidTx else dTotTx
                accRx += rxBps; accTx += txBps
                unsavedRx += rxBps; unsavedTx += txBps
                if (rxBps > peakRx) peakRx = rxBps

                lastTotalRx = nowTotalRx; lastTotalTx = nowTotalTx
                lastUidRx = nowUidRx; lastUidTx = nowUidTx

                val cur = _stats.value
                _stats.value = cur.copy(
                    rxBytesPerSec = rxBps, txBytesPerSec = txBps, peakRxBytesPerSec = peakRx,
                    totalRxBytes = accRx, totalTxBytes = accTx,
                    rxHistory = cur.rxHistory.drop(1) + (rxBps / 1024f),
                    txHistory = cur.txHistory.drop(1) + (txBps / 1024f),
                    connectedSeconds = (System.currentTimeMillis() - startMs) / 1000L
                )

                saveCounter++
                if (saveCounter >= 5) {
                    repo.recordServerTraffic(profile, unsavedRx, unsavedTx, 5L)
                    unsavedRx = 0L; unsavedTx = 0L; saveCounter = 0
                }
            }
            if (unsavedRx > 0L || unsavedTx > 0L || saveCounter > 0) {
                repo.recordServerTraffic(profile, unsavedRx, unsavedTx, saveCounter.toLong())
            }
        }

        pingJob = scope.launch {
            while (isActive && _state.value == ConnectionState.CONNECTED) {
                val ms = measureTunnelPing() ?: repo.measureTcpPing(profile.address, profile.port)
                _stats.value = _stats.value.copy(livePingMs = ms)
                delay(3000)
            }
        }
    }

    private fun measureTunnelPing(): Int? = runCatching {
        val t0 = System.currentTimeMillis()
        val req = Request.Builder().url("https://www.gstatic.com/generate_204").head().build()
        socksHttp.newCall(req).execute().use { resp ->
            if (resp.code in 200..399) (System.currentTimeMillis() - t0).toInt() else null
        }
    }.getOrNull()

    private fun stopVpn(keepError: Boolean = false) {
        monitorJob?.cancel(); pingJob?.cancel()
        activeEngine?.stop(); activeEngine = null; activeProfile = null
        runCatching { tunInterface?.close() }; tunInterface = null
        if (!keepError) {
            _state.value = ConnectionState.DISCONNECTED
            _stats.value = TrafficStats()
        }
        refreshQsTile()
        stopForeground(STOP_FOREGROUND_REMOVE)
    }

    private fun buildNotification(text: String): Notification {
        val nm = getSystemService(NotificationManager::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            nm.createNotificationChannel(NotificationChannel(CHANNEL_ID, "Albin-vpn", NotificationManager.IMPORTANCE_LOW))
        }
        return Notification.Builder(this, CHANNEL_ID)
            .setContentTitle("Albin-vpn").setContentText(text)
            .setSmallIcon(android.R.drawable.ic_lock_lock).setOngoing(true).build()
    }

    override fun onDestroy() { stopVpn(); super.onDestroy() }
}
