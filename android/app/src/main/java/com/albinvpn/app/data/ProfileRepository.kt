package com.albinvpn.app.data

import android.content.Context
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import okhttp3.OkHttpClient
import okhttp3.Request
import org.json.JSONObject
import java.net.InetSocketAddress
import java.net.Proxy
import java.net.Socket
import java.util.concurrent.TimeUnit

class ProfileRepository(context: Context) {
    private val prefs = context.getSharedPreferences("albinvpn_store", Context.MODE_PRIVATE)
    private val json = Json { ignoreUnknownKeys = true; encodeDefaults = true }
    private val http = OkHttpClient.Builder()
        .connectTimeout(8, TimeUnit.SECONDS)
        .readTimeout(10, TimeUnit.SECONDS)
        .build()

    fun loadProfiles(): List<VpnProfile> =
        prefs.getString("profiles", null)?.let { runCatching { json.decodeFromString<List<VpnProfile>>(it) }.getOrNull() } ?: emptyList()

    fun saveProfiles(items: List<VpnProfile>) { prefs.edit().putString("profiles", json.encodeToString(items)).apply() }

    fun loadSubscriptions(): List<Subscription> =
        prefs.getString("subscriptions", null)?.let { runCatching { json.decodeFromString<List<Subscription>>(it) }.getOrNull() } ?: emptyList()

    fun saveSubscriptions(items: List<Subscription>) { prefs.edit().putString("subscriptions", json.encodeToString(items)).apply() }

    fun loadSettings(): AppSettings =
        prefs.getString("settings", null)?.let { runCatching { json.decodeFromString<AppSettings>(it) }.getOrNull() } ?: AppSettings()

    fun saveSettings(settings: AppSettings) { prefs.edit().putString("settings", json.encodeToString(settings)).apply() }

    fun loadSelectedProfileId(): String? = prefs.getString("selected_profile_id", null)
    fun saveSelectedProfileId(id: String?) { prefs.edit().putString("selected_profile_id", id).apply() }

    fun loadServerStats(): List<ServerTrafficRecord> =
        prefs.getString("server_stats", null)?.let {
            runCatching { json.decodeFromString<List<ServerTrafficRecord>>(it) }.getOrNull()
        } ?: emptyList()

    fun saveServerStats(items: List<ServerTrafficRecord>) {
        prefs.edit().putString("server_stats", json.encodeToString(items)).apply()
    }

    fun recordServerTraffic(profile: VpnProfile, rxDelta: Long, txDelta: Long, secDelta: Long) {
        if (rxDelta <= 0L && txDelta <= 0L && secDelta <= 0L) return
        val key = "${profile.address}:${profile.port}"
        val list = loadServerStats().toMutableList()
        val idx = list.indexOfFirst { it.serverKey == key }
        if (idx >= 0) {
            val cur = list[idx]
            list[idx] = cur.copy(
                serverName = profile.name,
                rxBytes = cur.rxBytes + rxDelta,
                txBytes = cur.txBytes + txDelta,
                durationSeconds = cur.durationSeconds + secDelta,
                lastUsedMs = System.currentTimeMillis()
            )
        } else {
            list.add(
                0,
                ServerTrafficRecord(
                    serverKey = key,
                    serverName = profile.name,
                    protocol = profile.protocol,
                    address = "${profile.address}:${profile.port}",
                    rxBytes = rxDelta,
                    txBytes = txDelta,
                    durationSeconds = secDelta
                )
            )
        }
        saveServerStats(list.sortedByDescending { it.lastUsedMs }.take(30))
    }

    suspend fun fetchSubscription(sub: Subscription): Pair<Subscription, List<VpnProfile>> = withContext(Dispatchers.IO) {
        val req = Request.Builder().url(sub.url).header("User-Agent", "Albin-vpn/5.0 (Happ; Hiddify)").build()
        http.newCall(req).execute().use { resp ->
            val body = resp.body?.string().orEmpty()
            val userInfo = resp.header("subscription-userinfo").orEmpty()
            var upload = 0L; var download = 0L; var total = 0L; var expire = 0L
            userInfo.split(";").forEach { token ->
                val kv = token.trim().split("=")
                if (kv.size == 2) {
                    val v = kv[1].toLongOrNull() ?: 0L
                    when (kv[0].lowercase()) {
                        "upload" -> upload = v; "download" -> download = v
                        "total" -> total = v; "expire" -> expire = v
                    }
                }
            }
            sub.copy(lastUpdated = System.currentTimeMillis(), usedBytes = upload + download, totalBytes = total, expireTimestamp = expire) to
                UriParser.parseBatch(body, sub.id)
        }
    }

    suspend fun measureTcpPing(host: String, port: Int): Int? = withContext(Dispatchers.IO) {
        runCatching {
            val start = System.currentTimeMillis()
            Socket().use { socket -> socket.connect(InetSocketAddress(host, port), 2000) }
            (System.currentTimeMillis() - start).toInt()
        }.getOrNull()
    }

    /** Fetches IP & Country either directly (ISP/RF) or through Xray local SOCKS5 127.0.0.1:10808 (Exit VPN IP). */
    suspend fun fetchIpInfo(viaLocalSocks: Boolean): String = withContext(Dispatchers.IO) {
        runCatching {
            val client = if (viaLocalSocks) {
                OkHttpClient.Builder()
                    .proxy(Proxy(Proxy.Type.SOCKS, InetSocketAddress("127.0.0.1", 10808)))
                    .connectTimeout(6, TimeUnit.SECONDS)
                    .readTimeout(6, TimeUnit.SECONDS)
                    .build()
            } else http

            val req = Request.Builder().url("https://ipwho.is/").build()
            client.newCall(req).execute().use { resp ->
                val obj = JSONObject(resp.body?.string().orEmpty())
                val ip = obj.optString("ip")
                val cc = obj.optString("country_code")
                val city = obj.optString("city")
                if (ip.isNotBlank()) {
                    if (city.isNotBlank()) "$ip • $city, $cc" else "$ip • $cc"
                } else "—"
            }
        }.getOrDefault("—")
    }
}
