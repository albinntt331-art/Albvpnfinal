package com.albinvpn.app.ui.screens

import androidx.compose.animation.*
import androidx.compose.animation.core.*
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.*
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.hapticfeedback.HapticFeedbackType
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.LocalHapticFeedback
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.albinvpn.app.data.*
import com.albinvpn.app.ui.AlbinVpnViewModel
import com.albinvpn.app.vpn.AlbinVpnService
import kotlin.math.PI
import kotlin.math.cos
import kotlin.math.sin

private fun formatRate(bytesPerSec: Long): String = when {
    bytesPerSec >= 1_000_000L -> "%.1f MB/s".format(bytesPerSec / 1_000_000f)
    bytesPerSec >= 1_000L -> "%.0f KB/s".format(bytesPerSec / 1_000f)
    else -> "$bytesPerSec B/s"
}

private fun formatBytes(bytes: Long): String = when {
    bytes >= 1_000_000_000L -> "%.2f GB".format(bytes / 1_000_000_000f)
    bytes >= 1_000_000L -> "%.1f MB".format(bytes / 1_000_000f)
    bytes >= 1_000L -> "%.0f KB".format(bytes / 1_000f)
    else -> "$bytes B"
}

private fun formatDuration(sec: Long): String {
    val h = sec / 3600; val m = (sec % 3600) / 60; val s = sec % 60
    return "%02d:%02d:%02d".format(h, m, s)
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AlbinVpnApp(vm: AlbinVpnViewModel, onToggleVpn: () -> Unit, onRestartVpn: () -> Unit = {}) {
    var currentTab by remember { mutableIntStateOf(0) }
    var showStatsSheet by remember { mutableStateOf(false) }

    val settings by vm.settings.collectAsState()
    val profiles by vm.profiles.collectAsState()
    val selectedId by vm.selectedProfileId.collectAsState()
    val connState by vm.connectionState.collectAsState()
    val stats by vm.trafficStats.collectAsState()
    val serverStats by vm.serverStats.collectAsState()
    val subs by vm.subscriptions.collectAsState()
    val installedApps by vm.installedApps.collectAsState()
    val logs by vm.logs.collectAsState()

    val str = remember(settings.language) { stringsFor(settings.language) }
    val selectedProfile = profiles.firstOrNull { it.id == selectedId }
    val isConnected = connState == ConnectionState.CONNECTED

    Box(modifier = Modifier.fillMaxSize().background(MaterialTheme.colorScheme.background)) {
        if (settings.auroraEnabled) {
            AuroraNebulaBackground(
                primary = MaterialTheme.colorScheme.primary,
                primaryContainer = MaterialTheme.colorScheme.primaryContainer,
                tertiary = MaterialTheme.colorScheme.tertiary,
                boost = isConnected
            )
        }

        Scaffold(
            containerColor = Color.Transparent,
            contentColor = MaterialTheme.colorScheme.onBackground,
            topBar = {
                TopAppBar(
                    colors = TopAppBarDefaults.topAppBarColors(
                        containerColor = Color.Transparent,
                        titleContentColor = MaterialTheme.colorScheme.onBackground
                    ),
                    title = {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(
                                modifier = Modifier
                                    .size(38.dp)
                                    .clip(CircleShape)
                                    .background(Brush.linearGradient(listOf(MaterialTheme.colorScheme.primary, MaterialTheme.colorScheme.tertiary))),
                                contentAlignment = Alignment.Center
                            ) {
                                Icon(Icons.Rounded.Shield, null, tint = Color.White, modifier = Modifier.size(21.dp))
                            }
                            Spacer(Modifier.width(12.dp))
                            Text("Albin-vpn", style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.ExtraBold, color = MaterialTheme.colorScheme.onBackground)
                        }
                    },
                    actions = {
                        IconButton(onClick = { vm.refreshServerStats(); showStatsSheet = true }) {
                            Icon(Icons.Rounded.BarChart, contentDescription = str.statsTitle, tint = MaterialTheme.colorScheme.primary)
                        }
                        val pingColor = when (val ms = stats.livePingMs) {
                            null -> MaterialTheme.colorScheme.onSurfaceVariant
                            in 0..95 -> Color(0xFF4ADE80)
                            in 96..220 -> Color(0xFFFACC15)
                            else -> Color(0xFFF87171)
                        }
                        Surface(
                            shape = RoundedCornerShape(50),
                            color = MaterialTheme.colorScheme.surfaceContainerHigh,
                            contentColor = pingColor,
                            border = BorderStroke(1.dp, pingColor.copy(alpha = 0.45f)),
                            modifier = Modifier.padding(end = 12.dp)
                        ) {
                            Row(modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
                                Box(Modifier.size(8.dp).clip(CircleShape).background(if (isConnected) pingColor else MaterialTheme.colorScheme.onSurfaceVariant))
                                Spacer(Modifier.width(6.dp))
                                Text(
                                    text = if (isConnected) (stats.livePingMs?.let { "$it ms" } ?: "…") else str.disconnected,
                                    fontSize = 12.sp,
                                    fontWeight = FontWeight.Bold,
                                    color = if (isConnected) pingColor else MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                        }
                    }
                )
            },
            bottomBar = {
                NavigationBar(
                    containerColor = MaterialTheme.colorScheme.surfaceContainer,
                    contentColor = MaterialTheme.colorScheme.onSurface,
                    tonalElevation = 0.dp
                ) {
                    NavigationBarItem(selected = currentTab == 0, onClick = { currentTab = 0 }, icon = { Icon(Icons.Rounded.Shield, null) }, label = { Text(str.navHome) })
                    NavigationBarItem(selected = currentTab == 1, onClick = { currentTab = 1 }, icon = { Icon(Icons.Rounded.Public, null) }, label = { Text(str.navServers) })
                    NavigationBarItem(selected = currentTab == 2, onClick = { currentTab = 2 }, icon = { Icon(Icons.Rounded.Apps, null) }, label = { Text(str.navApps) })
                    NavigationBarItem(selected = currentTab == 3, onClick = { currentTab = 3 }, icon = { Icon(Icons.Rounded.Tune, null) }, label = { Text(str.navSettings) })
                }
            }
        ) { padding ->
            AnimatedContent(
                targetState = currentTab,
                transitionSpec = {
                    (fadeIn(tween(240)) + scaleIn(initialScale = 0.96f, animationSpec = tween(240)))
                        .togetherWith(fadeOut(tween(150)))
                },
                modifier = Modifier.padding(padding).fillMaxSize(),
                label = "tabAnim"
            ) { tab ->
                when (tab) {
                    0 -> HomeScreen(
                        str = str, connState = connState, stats = stats, selectedId = selectedId,
                        activeProfile = selectedProfile, settings = settings,
                        onToggleVpn = onToggleVpn, onOpenServers = { currentTab = 1 },
                        onModeChange = { m ->
                            val changed = m != settings.vpnMode
                            vm.updateSettings { it.copy(vpnMode = m) }
                            if (changed && isConnected) onRestartVpn()
                        },
                        onCheckIps = vm::checkBothIps,
                        onOpenStats = { vm.refreshServerStats(); showStatsSheet = true }
                    )
                    1 -> ServersScreen(
                        str = str, profiles = profiles, subscriptions = subs, selectedId = selectedId,
                        onSelect = vm::selectProfile, onTogglePriority = vm::togglePriority,
                        onDelete = vm::deleteProfile, onImportRaw = vm::importRawKeys,
                        onAddSub = vm::addSubscription, onRefreshSub = vm::refreshSubscription,
                        onPingAll = vm::pingAllProfiles, onSortByPing = vm::sortProfilesByPing
                    )
                    2 -> AppsRoutingScreen(
                        str = str, settings = settings, apps = installedApps,
                        onToggleApp = vm::toggleAppSelected, onClearAll = vm::clearSelectedApps,
                        onPolicyChange = { p -> vm.updateSettings { it.copy(perAppPolicy = p) } }
                    )
                    3 -> SettingsScreen(str = str, settings = settings, logs = logs, onUpdate = vm::updateSettings)
                }
            }
        }
    }

    if (showStatsSheet) {
        ModalBottomSheet(
            onDismissRequest = { showStatsSheet = false },
            containerColor = MaterialTheme.colorScheme.surfaceContainer,
            contentColor = MaterialTheme.colorScheme.onSurface
        ) {
            Column(modifier = Modifier.fillMaxWidth().padding(horizontal = 20.dp, vertical = 8.dp)) {
                Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                    Text(str.statsTitle, style = MaterialTheme.typography.titleLarge, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface)
                    if (serverStats.isNotEmpty()) {
                        TextButton(onClick = vm::resetServerStats) { Text(str.resetStats) }
                    }
                }
                Spacer(Modifier.height(10.dp))
                if (serverStats.isEmpty()) {
                    Text(str.statsEmpty, color = MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.padding(vertical = 24.dp))
                } else {
                    LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.heightIn(max = 380.dp)) {
                        items(serverStats, key = { it.serverKey }) { rec ->
                            Surface(
                                shape = RoundedCornerShape(20.dp),
                                color = MaterialTheme.colorScheme.surfaceContainerHigh,
                                contentColor = MaterialTheme.colorScheme.onSurface,
                                border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
                                modifier = Modifier.fillMaxWidth()
                            ) {
                                Row(modifier = Modifier.padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
                                    Column(Modifier.weight(1f)) {
                                        Text(rec.serverName, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface)
                                        Text("${rec.protocol.uppercase()} • ${rec.address}", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                                        Text("⏱ ${formatDuration(rec.durationSeconds)}", style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.primary)
                                    }
                                    Column(horizontalAlignment = Alignment.End) {
                                        Text("↓ ${formatBytes(rec.rxBytes)}", fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.primary)
                                        Text("↑ ${formatBytes(rec.txBytes)}", fontWeight = FontWeight.Medium, color = MaterialTheme.colorScheme.tertiary, fontSize = 12.sp)
                                    }
                                }
                            }
                        }
                    }
                }
                Spacer(Modifier.height(24.dp))
            }
        }
    }
}

@Composable
private fun AuroraNebulaBackground(primary: Color, primaryContainer: Color, tertiary: Color, boost: Boolean) {
    val inf = rememberInfiniteTransition(label = "nebula")
    val t by inf.animateFloat(0f, (2 * PI).toFloat(), infiniteRepeatable(tween(11000, easing = LinearEasing)), label = "t")
    val intensity by animateFloatAsState(if (boost) 0.50f else 0.28f, tween(900), label = "boost")

    Canvas(modifier = Modifier.fillMaxSize()) {
        val w = size.width; val h = size.height
        val c1 = Offset(w * (0.48f + 0.22f * cos(t)), h * (0.28f + 0.14f * sin(t)))
        val c2 = Offset(w * (0.52f - 0.25f * sin(t * 0.75f)), h * (0.68f + 0.12f * cos(t * 0.75f)))
        val c3 = Offset(w * (0.22f + 0.14f * sin(t * 0.55f)), h * (0.20f + 0.12f * cos(t * 0.55f)))
        drawCircle(Brush.radialGradient(listOf(primary.copy(alpha = intensity), Color.Transparent), center = c1, radius = maxOf(w, h) * 0.62f), maxOf(w, h) * 0.62f, c1)
        drawCircle(Brush.radialGradient(listOf(tertiary.copy(alpha = intensity * 0.75f), Color.Transparent), center = c2, radius = maxOf(w, h) * 0.52f), maxOf(w, h) * 0.52f, c2)
        drawCircle(Brush.radialGradient(listOf(primaryContainer.copy(alpha = intensity * 0.85f), Color.Transparent), center = c3, radius = maxOf(w, h) * 0.45f), maxOf(w, h) * 0.45f, c3)
    }
}

@Composable
private fun ModePillSwitcher(str: UiStrings, current: VpnMode, onChange: (VpnMode) -> Unit) {
    val primary = MaterialTheme.colorScheme.primary
    val tertiary = MaterialTheme.colorScheme.tertiary
    Surface(
        shape = RoundedCornerShape(50),
        color = MaterialTheme.colorScheme.surfaceContainer,
        contentColor = MaterialTheme.colorScheme.onSurface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
        modifier = Modifier.fillMaxWidth().height(50.dp)
    ) {
        Row(modifier = Modifier.fillMaxSize().padding(4.dp), horizontalArrangement = Arrangement.spacedBy(4.dp)) {
            listOf(
                Triple(VpnMode.PROXY_APPS, str.modeProxyApps, Icons.Rounded.Apps),
                Triple(VpnMode.TUN, str.modeTun, Icons.Rounded.VpnLock)
            ).forEach { (mode, label, icon) ->
                val selected = current == mode
                Box(
                    modifier = Modifier
                        .weight(1f).fillMaxHeight().clip(RoundedCornerShape(50))
                        .background(
                            if (selected) Brush.horizontalGradient(listOf(primary, tertiary))
                            else Brush.horizontalGradient(listOf(Color.Transparent, Color.Transparent))
                        )
                        .clickable { onChange(mode) },
                    contentAlignment = Alignment.Center
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(icon, null, Modifier.size(18.dp), tint = if (selected) Color.White else MaterialTheme.colorScheme.onSurfaceVariant)
                        Spacer(Modifier.width(7.dp))
                        Text(label, fontWeight = if (selected) FontWeight.Bold else FontWeight.Medium, fontSize = 13.sp, color = if (selected) Color.White else MaterialTheme.colorScheme.onSurfaceVariant, maxLines = 1)
                    }
                }
            }
        }
    }
}

@Composable
private fun QuantumPowerOrb(
    str: UiStrings,
    connState: ConnectionState,
    connectedSeconds: Long,
    onClick: () -> Unit
) {
    val haptic = LocalHapticFeedback.current
    val isConnected = connState == ConnectionState.CONNECTED
    val isConnecting = connState == ConnectionState.CONNECTING
    val primary = MaterialTheme.colorScheme.primary
    val primaryContainer = MaterialTheme.colorScheme.primaryContainer
    val tertiary = MaterialTheme.colorScheme.tertiary
    val surfHigh = MaterialTheme.colorScheme.surfaceContainerHigh
    val surf = MaterialTheme.colorScheme.surfaceContainer

    val inf = rememberInfiniteTransition(label = "quantumV5")
    val orbit1 by inf.animateFloat(0f, 360f, infiniteRepeatable(tween(if (isConnecting) 950 else 4000, easing = LinearEasing)), label = "o1")
    val orbit2 by inf.animateFloat(360f, 0f, infiniteRepeatable(tween(if (isConnecting) 1500 else 6400, easing = LinearEasing)), label = "o2")
    val orbit3 by inf.animateFloat(0f, 360f, infiniteRepeatable(tween(9000, easing = LinearEasing)), label = "o3")
    val r1 by inf.animateFloat(0f, 1f, infiniteRepeatable(tween(2400, easing = FastOutSlowInEasing)), label = "r1")
    val r2 by inf.animateFloat(0f, 1f, infiniteRepeatable(tween(2400, delayMillis = 800, easing = FastOutSlowInEasing)), label = "r2")
    val r3 by inf.animateFloat(0f, 1f, infiniteRepeatable(tween(2400, delayMillis = 1600, easing = FastOutSlowInEasing)), label = "r3")
    val breathe by inf.animateFloat(0.96f, 1.05f, infiniteRepeatable(tween(1900, easing = FastOutSlowInEasing), RepeatMode.Reverse), label = "br")

    val scale by animateFloatAsState(if (isConnected) 1.06f else 1.0f, spring(dampingRatio = 0.52f, stiffness = 230f), label = "sc")

    Box(contentAlignment = Alignment.Center, modifier = Modifier.size(270.dp)) {
        Canvas(modifier = Modifier.fillMaxSize()) {
            val c = center; val maxR = size.minDimension / 2f
            drawCircle(
                Brush.radialGradient(
                    listOf(primary.copy(if (isConnected) 0.58f else 0.28f), tertiary.copy(if (isConnected) 0.26f else 0.10f), Color.Transparent),
                    center = c, radius = maxR * breathe
                ),
                maxR * breathe, c
            )

            if (isConnected || isConnecting) {
                listOf(r1, r2, r3).forEach { p ->
                    drawCircle(
                        color = primary.copy(alpha = (1f - p) * 0.52f),
                        radius = maxR * (0.62f + 0.36f * p),
                        center = c,
                        style = Stroke(width = 3.2f)
                    )
                }
            }

            rotate(orbit1) {
                drawCircle(Brush.sweepGradient(listOf(primary, Color.Transparent, tertiary, Color.Transparent, primary)), maxR * 0.74f, c, style = Stroke(if (isConnected || isConnecting) 6.5f else 3.5f, cap = StrokeCap.Round))
            }
            rotate(orbit2) {
                drawCircle(Brush.sweepGradient(listOf(Color.Transparent, tertiary.copy(0.9f), Color.Transparent, primary.copy(0.9f))), maxR * 0.82f, c, style = Stroke(3.2f, cap = StrokeCap.Round))
            }
            rotate(orbit3) {
                drawCircle(Brush.sweepGradient(listOf(primary.copy(0.4f), Color.Transparent, Color.Transparent, tertiary.copy(0.4f))), maxR * 0.90f, c, style = Stroke(2f, cap = StrokeCap.Round))
            }

            // 10 orbiting luminous plasma particles
            for (k in 0 until 10) {
                val pr = if (k % 2 == 0) maxR * 0.82f else maxR * 0.90f
                val deg = ((if (k % 2 == 0) orbit1 else orbit2) + k * 36f) * (PI / 180.0)
                val px = c.x + (pr * cos(deg)).toFloat()
                val py = c.y + (pr * sin(deg)).toFloat()
                drawCircle(
                    color = if (k % 2 == 0) primary else tertiary,
                    radius = if (isConnected) (4.5f + (k % 3)) else 3f,
                    center = Offset(px, py)
                )
            }
        }

        // 100% theme-matched Pure Circular Orb (ZERO hardcoded purple, ZERO square!)
        Box(
            modifier = Modifier
                .size(168.dp)
                .scale(scale)
                .clip(CircleShape)
                .background(
                    if (isConnected) Brush.radialGradient(listOf(tertiary, primary, primaryContainer), radius = 290f)
                    else Brush.radialGradient(listOf(surfHigh, surf, MaterialTheme.colorScheme.background), radius = 290f)
                )
                .border(2.2.dp, Brush.linearGradient(listOf(primary, tertiary)), CircleShape)
                .clickable(interactionSource = remember { MutableInteractionSource() }, indication = null) {
                    haptic.performHapticFeedback(HapticFeedbackType.LongPress)
                    onClick()
                },
            contentAlignment = Alignment.Center
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally) {
                Icon(Icons.Rounded.PowerSettingsNew, str.connect, tint = Color.White, modifier = Modifier.size(56.dp))
                Spacer(Modifier.height(6.dp))
                AnimatedContent(targetState = connState, label = "st") { st ->
                    Text(
                        text = when (st) {
                            ConnectionState.DISCONNECTED -> str.connect
                            ConnectionState.CONNECTING -> str.connecting
                            ConnectionState.CONNECTED -> str.connected
                            ConnectionState.ERROR -> str.error
                        },
                        color = Color.White, fontWeight = FontWeight.ExtraBold, fontSize = 17.sp
                    )
                }
                if (isConnected) {
                    Text(formatDuration(connectedSeconds), color = Color.White.copy(0.9f), fontSize = 13.sp, fontWeight = FontWeight.SemiBold)
                }
            }
        }
    }
}

@Composable
private fun DualIpChainCard(
    str: UiStrings,
    stats: TrafficStats,
    isConnected: Boolean,
    onCheckIps: () -> Unit,
    onOpenStats: () -> Unit
) {
    val primary = MaterialTheme.colorScheme.primary
    val tertiary = MaterialTheme.colorScheme.tertiary
    Surface(
        onClick = onCheckIps,
        shape = RoundedCornerShape(22.dp),
        color = MaterialTheme.colorScheme.surfaceContainer,
        contentColor = MaterialTheme.colorScheme.onSurface,
        border = BorderStroke(1.dp, primary.copy(alpha = 0.35f)),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column(modifier = Modifier.padding(14.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(modifier = Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.SpaceBetween) {
                Column(Modifier.weight(1f)) {
                    Text(str.directIpLabel, fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(stats.directIpInfo ?: str.checkIps, fontSize = 12.sp, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface, maxLines = 1, overflow = TextOverflow.Ellipsis)
                }
                Icon(Icons.Rounded.ArrowForward, null, tint = if (isConnected) primary else MaterialTheme.colorScheme.onSurfaceVariant, modifier = Modifier.padding(horizontal = 6.dp).size(18.dp))
                Column(Modifier.weight(1f), horizontalAlignment = Alignment.End) {
                    Text(str.exitIpLabel, fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text(stats.exitIpInfo ?: "—", fontSize = 12.sp, fontWeight = FontWeight.Bold, color = if (isConnected) primary else MaterialTheme.colorScheme.onSurfaceVariant, maxLines = 1, overflow = TextOverflow.Ellipsis)
                }
            }
            if (isConnected) {
                Row(
                    modifier = Modifier.fillMaxWidth().clickable { onOpenStats() },
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text("↓ ${formatBytes(stats.totalRxBytes)}  •  ↑ ${formatBytes(stats.totalTxBytes)}", fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text("${str.peakSpeed}: ${formatRate(stats.peakRxBytesPerSec)}", fontSize = 11.sp, fontWeight = FontWeight.SemiBold, color = tertiary)
                }
            }
        }
    }
}

@Composable
fun HomeScreen(
    str: UiStrings,
    connState: ConnectionState,
    stats: TrafficStats,
    selectedId: String,
    activeProfile: VpnProfile?,
    settings: AppSettings,
    onToggleVpn: () -> Unit,
    onOpenServers: () -> Unit,
    onModeChange: (VpnMode) -> Unit,
    onCheckIps: () -> Unit,
    onOpenStats: () -> Unit
) {
    val isConnected = connState == ConnectionState.CONNECTED
    val primary = MaterialTheme.colorScheme.primary
    val tertiary = MaterialTheme.colorScheme.tertiary

    BoxWithConstraints(modifier = Modifier.fillMaxSize()) {
        val isWideTablet = maxWidth >= 680.dp
        if (isWideTablet) {
            Row(
                modifier = Modifier.fillMaxSize().padding(horizontal = 28.dp, vertical = 12.dp),
                horizontalArrangement = Arrangement.spacedBy(24.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(Modifier.weight(1f).fillMaxHeight(), horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center) {
                    QuantumPowerOrb(str, connState, stats.connectedSeconds, onToggleVpn)
                    stats.errorMessage?.let { err ->
                        Surface(shape = RoundedCornerShape(16.dp), color = MaterialTheme.colorScheme.errorContainer, contentColor = MaterialTheme.colorScheme.onErrorContainer) {
                            Text(err, style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp))
                        }
                    }
                }
                Column(Modifier.weight(1.15f).fillMaxHeight().verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(12.dp, Alignment.CenterVertically)) {
                    ModePillSwitcher(str, settings.vpnMode, onModeChange)
                    DualIpChainCard(str, stats, isConnected, onCheckIps, onOpenStats)
                    Column(Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                        TrafficCard(str.download, formatRate(stats.rxBytesPerSec), stats.rxHistory, primary, Modifier.fillMaxWidth())
                        TrafficCard(str.upload, formatRate(stats.txBytesPerSec), stats.txHistory, tertiary, Modifier.fillMaxWidth())
                    }
                    ActiveServerCard(str, isConnected, stats, selectedId, activeProfile, primary, tertiary, onOpenServers)
                }
            }
        } else {
            Column(
                modifier = Modifier.fillMaxSize().padding(horizontal = 18.dp, vertical = 8.dp).verticalScroll(rememberScrollState()),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(12.dp)
            ) {
                ModePillSwitcher(str, settings.vpnMode, onModeChange)
                QuantumPowerOrb(str, connState, stats.connectedSeconds, onToggleVpn)
                stats.errorMessage?.let { err ->
                    Surface(shape = RoundedCornerShape(16.dp), color = MaterialTheme.colorScheme.errorContainer, contentColor = MaterialTheme.colorScheme.onErrorContainer) {
                        Text(err, style = MaterialTheme.typography.bodySmall, modifier = Modifier.padding(horizontal = 12.dp, vertical = 6.dp))
                    }
                }
                DualIpChainCard(str, stats, isConnected, onCheckIps, onOpenStats)
                Column(Modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(10.dp)) {
                    TrafficCard(str.download, formatRate(stats.rxBytesPerSec), stats.rxHistory, primary, Modifier.fillMaxWidth())
                    TrafficCard(str.upload, formatRate(stats.txBytesPerSec), stats.txHistory, tertiary, Modifier.fillMaxWidth())
                }
                ActiveServerCard(str, isConnected, stats, selectedId, activeProfile, primary, tertiary, onOpenServers)
            }
        }
    }
}

@Composable
private fun ActiveServerCard(
    str: UiStrings, isConnected: Boolean, stats: TrafficStats, selectedId: String,
    activeProfile: VpnProfile?, primary: Color, tertiary: Color, onOpenServers: () -> Unit
) {
    Surface(
        onClick = onOpenServers,
        shape = RoundedCornerShape(26.dp),
        color = MaterialTheme.colorScheme.surfaceContainer,
        contentColor = MaterialTheme.colorScheme.onSurface,
        border = BorderStroke(1.2.dp, Brush.horizontalGradient(listOf(primary.copy(if (isConnected) 0.7f else 0.35f), tertiary.copy(0.35f)))),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(modifier = Modifier.padding(16.dp).fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier = Modifier.size(44.dp).clip(CircleShape).background(Brush.linearGradient(listOf(primary, tertiary))),
                contentAlignment = Alignment.Center
            ) { Icon(if (selectedId == AUTO_PROFILE_ID) Icons.Rounded.AutoAwesome else Icons.Rounded.Public, null, tint = Color.White) }
            Spacer(Modifier.width(14.dp))
            Column(Modifier.weight(1f)) {
                Text(
                    text = if (isConnected && stats.activeServerName.isNotBlank()) stats.activeServerName
                    else if (selectedId == AUTO_PROFILE_ID) str.autoServerTitle
                    else activeProfile?.name ?: str.autoServerTitle,
                    style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface, maxLines = 1, overflow = TextOverflow.Ellipsis
                )
                Text(
                    text = if (selectedId == AUTO_PROFILE_ID) str.autoServerDesc
                    else activeProfile?.let { "${it.protocol.uppercase()} • ${it.address}:${it.port}" } ?: str.noServersYet,
                    style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant, maxLines = 1, overflow = TextOverflow.Ellipsis
                )
            }
            Icon(Icons.Rounded.ChevronRight, null, tint = MaterialTheme.colorScheme.onSurfaceVariant)
        }
    }
}

@Composable
private fun TrafficCard(title: String, value: String, points: List<Float>, accent: Color, modifier: Modifier) {
    Surface(
        shape = RoundedCornerShape(24.dp),
        color = MaterialTheme.colorScheme.surfaceContainer,
        contentColor = MaterialTheme.colorScheme.onSurface,
        border = BorderStroke(1.dp, accent.copy(alpha = 0.35f)),
        modifier = modifier
    ) {
        Column(modifier = Modifier.padding(14.dp)) {
            Text(title, style = MaterialTheme.typography.labelMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Text(value, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.ExtraBold, color = accent)
            Spacer(Modifier.height(6.dp))
            Canvas(modifier = Modifier.fillMaxWidth().height(34.dp)) {
                val maxVal = (points.maxOrNull() ?: 1f).coerceAtLeast(1f)
                val step = if (points.size > 1) size.width / (points.size - 1) else size.width
                val line = Path(); val fill = Path()
                points.forEachIndexed { i, v ->
                    val x = i * step
                    val y = size.height - (v / maxVal) * (size.height * 0.85f) - 2f
                    if (i == 0) {
                        line.moveTo(x, y); fill.moveTo(x, size.height); fill.lineTo(x, y)
                    } else {
                        val px = (i - 1) * step; val py = size.height - (points[i - 1] / maxVal) * (size.height * 0.85f) - 2f
                        val cx = (px + x) / 2f
                        line.cubicTo(cx, py, cx, y, x, y); fill.cubicTo(cx, py, cx, y, x, y)
                    }
                }
                fill.lineTo(size.width, size.height); fill.close()
                drawPath(fill, Brush.verticalGradient(listOf(accent.copy(0.42f), Color.Transparent)))
                drawPath(line, accent, style = Stroke(3.5f, cap = StrokeCap.Round))
            }
        }
    }
}

@Composable
fun ServersScreen(
    str: UiStrings, profiles: List<VpnProfile>, subscriptions: List<Subscription>, selectedId: String,
    onSelect: (String) -> Unit, onTogglePriority: (String) -> Unit, onDelete: (String) -> Unit,
    onImportRaw: (String) -> Int, onAddSub: (String, String) -> Unit, onRefreshSub: (Subscription) -> Unit,
    onPingAll: () -> Unit, onSortByPing: () -> Unit
) {
    val clipboard = LocalClipboardManager.current
    var showAddSub by remember { mutableStateOf(false) }
    var showAddKey by remember { mutableStateOf(false) }
    var subName by remember { mutableStateOf("") }
    var subUrl by remember { mutableStateOf("") }
    var keyText by remember { mutableStateOf("") }

    Column(modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp)) {
        Row(modifier = Modifier.fillMaxWidth().padding(vertical = 8.dp), horizontalArrangement = Arrangement.spacedBy(6.dp)) {
            FilledTonalButton(onClick = { showAddSub = true }, modifier = Modifier.weight(1f), contentPadding = PaddingValues(horizontal = 10.dp)) {
                Icon(Icons.Rounded.Link, null, Modifier.size(16.dp)); Spacer(Modifier.width(4.dp)); Text(str.addSub, maxLines = 1, fontSize = 12.sp)
            }
            FilledTonalButton(onClick = { showAddKey = true }, modifier = Modifier.weight(1f), contentPadding = PaddingValues(horizontal = 10.dp)) {
                Icon(Icons.Rounded.VpnKey, null, Modifier.size(16.dp)); Spacer(Modifier.width(4.dp)); Text(str.addKey, maxLines = 1, fontSize = 12.sp)
            }
            IconButton(onClick = { clipboard.getText()?.text?.let { onImportRaw(it) } }) { Icon(Icons.Rounded.ContentPaste, str.paste) }
            IconButton(onClick = onPingAll) { Icon(Icons.Rounded.Speed, str.pingAll) }
            IconButton(onClick = onSortByPing) { Icon(Icons.Rounded.Sort, str.sortByPing) }
        }

        LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp), contentPadding = PaddingValues(bottom = 16.dp)) {
            item {
                val isAuto = selectedId == AUTO_PROFILE_ID
                Surface(
                    onClick = { onSelect(AUTO_PROFILE_ID) },
                    shape = RoundedCornerShape(24.dp),
                    color = if (isAuto) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceContainer,
                    contentColor = if (isAuto) MaterialTheme.colorScheme.onPrimaryContainer else MaterialTheme.colorScheme.onSurface,
                    border = BorderStroke(1.5.dp, if (isAuto) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outlineVariant),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(modifier = Modifier.padding(16.dp), verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier.size(42.dp).clip(CircleShape)
                                .background(Brush.linearGradient(listOf(MaterialTheme.colorScheme.primary, MaterialTheme.colorScheme.tertiary))),
                            contentAlignment = Alignment.Center
                        ) { Icon(Icons.Rounded.AutoAwesome, null, tint = Color.White) }
                        Spacer(Modifier.width(12.dp))
                        Column(Modifier.weight(1f)) {
                            Text(str.autoServerTitle, fontWeight = FontWeight.Bold)
                            Text(str.autoServerDesc, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                        if (isAuto) Icon(Icons.Rounded.CheckCircle, null, tint = MaterialTheme.colorScheme.primary)
                    }
                }
            }

            if (subscriptions.isNotEmpty()) {
                item { Text(str.subscriptions, style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary) }
                items(subscriptions, key = { it.id }) { sub ->
                    Surface(shape = RoundedCornerShape(22.dp), color = MaterialTheme.colorScheme.surfaceContainer, contentColor = MaterialTheme.colorScheme.onSurface, modifier = Modifier.fillMaxWidth()) {
                        Row(modifier = Modifier.padding(14.dp), verticalAlignment = Alignment.CenterVertically) {
                            Column(Modifier.weight(1f)) {
                                Text(sub.name, fontWeight = FontWeight.Bold)
                                Text(sub.url, maxLines = 1, overflow = TextOverflow.Ellipsis, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                            }
                            IconButton(onClick = { onRefreshSub(sub) }) { Icon(Icons.Rounded.Refresh, null) }
                        }
                    }
                }
            }

            item { Text("${str.servers} (${profiles.size})", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary) }
            items(profiles, key = { it.id }) { p ->
                val selected = p.id == selectedId
                Surface(
                    onClick = { onSelect(p.id) },
                    shape = RoundedCornerShape(22.dp),
                    color = if (selected) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceContainer,
                    contentColor = if (selected) MaterialTheme.colorScheme.onPrimaryContainer else MaterialTheme.colorScheme.onSurface,
                    border = BorderStroke(1.dp, if (selected) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outlineVariant),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(modifier = Modifier.padding(10.dp), verticalAlignment = Alignment.CenterVertically) {
                        IconButton(onClick = { onTogglePriority(p.id) }) {
                            Icon(if (p.isPriority) Icons.Rounded.Star else Icons.Rounded.StarBorder, null, tint = if (p.isPriority) Color(0xFFFACC15) else MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                        Column(Modifier.weight(1f)) {
                            Text(p.name, fontWeight = FontWeight.Bold, maxLines = 1, overflow = TextOverflow.Ellipsis)
                            Text("${p.protocol.uppercase()} • ${p.address}:${p.port}", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                        }
                        p.pingMs?.let { ms ->
                            val c = if (ms < 100) Color(0xFF4ADE80) else if (ms < 220) Color(0xFFFACC15) else Color(0xFFF87171)
                            Text("${ms}ms", fontWeight = FontWeight.Bold, color = c, fontSize = 12.sp)
                            Spacer(Modifier.width(4.dp))
                        }
                        IconButton(onClick = { onDelete(p.id) }) { Icon(Icons.Rounded.DeleteOutline, null) }
                    }
                }
            }
        }
    }

    if (showAddSub) {
        AlertDialog(
            onDismissRequest = { showAddSub = false },
            title = { Text(str.addSub) },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedTextField(value = subName, onValueChange = { subName = it }, label = { Text(str.subName) })
                    OutlinedTextField(value = subUrl, onValueChange = { subUrl = it }, label = { Text(str.subUrl) })
                }
            },
            confirmButton = { Button(onClick = { onAddSub(subName, subUrl); subName = ""; subUrl = ""; showAddSub = false }) { Text(str.add) } },
            dismissButton = { TextButton(onClick = { showAddSub = false }) { Text(str.cancel) } }
        )
    }

    if (showAddKey) {
        AlertDialog(
            onDismissRequest = { showAddKey = false },
            title = { Text(str.addKey) },
            text = { OutlinedTextField(value = keyText, onValueChange = { keyText = it }, label = { Text("vless://, vmess://, trojan://, ss://...") }, minLines = 3) },
            confirmButton = { Button(onClick = { onImportRaw(keyText); keyText = ""; showAddKey = false }) { Text(str.importBtn) } },
            dismissButton = { TextButton(onClick = { showAddKey = false }) { Text(str.cancel) } }
        )
    }
}

@Composable
fun AppsRoutingScreen(
    str: UiStrings, settings: AppSettings, apps: List<InstalledAppInfo>,
    onToggleApp: (String) -> Unit, onClearAll: () -> Unit, onPolicyChange: (PerAppPolicy) -> Unit
) {
    var query by remember { mutableStateOf("") }
    var showSystem by remember { mutableStateOf(false) }
    var selectedOnly by remember { mutableStateOf(false) }

    val filtered = remember(apps, query, showSystem, selectedOnly, settings.selectedPackages) {
        apps.filter { app ->
            (showSystem || !app.isSystem) &&
            (!selectedOnly || app.packageName in settings.selectedPackages) &&
            (query.isBlank() || app.label.contains(query, ignoreCase = true) || app.packageName.contains(query, ignoreCase = true))
        }.sortedByDescending { it.packageName in settings.selectedPackages }
    }

    Column(modifier = Modifier.fillMaxSize().padding(horizontal = 16.dp, vertical = 6.dp)) {
        Text(str.appsRoutingTitle, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onBackground)
        Text(str.appsRoutingHint, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Spacer(Modifier.height(8.dp))

        SingleChoiceSegmentedButtonRow(modifier = Modifier.fillMaxWidth()) {
            SegmentedButton(selected = settings.perAppPolicy == PerAppPolicy.ONLY_SELECTED, onClick = { onPolicyChange(PerAppPolicy.ONLY_SELECTED) }, shape = SegmentedButtonDefaults.itemShape(0, 2)) { Text(str.onlySelectedApps, maxLines = 1, fontSize = 12.sp) }
            SegmentedButton(selected = settings.perAppPolicy == PerAppPolicy.EXCLUDE_SELECTED, onClick = { onPolicyChange(PerAppPolicy.EXCLUDE_SELECTED) }, shape = SegmentedButtonDefaults.itemShape(1, 2)) { Text(str.excludeSelectedApps, maxLines = 1, fontSize = 12.sp) }
        }

        Spacer(Modifier.height(8.dp))
        OutlinedTextField(
            value = query, onValueChange = { query = it },
            leadingIcon = { Icon(Icons.Rounded.Search, null) },
            placeholder = { Text(str.searchApps) },
            singleLine = true, shape = RoundedCornerShape(26.dp), modifier = Modifier.fillMaxWidth()
        )

        LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.padding(vertical = 8.dp)) {
            item { FilterChip(selected = showSystem, onClick = { showSystem = !showSystem }, label = { Text(str.showSystemApps) }) }
            item { FilterChip(selected = selectedOnly, onClick = { selectedOnly = !selectedOnly }, label = { Text("${str.selectedOnlyFilter} (${settings.selectedPackages.size})") }) }
            if (settings.selectedPackages.isNotEmpty()) item { AssistChip(onClick = onClearAll, label = { Text(str.clearSelection) }) }
        }

        LazyColumn(verticalArrangement = Arrangement.spacedBy(8.dp), contentPadding = PaddingValues(bottom = 16.dp)) {
            items(filtered, key = { it.packageName }) { app ->
                val checked = app.packageName in settings.selectedPackages
                Surface(
                    onClick = { onToggleApp(app.packageName) },
                    shape = RoundedCornerShape(22.dp),
                    color = if (checked) MaterialTheme.colorScheme.primaryContainer else MaterialTheme.colorScheme.surfaceContainer,
                    contentColor = if (checked) MaterialTheme.colorScheme.onPrimaryContainer else MaterialTheme.colorScheme.onSurface,
                    border = BorderStroke(1.dp, if (checked) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outlineVariant),
                    modifier = Modifier.fillMaxWidth()
                ) {
                    Row(modifier = Modifier.padding(horizontal = 12.dp, vertical = 10.dp), verticalAlignment = Alignment.CenterVertically) {
                        if (app.icon != null) {
                            Image(bitmap = app.icon.asImageBitmap(), contentDescription = app.label, modifier = Modifier.size(40.dp).clip(RoundedCornerShape(12.dp)))
                        } else {
                            Surface(shape = RoundedCornerShape(12.dp), color = MaterialTheme.colorScheme.surfaceContainerHigh, contentColor = MaterialTheme.colorScheme.onSurface, modifier = Modifier.size(40.dp)) {
                                Box(contentAlignment = Alignment.Center) { Icon(Icons.Rounded.Android, null) }
                            }
                        }
                        Spacer(Modifier.width(12.dp))
                        Column(Modifier.weight(1f)) {
                            Text(app.label, fontWeight = FontWeight.SemiBold, maxLines = 1, overflow = TextOverflow.Ellipsis)
                            Text(app.packageName, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant, maxLines = 1, overflow = TextOverflow.Ellipsis)
                        }
                        Checkbox(checked = checked, onCheckedChange = { onToggleApp(app.packageName) })
                    }
                }
            }
        }
    }
}

@Composable
fun SettingsScreen(str: UiStrings, settings: AppSettings, logs: List<String>, onUpdate: ((AppSettings) -> AppSettings) -> Unit) {
    LazyColumn(modifier = Modifier.fillMaxSize().padding(16.dp), verticalArrangement = Arrangement.spacedBy(14.dp)) {
        item {
            Text(str.language, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onBackground)
            Spacer(Modifier.height(8.dp))
            SingleChoiceSegmentedButtonRow(modifier = Modifier.fillMaxWidth()) {
                AppLanguage.entries.forEachIndexed { idx, lang ->
                    SegmentedButton(selected = settings.language == lang, onClick = { onUpdate { it.copy(language = lang) } }, shape = SegmentedButtonDefaults.itemShape(idx, AppLanguage.entries.size)) { Text(lang.nativeLabel) }
                }
            }
        }
        item {
            Text(str.appearance, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onBackground)
            Spacer(Modifier.height(8.dp))
            SingleChoiceSegmentedButtonRow(modifier = Modifier.fillMaxWidth()) {
                val labels = listOf(str.themeSystem, str.themeLight, str.themeDark)
                ThemeMode.entries.forEachIndexed { idx, mode ->
                    SegmentedButton(selected = settings.themeMode == mode, onClick = { onUpdate { it.copy(themeMode = mode) } }, shape = SegmentedButtonDefaults.itemShape(idx, ThemeMode.entries.size)) { Text(labels[idx]) }
                }
            }
            Spacer(Modifier.height(12.dp))
            Text(str.accentColor, style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.onBackground)
            Spacer(Modifier.height(8.dp))
            LazyRow(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                items(AccentShade.entries) { shade ->
                    val selected = settings.accentShade == shade
                    Box(
                        modifier = Modifier.size(46.dp).clip(CircleShape).background(Color(shade.seedHex))
                            .border(if (selected) 3.dp else 1.dp, if (selected) Color.White else Color.White.copy(0.25f), CircleShape)
                            .clickable { onUpdate { it.copy(accentShade = shade) } },
                        contentAlignment = Alignment.Center
                    ) { if (selected) Icon(Icons.Rounded.Check, null, tint = Color.White) }
                }
            }
        }
        item { SettingSwitchCard(str.auroraTitle, str.auroraDesc, settings.auroraEnabled) { v -> onUpdate { it.copy(auroraEnabled = v) } } }
        item { Text(str.coreAndNetwork, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onBackground) }
        item { SettingSwitchCard(str.fragmentTitle, str.fragmentDesc, settings.fragmentEnabled) { v -> onUpdate { it.copy(fragmentEnabled = v) } } }
        item { SettingSwitchCard(str.muxTitle, str.muxDesc, settings.muxEnabled) { v -> onUpdate { it.copy(muxEnabled = v) } } }
        item { SettingSwitchCard(str.sniffingTitle, str.sniffingDesc, settings.sniffingEnabled) { v -> onUpdate { it.copy(sniffingEnabled = v) } } }
        item { SettingSwitchCard(str.ipv6Title, str.ipv6Desc, settings.ipv6Enabled) { v -> onUpdate { it.copy(ipv6Enabled = v) } } }
        item {
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
                Text(str.logsTitle, style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onBackground)
                TextButton(onClick = { AlbinVpnService.clearLogs() }) { Text(str.clearLogs) }
            }
            Surface(shape = RoundedCornerShape(20.dp), color = MaterialTheme.colorScheme.surfaceContainer, contentColor = MaterialTheme.colorScheme.onSurface, modifier = Modifier.fillMaxWidth()) {
                Column(modifier = Modifier.padding(12.dp)) {
                    logs.takeLast(20).forEach { line -> Text(line, fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant) }
                }
            }
        }
    }
}

@Composable
private fun SettingSwitchCard(title: String, subtitle: String, checked: Boolean, onChange: (Boolean) -> Unit) {
    Surface(
        shape = RoundedCornerShape(24.dp),
        color = MaterialTheme.colorScheme.surfaceContainer,
        contentColor = MaterialTheme.colorScheme.onSurface,
        border = BorderStroke(1.dp, MaterialTheme.colorScheme.outlineVariant),
        modifier = Modifier.fillMaxWidth()
    ) {
        Row(modifier = Modifier.padding(16.dp).fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween, verticalAlignment = Alignment.CenterVertically) {
            Column(Modifier.weight(1f)) {
                Text(title, fontWeight = FontWeight.Bold, color = MaterialTheme.colorScheme.onSurface)
                Text(subtitle, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            Switch(checked = checked, onCheckedChange = onChange)
        }
    }
}
