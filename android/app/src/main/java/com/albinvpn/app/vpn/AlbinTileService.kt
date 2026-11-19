package com.albinvpn.app.vpn

import android.content.Intent
import android.net.VpnService
import android.os.Build
import android.service.quicksettings.Tile
import android.service.quicksettings.TileService
import com.albinvpn.app.MainActivity
import com.albinvpn.app.data.AUTO_PROFILE_ID
import com.albinvpn.app.data.ConnectionState
import com.albinvpn.app.data.ProfileRepository

class AlbinTileService : TileService() {

    override fun onStartListening() {
        super.onStartListening()
        syncTileState()
    }

    override fun onClick() {
        super.onClick()
        val state = AlbinVpnService.state.value
        if (state == ConnectionState.CONNECTED || state == ConnectionState.CONNECTING) {
            startService(Intent(this, AlbinVpnService::class.java).apply {
                action = AlbinVpnService.ACTION_STOP
            })
        } else {
            val prepareIntent = VpnService.prepare(this)
            if (prepareIntent != null) {
                val launch = Intent(this, MainActivity::class.java).apply {
                    addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                }
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.UPSIDE_DOWN_CAKE) {
                    val pi = android.app.PendingIntent.getActivity(
                        this, 0, launch,
                        android.app.PendingIntent.FLAG_IMMUTABLE or android.app.PendingIntent.FLAG_UPDATE_CURRENT
                    )
                    startActivityAndCollapse(pi)
                } else {
                    @Suppress("DEPRECATION")
                    startActivityAndCollapse(launch)
                }
            } else {
                val repo = ProfileRepository(this)
                val targetId = repo.loadSelectedProfileId() ?: AUTO_PROFILE_ID
                startForegroundService(Intent(this, AlbinVpnService::class.java).apply {
                    action = AlbinVpnService.ACTION_START
                    putExtra(AlbinVpnService.EXTRA_PROFILE_ID, targetId)
                })
            }
        }
        syncTileState()
    }

    private fun syncTileState() {
        val tile = qsTile ?: return
        val state = AlbinVpnService.state.value
        val stats = AlbinVpnService.stats.value
        tile.label = "Albin-vpn"
        tile.state = when (state) {
            ConnectionState.CONNECTED, ConnectionState.CONNECTING -> Tile.STATE_ACTIVE
            else -> Tile.STATE_INACTIVE
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            tile.subtitle = when (state) {
                ConnectionState.CONNECTED -> stats.activeServerName.ifBlank { "Protected" }
                ConnectionState.CONNECTING -> "Connecting..."
                else -> "Off"
            }
        }
        tile.updateTile()
    }
}
