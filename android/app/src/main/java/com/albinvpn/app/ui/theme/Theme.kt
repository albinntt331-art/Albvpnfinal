package com.albinvpn.app.ui.theme

import android.os.Build
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import com.albinvpn.app.data.AccentShade
import com.albinvpn.app.data.ThemeMode

private val DarkText = Color(0xFFF6F5FA)
private val DarkMuted = Color(0xFFBDC2D6)
private val LightText = Color(0xFF151822)
private val LightMuted = Color(0xFF4F566B)

private val PurpleDark = darkColorScheme(
    primary = Color(0xFFC084FC), onPrimary = Color.White,
    primaryContainer = Color(0xFF5B21B6), onPrimaryContainer = Color(0xFFF3E8FF),
    secondary = Color(0xFFA78BFA), onSecondary = Color.White,
    tertiary = Color(0xFFF472B6), onTertiary = Color.White,
    background = Color(0xFF090711), onBackground = DarkText,
    surface = Color(0xFF090711), onSurface = DarkText,
    surfaceVariant = Color(0xFF1B1530), onSurfaceVariant = DarkMuted,
    surfaceContainer = Color(0xFF151026), surfaceContainerHigh = Color(0xFF221A3C),
    outline = Color(0xFF5A4985), outlineVariant = Color(0xFF392D5C)
)
private val PurpleLight = lightColorScheme(
    primary = Color(0xFF7C3AED), onPrimary = Color.White,
    primaryContainer = Color(0xFFEDE9FE), onPrimaryContainer = Color(0xFF2E1065),
    tertiary = Color(0xFFEC4899), onTertiary = Color.White,
    background = Color(0xFFFAF7FF), onBackground = LightText,
    surface = Color(0xFFFAF7FF), onSurface = LightText,
    surfaceContainer = Color(0xFFF3ECFF), surfaceContainerHigh = Color(0xFFE9DDFC),
    outlineVariant = Color(0xFFD5C4F2)
)

private val UltraDark = darkColorScheme(
    primary = Color(0xFFD946EF), onPrimary = Color.White,
    primaryContainer = Color(0xFF86198F), onPrimaryContainer = Color(0xFFFAE8FF),
    tertiary = Color(0xFF38BDF8), onTertiary = Color.White,
    background = Color(0xFF0A0512), onBackground = DarkText,
    surface = Color(0xFF0A0512), onSurface = DarkText,
    surfaceVariant = Color(0xFF1E1033), onSurfaceVariant = DarkMuted,
    surfaceContainer = Color(0xFF170D28), surfaceContainerHigh = Color(0xFF271642),
    outlineVariant = Color(0xFF542885)
)
private val UltraLight = lightColorScheme(
    primary = Color(0xFFA21CAF), onPrimary = Color.White,
    primaryContainer = Color(0xFFFAE8FF), onPrimaryContainer = Color(0xFF4A044E),
    tertiary = Color(0xFF0284C7), onTertiary = Color.White,
    background = Color(0xFFFDF7FF), onBackground = LightText,
    surface = Color(0xFFFDF7FF), onSurface = LightText,
    surfaceContainer = Color(0xFFF7E9FE), surfaceContainerHigh = Color(0xFFEED4FC)
)

// PURE OCEAN / SKY BLUE — ZERO PURPLE OR VIOLET!
private val BlueDark = darkColorScheme(
    primary = Color(0xFF38BDF8), onPrimary = Color(0xFF04263B),
    primaryContainer = Color(0xFF0369A1), onPrimaryContainer = Color(0xFFE0F2FE),
    secondary = Color(0xFF0EA5E9), onSecondary = Color.White,
    tertiary = Color(0xFF22D3EE), onTertiary = Color(0xFF042F3B),
    background = Color(0xFF050D16), onBackground = DarkText,
    surface = Color(0xFF050D16), onSurface = DarkText,
    surfaceVariant = Color(0xFF0D2238), onSurfaceVariant = Color(0xFF9AC5E6),
    surfaceContainer = Color(0xFF0A192A), surfaceContainerHigh = Color(0xFF112842),
    outline = Color(0xFF275A85), outlineVariant = Color(0xFF1A3F5F)
)
private val BlueLight = lightColorScheme(
    primary = Color(0xFF0284C7), onPrimary = Color.White,
    primaryContainer = Color(0xFFE0F2FE), onPrimaryContainer = Color(0xFF082F49),
    tertiary = Color(0xFF06B6D4), onTertiary = Color.White,
    background = Color(0xFFF4FAFF), onBackground = LightText,
    surface = Color(0xFFF4FAFF), onSurface = LightText,
    surfaceContainer = Color(0xFFE6F4FE), surfaceContainerHigh = Color(0xFFD4ECFC),
    outlineVariant = Color(0xFFBAE0FA)
)

private val EmeraldDark = darkColorScheme(
    primary = Color(0xFF34D399), onPrimary = Color(0xFF022C22),
    primaryContainer = Color(0xFF047857), onPrimaryContainer = Color(0xFFD1FAE5),
    tertiary = Color(0xFF2DD4BF), onTertiary = Color(0xFF042F2E),
    background = Color(0xFF05120E), onBackground = DarkText,
    surface = Color(0xFF05120E), onSurface = DarkText,
    surfaceVariant = Color(0xFF0D2920), onSurfaceVariant = Color(0xFFA0D9C6),
    surfaceContainer = Color(0xFF0A1F18), surfaceContainerHigh = Color(0xFF113328),
    outlineVariant = Color(0xFF1D5744)
)
private val EmeraldLight = lightColorScheme(
    primary = Color(0xFF059669), onPrimary = Color.White,
    primaryContainer = Color(0xFFD1FAE5), onPrimaryContainer = Color(0xFF022C22),
    tertiary = Color(0xFF0D9488), onTertiary = Color.White,
    background = Color(0xFFF2FCF8), onBackground = LightText,
    surface = Color(0xFFF2FCF8), onSurface = LightText,
    surfaceContainer = Color(0xFFE3F7EF), surfaceContainerHigh = Color(0xFFD0F0E3)
)

private val RoseDark = darkColorScheme(
    primary = Color(0xFFF472B6), onPrimary = Color.White,
    primaryContainer = Color(0xFF9D174D), onPrimaryContainer = Color(0xFFFCE7F3),
    tertiary = Color(0xFFFB7185), onTertiary = Color.White,
    background = Color(0xFF14070D), onBackground = DarkText,
    surface = Color(0xFF14070D), onSurface = DarkText,
    surfaceVariant = Color(0xFF2B101D), onSurfaceVariant = Color(0xFFE6B5CA),
    surfaceContainer = Color(0xFF220C17), surfaceContainerHigh = Color(0xFF361425),
    outlineVariant = Color(0xFF5E2440)
)
private val RoseLight = lightColorScheme(
    primary = Color(0xFFDB2777), onPrimary = Color.White,
    primaryContainer = Color(0xFFFCE7F3), onPrimaryContainer = Color(0xFF500724),
    tertiary = Color(0xFFE11D48), onTertiary = Color.White,
    background = Color(0xFFFFF7FA), onBackground = LightText,
    surface = Color(0xFFFFF7FA), onSurface = LightText,
    surfaceContainer = Color(0xFFFCE9F1), surfaceContainerHigh = Color(0xFFF7D7E5)
)

private val AmberDark = darkColorScheme(
    primary = Color(0xFFFBBF24), onPrimary = Color(0xFF2E1202),
    primaryContainer = Color(0xFFB45309), onPrimaryContainer = Color(0xFFFEF3C7),
    tertiary = Color(0xFFFB923C), onTertiary = Color(0xFF2E1202),
    background = Color(0xFF120C05), onBackground = DarkText,
    surface = Color(0xFF120C05), onSurface = DarkText,
    surfaceVariant = Color(0xFF2B1C0C), onSurfaceVariant = Color(0xFFE3C8A8),
    surfaceContainer = Color(0xFF21160A), surfaceContainerHigh = Color(0xFF362411),
    outlineVariant = Color(0xFF5E401E)
)
private val AmberLight = lightColorScheme(
    primary = Color(0xFFD97706), onPrimary = Color.White,
    primaryContainer = Color(0xFFFEF3C7), onPrimaryContainer = Color(0xFF451A03),
    tertiary = Color(0xFFEA580C), onTertiary = Color.White,
    background = Color(0xFFFFFAF2), onBackground = LightText,
    surface = Color(0xFFFFFAF2), onSurface = LightText,
    surfaceContainer = Color(0xFFF9EEDF), surfaceContainerHigh = Color(0xFFF2DFC7)
)

@Composable
fun AlbinVpnTheme(
    themeMode: ThemeMode,
    accentShade: AccentShade,
    content: @Composable () -> Unit
) {
    val darkTheme = when (themeMode) {
        ThemeMode.SYSTEM -> isSystemInDarkTheme()
        ThemeMode.LIGHT -> false
        ThemeMode.DARK -> true
    }

    val context = LocalContext.current
    val colorScheme = if (accentShade == AccentShade.SYSTEM_DYNAMIC && Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        if (darkTheme) dynamicDarkColorScheme(context) else dynamicLightColorScheme(context)
    } else {
        when (accentShade) {
            AccentShade.PURPLE, AccentShade.SYSTEM_DYNAMIC -> if (darkTheme) PurpleDark else PurpleLight
            AccentShade.ULTRAVIOLET -> if (darkTheme) UltraDark else UltraLight
            AccentShade.OCEAN_BLUE -> if (darkTheme) BlueDark else BlueLight
            AccentShade.EMERALD -> if (darkTheme) EmeraldDark else EmeraldLight
            AccentShade.ROSE -> if (darkTheme) RoseDark else RoseLight
            AccentShade.AMBER -> if (darkTheme) AmberDark else AmberLight
        }
    }

    MaterialTheme(colorScheme = colorScheme, content = content)
}
