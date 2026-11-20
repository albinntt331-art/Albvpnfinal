"""Albin-vpn v6 Ultimate Desktop UI — Full Visual Parity with Android APK:
- Living Animated Aurora Nebula Background behind translucent frosted glass cards
- Glowing Gradient Mode Pill Switcher (Proxy Apps | TUN Strict)
- 4-Layer Circular Quantum Plasma Orb with 10 orbiting particles & 3 sonar waves
- Dual separate Download & Upload smooth Bézier sparkline cards + Dual-IP Chain
- Interactive circular Accent Color Swatches (6 palettes) + Per-Server Stats + UAC Admin TUN + System Tray
"""
import json
import math
import subprocess
import sys
import threading
import time
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, Signal, QObject, QPointF
from PySide6.QtGui import QAction, QColor, QConicalGradient, QFont, QIcon, QLinearGradient, QPainter, QPainterPath, QPen, QRadialGradient
from PySide6.QtWidgets import (
    QApplication, QCheckBox, QComboBox, QFileDialog, QFrame, QHBoxLayout, QInputDialog,
    QLabel, QLineEdit, QListWidget, QListWidgetItem, QMainWindow, QMenu, QMessageBox,
    QPlainTextEdit, QPushButton, QSizePolicy, QStackedWidget, QSystemTrayIcon, QVBoxLayout, QWidget,
)
from config_builder import build_singbox_config, build_xray_config, choose_core
from core_manager import (
    CoreProcessManager, fetch_ip_info, get_windows_net_bytes,
    is_windows_admin, measure_ping, relaunch_as_admin,
)
from theme import ACCENT_PALETTES, build_stylesheet, get_palette
from uri_parser import fetch_subscription, parse_batch

STATE_FILE = Path.home() / ".albinvpn_desktop.json"
AUTO_ID = "__AUTO_BEST__"


def fmt_rate(bps: int) -> str:
    if bps >= 1_000_000:
        return f"{bps / 1_000_000:.1f} MB/s"
    if bps >= 1_000:
        return f"{bps / 1_000:.0f} KB/s"
    return f"{bps} B/s"


def fmt_bytes(b: int) -> str:
    if b >= 1_000_000_000:
        return f"{b / 1_000_000_000:.2f} GB"
    if b >= 1_000_000:
        return f"{b / 1_000_000:.1f} MB"
    if b >= 1_000:
        return f"{b / 1_000:.0f} KB"
    return f"{b} B"


I18N = {
    "ru": {
        "nav": ["Главная", "Серверы", "Программы", "Статистика", "Журнал", "Настройки"],
        "mode_proxy": "Proxy Apps", "mode_tun": "TUN (Строгий)",
        "connect": "Подключить", "connected": "Защищено", "disconnected": "Отключено",
        "auto_title": "★ Авто (Лучший сервер)",
        "download": "Загрузка", "upload": "Отдача",
        "add_sub": "+ Подписка", "add_key": "+ Ключ", "ping": "Пинг всех", "prio": "★ Приоритет", "del": "Удалить",
        "apps_title": "Маршрутизация по программам (.exe)",
        "add_exe": "+ Добавить .exe", "scan_exe": "Сканировать запущенные",
        "stats_title": "Статистика трафика по серверам", "reset_stats": "Сбросить",
        "lang": "Язык интерфейса", "dark": "Тёмная тема", "aurora": "Живой фон Aurora (плазменное свечение)",
        "accent": "Оттенок системы (Фиолетовый по базе)",
        "check_ips": "Проверить оба IP", "elevate": "Перезапустить от Admin (для TUN)",
    },
    "en": {
        "nav": ["Home", "Servers", "Apps", "Stats", "Logs", "Settings"],
        "mode_proxy": "Proxy Apps", "mode_tun": "TUN (Strict)",
        "connect": "Connect", "connected": "Protected", "disconnected": "Disconnected",
        "auto_title": "★ Auto (Best Server)",
        "download": "Download", "upload": "Upload",
        "add_sub": "+ Subscription", "add_key": "+ Key", "ping": "Ping all", "prio": "★ Priority", "del": "Delete",
        "apps_title": "Per-Application Routing (.exe)",
        "add_exe": "+ Add .exe", "scan_exe": "Scan running apps",
        "stats_title": "Traffic Statistics by Server", "reset_stats": "Reset",
        "lang": "App Language", "dark": "Dark theme", "aurora": "Living Aurora Background (plasma glow)",
        "accent": "System accent (Purple default)",
        "check_ips": "Check Both IPs", "elevate": "Relaunch as Admin (for TUN)",
    },
}


class AuroraRootWidget(QWidget):
    """Living 3-cloud theme-matched Aurora Nebula canvas behind translucent frosted glass cards."""
    def __init__(self):
        super().__init__()
        self.pal = get_palette("purple", True)
        self.enabled_aurora = True
        self.boost = False
        self.phase = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._step)
        self._timer.start(45)

    def set_theme(self, pal: dict, enabled: bool) -> None:
        self.pal = pal; self.enabled_aurora = enabled; self.update()

    def set_boost(self, boost: bool) -> None:
        self.boost = boost; self.update()

    def _step(self) -> None:
        if self.enabled_aurora:
            self.phase = (self.phase + 0.022) % (2 * math.pi)
            self.update()

    def paintEvent(self, event) -> None:
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        p.fillRect(self.rect(), QColor(self.pal["bg"]))
        if not self.enabled_aurora:
            return
        w, h = self.width(), self.height()
        alpha = 115 if self.boost else 68
        clouds = [
            (QColor(self.pal["primary"]), w * (0.48 + 0.20 * math.cos(self.phase)), h * (0.30 + 0.14 * math.sin(self.phase)), max(w, h) * 0.55, alpha),
            (QColor(self.pal["tertiary"]), w * (0.62 - 0.22 * math.sin(self.phase * 0.75)), h * (0.72 + 0.12 * math.cos(self.phase * 0.75)), max(w, h) * 0.48, int(alpha * 0.78)),
            (QColor(self.pal["primary_container"]), w * (0.24 + 0.12 * math.sin(self.phase * 0.55)), h * (0.22 + 0.10 * math.cos(self.phase * 0.55)), max(w, h) * 0.42, int(alpha * 0.85)),
        ]
        p.setPen(Qt.NoPen)
        for col, cx, cy, rad, a in clouds:
            g = QRadialGradient(cx, cy, rad)
            c1 = QColor(col); c1.setAlpha(a)
            c2 = QColor(col); c2.setAlpha(0)
            g.setColorAt(0.0, c1); g.setColorAt(1.0, c2)
            p.setBrush(g)
            p.drawEllipse(QPointF(cx, cy), rad, rad)


class GlowingPowerButton(QWidget):
    """4-Layer Pure Circular Quantum Plasma Orb with 10 orbiting particles & 3 sonar ripples."""
    clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setMinimumSize(280, 280)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCursor(Qt.PointingHandCursor)
        self.connected = False
        self.phase = 0.0
        self.angle1 = 0.0
        self.angle2 = 360.0
        self.angle3 = 120.0
        self.ripple = 0.0
        self.label_connect = "Подключить"
        self.label_connected = "Защищено"
        self.pal = get_palette("purple", True)
        self._anim = QTimer(self); self._anim.timeout.connect(self._step); self._anim.start(26)

    def set_theme(self, pal: dict) -> None:
        self.pal = pal; self.update()

    def set_labels(self, connect_txt: str, connected_txt: str) -> None:
        self.label_connect = connect_txt; self.label_connected = connected_txt; self.update()

    def set_connected(self, state: bool) -> None:
        self.connected = state; self.update()

    def _step(self) -> None:
        self.phase = (self.phase + 0.07) % (2 * math.pi)
        self.angle1 = (self.angle1 + (3.0 if self.connected else 0.85)) % 360.0
        self.angle2 = (self.angle2 - (1.9 if self.connected else 0.50)) % 360.0
        self.angle3 = (self.angle3 + (1.1 if self.connected else 0.30)) % 360.0
        self.ripple = (self.ripple + 0.013) % 1.0
        self.update()

    def mousePressEvent(self, event) -> None:
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

    def paintEvent(self, event) -> None:
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        cx, cy = self.width() / 2.0, self.height() / 2.0
        unit = min(self.width(), self.height()) / 280.0
        prim = QColor(self.pal["primary"])
        tert = QColor(self.pal["tertiary"])
        glow = QColor(self.pal["glow"])

        # Ambient halo scaled proportionally to widget bounds
        aura_r = (122 + 6 * math.sin(self.phase)) * unit
        g = QRadialGradient(cx, cy, aura_r)
        c1 = QColor(glow); c1.setAlpha(150 if self.connected else 60)
        c2 = QColor(glow); c2.setAlpha(0)
        g.setColorAt(0.2, c1); g.setColorAt(1.0, c2)
        p.setBrush(g); p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, cy), aura_r, aura_r)

        # 3 staggered sonar waves
        if self.connected:
            for offset in (0.0, 0.33, 0.66):
                rp = (self.ripple + offset) % 1.0
                r = (76 + rp * 48) * unit
                rc = QColor(prim); rc.setAlpha(int((1.0 - rp) * 135))
                p.setBrush(Qt.NoBrush); p.setPen(QPen(rc, 2.5))
                p.drawEllipse(QPointF(cx, cy), r, r)

        # 3 counter-rotating orbital plasma rings
        for r_ring, ang, w, col in ((88 * unit, -self.angle1, 4.0, prim), (100 * unit, -self.angle2, 2.4, tert), (112 * unit, -self.angle3, 1.6, prim)):
            con = QConicalGradient(cx, cy, ang)
            cd = QColor(col); cd.setAlpha(18)
            con.setColorAt(0.0, col); con.setColorAt(0.5, cd); con.setColorAt(1.0, col)
            p.setBrush(Qt.NoBrush); p.setPen(QPen(con, w if self.connected else w * 0.65))
            p.drawEllipse(QPointF(cx, cy), r_ring, r_ring)

        # 10 orbiting glowing plasma particles
        for k in range(10):
            pr = (100 if k % 2 == 0 else 112) * unit
            rad = math.radians((self.angle1 if k % 2 == 0 else self.angle2) + k * 36)
            px, py = cx + pr * math.cos(rad), cy + pr * math.sin(rad)
            p.setBrush(prim if k % 2 == 0 else tert); p.setPen(Qt.NoPen)
            sz = (3.6 + (k % 2)) if self.connected else 2.4
            p.drawEllipse(QPointF(px, py), sz, sz)

        # Pure circular glowing core
        core_r = 74 * unit
        if self.connected:
            cg = QRadialGradient(cx - 20, cy - 20, core_r * 2.1)
            cg.setColorAt(0.0, tert); cg.setColorAt(0.55, prim); cg.setColorAt(1.0, QColor(self.pal["primary_container"]))
            p.setBrush(cg)
        else:
            cg = QRadialGradient(cx, cy, core_r)
            cg.setColorAt(0.0, QColor(self.pal["surface_solid"])); cg.setColorAt(1.0, QColor(self.pal["bg"]))
            p.setBrush(cg)
        p.setPen(QPen(prim, 2.4))
        p.drawEllipse(QPointF(cx, cy), core_r, core_r)

        # Proper Power Symbol (gap at 12 o'clock: start=130 deg, span=280 deg counter-clockwise)
        p.setPen(QPen(QColor("#FFFFFF"), 4.2 * unit, Qt.SolidLine, Qt.RoundCap))
        ic_r = 18 * unit
        ic_cy = cy - 12 * unit
        p.drawArc(int(cx - ic_r), int(ic_cy - ic_r), int(ic_r * 2), int(ic_r * 2), 130 * 16, 280 * 16)
        p.drawLine(int(cx), int(ic_cy - ic_r - 5 * unit), int(cx), int(ic_cy - 2 * unit))
        p.setFont(QFont("Segoe UI", max(10, int(12 * unit)), QFont.Bold))
        p.drawText(int(cx - 72 * unit), int(cy + 16 * unit), int(144 * unit), int(32 * unit), Qt.AlignCenter, self.label_connected if self.connected else self.label_connect)


class TrafficSparklineWidget(QWidget):
    def __init__(self, use_tertiary: bool = False):
        super().__init__()
        self.setMinimumHeight(76)
        self.use_tertiary = use_tertiary
        self.values = [0.2] * 26
        self.pal = get_palette("purple", True)

    def set_theme(self, pal: dict) -> None:
        self.pal = pal; self.update()

    def push_value(self, val: float) -> None:
        self.values = self.values[1:] + [max(0.1, val)]
        self.update()

    def paintEvent(self, event) -> None:
        p = QPainter(self); p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        max_v = max(max(self.values), 1.0)
        step_x = w / max(len(self.values) - 1, 1)
        line, area = QPainterPath(), QPainterPath()
        for i, v in enumerate(self.values):
            x = i * step_x; y = h - (v / max_v) * (h * 0.80) - 5
            if i == 0:
                line.moveTo(x, y); area.moveTo(x, h); area.lineTo(x, y)
            else:
                px = (i - 1) * step_x; py = h - (self.values[i - 1] / max_v) * (h * 0.80) - 5
                cx = (px + x) / 2
                line.cubicTo(cx, py, cx, y, x, y); area.cubicTo(cx, py, cx, y, x, y)
        area.lineTo(w, h); area.closeSubpath()
        accent = QColor(self.pal["tertiary"] if self.use_tertiary else self.pal["primary"])
        fg = QLinearGradient(0, 0, 0, h)
        c1 = QColor(accent); c1.setAlpha(125); c2 = QColor(accent); c2.setAlpha(0)
        fg.setColorAt(0.0, c1); fg.setColorAt(1.0, c2)
        p.fillPath(area, fg)
        p.setPen(QPen(accent, 2.8, Qt.SolidLine, Qt.RoundCap))
        p.drawPath(line)


class LogBridge(QObject):
    new_line = Signal(str)
    ping_done = Signal(str, object)
    live_ping = Signal(object)
    ips_done = Signal(str, str)


class AlbinVpnWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Albin-vpn — Google Pixel Edition")
        _base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        _ico = _base / "albin_icon.png"
        self.app_icon = QIcon(str(_ico)) if _ico.exists() else QIcon()
        if not self.app_icon.isNull():
            self.setWindowIcon(self.app_icon)
        self.resize(1120, 710)

        self.is_admin = is_windows_admin()
        self.data = self._load_state()
        self.connected = False
        self.active_profile = None
        self.connect_ts = 0.0
        self.last_rx, self.last_tx = get_windows_net_bytes()
        self.sess_rx, self.sess_tx, self.peak_rx = 0, 0, 0

        self.bridge = LogBridge()
        self.bridge.new_line.connect(self._append_log)
        self.bridge.ping_done.connect(self._on_ping_result)
        self.bridge.live_ping.connect(self._on_live_ping)
        self.bridge.ips_done.connect(self._on_ips_done)
        self.core_mgr = CoreProcessManager(lambda msg: self.bridge.new_line.emit(msg))

        self._build_ui()
        self._setup_tray()
        self._apply_theme()
        self._apply_language()
        self._refresh_lists()

        self.timer = QTimer(self); self.timer.timeout.connect(self._tick_timer); self.timer.start(1000)
        self.ping_timer = QTimer(self); self.ping_timer.timeout.connect(self._run_live_ping); self.ping_timer.start(3500)

    def _tr(self, key: str):
        return I18N.get(self.data["settings"].get("language", "ru"), I18N["ru"])[key]

    def _load_state(self) -> dict:
        default = {
            "settings": {
                "language": "ru", "dark": True, "accent": "purple", "aurora": True,
                "vpn_mode": "proxy_apps", "per_app_policy": "only_selected",
                "selected_apps": ["chrome.exe", "Telegram.exe", "Discord.exe"],
                "sniffing": True, "fragment": False, "mux": False, "ipv6": False, "remote_dns": "1.1.1.1",
            },
            "profiles": [], "server_stats": {}, "selected_id": AUTO_ID,
        }
        if STATE_FILE.exists():
            try:
                loaded = json.loads(STATE_FILE.read_text(encoding="utf-8"))
                default["settings"].update(loaded.get("settings", {}))
                default["profiles"] = loaded.get("profiles", [])
                default["server_stats"] = loaded.get("server_stats", {})
                default["selected_id"] = loaded.get("selected_id", AUTO_ID)
            except Exception:
                pass
        return default

    def _save_state(self) -> None:
        try:
            STATE_FILE.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")
        except Exception:
            pass

    def _setup_tray(self) -> None:
        if not QSystemTrayIcon.isSystemTrayAvailable():
            return
        self.tray = QSystemTrayIcon(self.app_icon, self)
        menu = QMenu()
        a_show = QAction("Open Albin-vpn", self); a_show.triggered.connect(self.showNormal)
        a_tog = QAction("Connect / Disconnect", self); a_tog.triggered.connect(self._toggle_vpn)
        a_quit = QAction("Exit", self); a_quit.triggered.connect(self._force_quit)
        menu.addAction(a_show); menu.addAction(a_tog); menu.addSeparator(); menu.addAction(a_quit)
        self.tray.setContextMenu(menu); self.tray.show()

    def _force_quit(self) -> None:
        self.core_mgr.stop(); QApplication.quit()

    def _apply_theme(self) -> None:
        s = self.data["settings"]
        acc, dark, aurora = s.get("accent", "purple"), s.get("dark", True), s.get("aurora", True)
        self.setStyleSheet(build_stylesheet(acc, dark))
        pal = get_palette(acc, dark)
        self.aurora_root.set_theme(pal, aurora)
        self.power_orb.set_theme(pal)
        self.dl_spark.set_theme(pal); self.ul_spark.set_theme(pal)
        self.dl_val_lbl.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {pal['primary']};")
        self.ul_val_lbl.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {pal['tertiary']};")
        self.exit_ip_lbl.setStyleSheet(f"font-weight: 700; color: {pal['primary']};")
        for k, btn in self.swatch_buttons.items():
            sel = (k == acc)
            sw = ACCENT_PALETTES[k]["swatch"]
            btn.setText("✓" if sel else "")
            btn.setStyleSheet(
                f"background-color: {sw}; color: #FFFFFF; font-weight: 800; font-size: 16px; "
                f"border-radius: 22px; border: {'3px solid #FFFFFF' if sel else '1px solid rgba(255,255,255,60)'};"
            )

    def _apply_language(self) -> None:
        for b, txt in zip(self.nav_buttons, self._tr("nav")):
            b.setText(txt)
        self.btn_mode_proxy.setText(self._tr("mode_proxy"))
        self.btn_mode_tun.setText(self._tr("mode_tun"))
        self.power_orb.set_labels(self._tr("connect"), self._tr("connected"))
        if not self.connected:
            self.status_lbl.setText(self._tr("disconnected"))
        self.dl_title_lbl.setText(self._tr("download")); self.ul_title_lbl.setText(self._tr("upload"))
        self.ip_btn.setText(self._tr("check_ips"))
        if hasattr(self, "elevate_btn"):
            self.elevate_btn.setText(self._tr("elevate"))
        self.btn_sub.setText(self._tr("add_sub")); self.btn_key.setText(self._tr("add_key"))
        self.btn_ping.setText(self._tr("ping")); self.btn_prio.setText(self._tr("prio")); self.btn_del.setText(self._tr("del"))
        self.apps_title_lbl.setText(self._tr("apps_title"))
        self.btn_add_exe.setText(self._tr("add_exe")); self.btn_scan_exe.setText(self._tr("scan_exe"))
        self.stats_title_lbl.setText(self._tr("stats_title")); self.btn_reset_stats.setText(self._tr("reset_stats"))
        self.dark_cb.setText(self._tr("dark")); self.aurora_cb.setText(self._tr("aurora"))
        self.lang_lbl.setText(self._tr("lang")); self.accent_lbl.setText(self._tr("accent"))
        self._refresh_lists()

    def _build_ui(self) -> None:
        self.aurora_root = AuroraRootWidget()
        self.setCentralWidget(self.aurora_root)
        main_layout = QHBoxLayout(self.aurora_root); main_layout.setContentsMargins(0, 0, 0, 0); main_layout.setSpacing(0)

        nav = QFrame(); nav.setObjectName("NavRail"); nav.setFixedWidth(220)
        nav_l = QVBoxLayout(nav); nav_l.setContentsMargins(16, 24, 16, 24); nav_l.setSpacing(8)
        brand = QLabel("Albin-vpn"); brand.setStyleSheet("font-size: 23px; font-weight: 800; padding-left: 8px;")
        nav_l.addWidget(brand)
        adm = "Admin • Full TUN Ready" if self.is_admin else "Standard Mode"
        sub = QLabel(adm); sub.setProperty("class", "Muted"); sub.setStyleSheet("font-size: 11px; padding-left: 8px; margin-bottom: 14px;")
        nav_l.addWidget(sub)

        self.nav_buttons = []
        for idx in range(6):
            btn = QPushButton(""); btn.setProperty("class", "NavBtn"); btn.setProperty("active", idx == 0)
            btn.clicked.connect(lambda _, i=idx: self._switch_page(i))
            nav_l.addWidget(btn); self.nav_buttons.append(btn)
        nav_l.addStretch()

        if not self.is_admin and sys.platform == "win32":
            self.elevate_btn = QPushButton("Admin TUN"); self.elevate_btn.setProperty("class", "PrimaryBtn")
            self.elevate_btn.clicked.connect(self._relaunch_admin)
            nav_l.addWidget(self.elevate_btn)

        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_home_page())
        self.stack.addWidget(self._build_profiles_page())
        self.stack.addWidget(self._build_apps_page())
        self.stack.addWidget(self._build_stats_page())
        self.stack.addWidget(self._build_logs_page())
        self.stack.addWidget(self._build_settings_page())
        main_layout.addWidget(nav); main_layout.addWidget(self.stack, 1)

    def _relaunch_admin(self) -> None:
        if relaunch_as_admin():
            self._force_quit()

    def _switch_page(self, idx: int) -> None:
        self.stack.setCurrentIndex(idx)
        for i, b in enumerate(self.nav_buttons):
            b.setProperty("active", i == idx); b.style().unpolish(b); b.style().polish(b)
        if idx == 3:
            self._refresh_stats()

    def _set_vpn_mode(self, mode: str) -> None:
        prev = self.data["settings"].get("vpn_mode", "proxy_apps")
        self._set_setting("vpn_mode", mode)
        self.btn_mode_proxy.setProperty("active", mode == "proxy_apps")
        self.btn_mode_tun.setProperty("active", mode == "tun")
        for b in (self.btn_mode_proxy, self.btn_mode_tun):
            b.style().unpolish(b); b.style().polish(b)
        if self.connected and mode != prev:
            self._append_log(f"[Mode] Переключение режима на {mode} — перезапуск туннеля...")
            self._toggle_vpn()
            QTimer.singleShot(350, self._toggle_vpn)

    def _build_home_page(self) -> QWidget:
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(28, 22, 28, 22); l.setSpacing(16)

        # Top Bar: Glowing Gradient Mode Pill + Live Ping + Dual IP Check button
        top = QHBoxLayout()
        pill = QFrame(); pill.setObjectName("ModePill")
        pl = QHBoxLayout(pill); pl.setContentsMargins(4, 4, 4, 4); pl.setSpacing(4)
        cur_mode = self.data["settings"].get("vpn_mode", "proxy_apps")
        self.btn_mode_proxy = QPushButton("Proxy Apps"); self.btn_mode_proxy.setProperty("class", "ModeTab")
        self.btn_mode_proxy.setProperty("active", cur_mode == "proxy_apps")
        self.btn_mode_proxy.clicked.connect(lambda: self._set_vpn_mode("proxy_apps"))
        self.btn_mode_tun = QPushButton("TUN (Strict)"); self.btn_mode_tun.setProperty("class", "ModeTab")
        self.btn_mode_tun.setProperty("active", cur_mode == "tun")
        self.btn_mode_tun.clicked.connect(lambda: self._set_vpn_mode("tun"))
        pl.addWidget(self.btn_mode_proxy); pl.addWidget(self.btn_mode_tun)

        self.live_ping_lbl = QLabel("● Ping: —"); self.live_ping_lbl.setStyleSheet("font-weight: 700; padding: 6px 12px;")
        self.ip_btn = QPushButton("Check Both IPs"); self.ip_btn.setProperty("class", "TonalBtn"); self.ip_btn.clicked.connect(self._check_both_ips)
        top.addWidget(pill); top.addStretch(); top.addWidget(self.live_ping_lbl); top.addWidget(self.ip_btn)
        l.addLayout(top)

        # Main 2-column Google Pixel Dashboard
        mid = QHBoxLayout(); mid.setSpacing(20)
        hero = QFrame(); hero.setProperty("class", "Card")
        hl = QVBoxLayout(hero); hl.setAlignment(Qt.AlignCenter); hl.setContentsMargins(20, 22, 20, 22); hl.setSpacing(8)
        self.power_orb = GlowingPowerButton(); self.power_orb.clicked.connect(self._toggle_vpn)
        hl.addWidget(self.power_orb, 1)
        self.status_lbl = QLabel(""); self.status_lbl.setStyleSheet("font-size: 17px; font-weight: 800;")
        hl.addWidget(self.status_lbl, alignment=Qt.AlignCenter)
        self.active_srv_lbl = QLabel(""); self.active_srv_lbl.setProperty("class", "Muted")
        hl.addWidget(self.active_srv_lbl, alignment=Qt.AlignCenter)
        mid.addWidget(hero, 1)

        right = QVBoxLayout(); right.setSpacing(14)

        # Dual-IP Chain Card
        ip_card = QFrame(); ip_card.setProperty("class", "Card")
        il = QVBoxLayout(ip_card); il.setContentsMargins(18, 14, 18, 14); il.setSpacing(6)
        ip_row = QHBoxLayout()
        self.direct_ip_lbl = QLabel("ISP: —"); self.direct_ip_lbl.setStyleSheet("font-weight: 600;")
        arrow = QLabel("━━▶"); arrow.setAlignment(Qt.AlignCenter)
        self.exit_ip_lbl = QLabel("VPN: —")
        ip_row.addWidget(self.direct_ip_lbl, 1); ip_row.addWidget(arrow); ip_row.addWidget(self.exit_ip_lbl, 1)
        il.addLayout(ip_row)
        self.session_tot_lbl = QLabel("Session: ↓ 0 B  •  ↑ 0 B  •  Peak: 0 B/s")
        self.session_tot_lbl.setProperty("class", "Muted")
        il.addWidget(self.session_tot_lbl)
        right.addWidget(ip_card)

        # Horizontal Download & Upload Sparkline Cards stacked one above the other
        speed_col = QVBoxLayout(); speed_col.setSpacing(12)

        dl_card = QFrame(); dl_card.setProperty("class", "Card")
        dll = QVBoxLayout(dl_card); dll.setContentsMargins(18, 12, 18, 12); dll.setSpacing(6)
        dl_hdr = QHBoxLayout()
        self.dl_title_lbl = QLabel("Download"); self.dl_title_lbl.setProperty("class", "Muted")
        self.dl_val_lbl = QLabel("0 B/s")
        dl_hdr.addWidget(self.dl_title_lbl); dl_hdr.addStretch(); dl_hdr.addWidget(self.dl_val_lbl)
        self.dl_spark = TrafficSparklineWidget(use_tertiary=False)
        dll.addLayout(dl_hdr); dll.addWidget(self.dl_spark, 1)

        ul_card = QFrame(); ul_card.setProperty("class", "Card")
        ull = QVBoxLayout(ul_card); ull.setContentsMargins(18, 12, 18, 12); ull.setSpacing(6)
        ul_hdr = QHBoxLayout()
        self.ul_title_lbl = QLabel("Upload"); self.ul_title_lbl.setProperty("class", "Muted")
        self.ul_val_lbl = QLabel("0 B/s")
        ul_hdr.addWidget(self.ul_title_lbl); ul_hdr.addStretch(); ul_hdr.addWidget(self.ul_val_lbl)
        self.ul_spark = TrafficSparklineWidget(use_tertiary=True)
        ull.addLayout(ul_hdr); ull.addWidget(self.ul_spark, 1)

        speed_col.addWidget(dl_card, 1); speed_col.addWidget(ul_card, 1)
        right.addLayout(speed_col, 1)

        mid.addLayout(right, 1)
        l.addLayout(mid, 1)
        return page

    def _build_profiles_page(self) -> QWidget:
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(24, 24, 24, 24); l.setSpacing(12)
        btns = QHBoxLayout()
        self.btn_sub = QPushButton(); self.btn_sub.setProperty("class", "PrimaryBtn"); self.btn_sub.clicked.connect(self._add_subscription)
        self.btn_key = QPushButton(); self.btn_key.setProperty("class", "TonalBtn"); self.btn_key.clicked.connect(self._add_key)
        self.btn_ping = QPushButton(); self.btn_ping.setProperty("class", "TonalBtn"); self.btn_ping.clicked.connect(self._ping_all)
        self.btn_prio = QPushButton(); self.btn_prio.setProperty("class", "TonalBtn"); self.btn_prio.clicked.connect(self._toggle_priority)
        self.btn_del = QPushButton(); self.btn_del.setProperty("class", "TonalBtn"); self.btn_del.clicked.connect(self._delete_selected_profile)
        for b in (self.btn_sub, self.btn_key, self.btn_ping, self.btn_prio, self.btn_del):
            btns.addWidget(b)
        btns.addStretch(); l.addLayout(btns)
        self.profiles_list = QListWidget(); self.profiles_list.currentRowChanged.connect(self._on_profile_selected)
        l.addWidget(self.profiles_list, 1)
        return page

    def _build_apps_page(self) -> QWidget:
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(24, 24, 24, 24); l.setSpacing(12)
        self.apps_title_lbl = QLabel(""); self.apps_title_lbl.setStyleSheet("font-size: 16px; font-weight: 700;")
        l.addWidget(self.apps_title_lbl)

        self.policy_combo = QComboBox()
        self.policy_combo.addItems(["Только выбранные в VPN (остальные напрямую)", "Исключить выбранные (остальные в VPN)"])
        self.policy_combo.setCurrentIndex(0 if self.data["settings"].get("per_app_policy") == "only_selected" else 1)
        self.policy_combo.currentIndexChanged.connect(lambda i: self._set_setting("per_app_policy", "only_selected" if i == 0 else "exclude_selected"))
        l.addWidget(self.policy_combo)

        row = QHBoxLayout()
        self.app_search = QLineEdit(); self.app_search.setPlaceholderText("Поиск или ввод имени .exe (например chrome.exe)...")
        self.app_search.textChanged.connect(lambda _: self._populate_apps_list())
        self.btn_add_exe = QPushButton("+ .exe"); self.btn_add_exe.setProperty("class", "PrimaryBtn"); self.btn_add_exe.clicked.connect(self._add_app_exe)
        self.btn_scan_exe = QPushButton("Обновить запущенные"); self.btn_scan_exe.setProperty("class", "TonalBtn"); self.btn_scan_exe.clicked.connect(self._scan_running_apps)
        btn_browse = QPushButton("Обзор..."); btn_browse.setProperty("class", "TonalBtn"); btn_browse.clicked.connect(self._browse_exe)
        btn_clear = QPushButton("Сбросить"); btn_clear.setProperty("class", "TonalBtn"); btn_clear.clicked.connect(self._clear_selected_apps)
        row.addWidget(self.app_search, 1); row.addWidget(self.btn_add_exe); row.addWidget(self.btn_scan_exe); row.addWidget(btn_browse); row.addWidget(btn_clear)
        l.addLayout(row)

        self.apps_count_lbl = QLabel("Выбрано программ: 0"); self.apps_count_lbl.setProperty("class", "Muted")
        l.addWidget(self.apps_count_lbl)

        self.discovered_apps = {
            "chrome.exe", "msedge.exe", "firefox.exe", "opera.exe", "brave.exe",
            "yandex.exe", "vivaldi.exe", "Telegram.exe", "Discord.exe", "Spotify.exe",
            "steam.exe", "Code.exe", "Obsidian.exe", "WhatsApp.exe",
        }
        self.apps_list = QListWidget()
        self.apps_list.itemChanged.connect(self._on_app_checkbox_changed)
        l.addWidget(self.apps_list, 1)
        self._scan_running_apps(silent=True)
        return page

    def _build_stats_page(self) -> QWidget:
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(24, 24, 24, 24); l.setSpacing(12)
        top = QHBoxLayout()
        self.stats_title_lbl = QLabel(""); self.stats_title_lbl.setStyleSheet("font-size: 16px; font-weight: 700;")
        self.btn_reset_stats = QPushButton("Reset"); self.btn_reset_stats.setProperty("class", "TonalBtn"); self.btn_reset_stats.clicked.connect(self._reset_stats)
        top.addWidget(self.stats_title_lbl); top.addStretch(); top.addWidget(self.btn_reset_stats)
        l.addLayout(top)
        self.stats_list = QListWidget(); l.addWidget(self.stats_list, 1)
        return page

    def _build_logs_page(self) -> QWidget:
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(24, 24, 24, 24)
        self.log_box = QPlainTextEdit(); self.log_box.setReadOnly(True); self.log_box.setPlainText("Albin-vpn v6 Ultimate ready.\n")
        l.addWidget(self.log_box)
        return page

    def _build_settings_page(self) -> QWidget:
        page = QWidget(); l = QVBoxLayout(page); l.setContentsMargins(24, 24, 24, 24); l.setSpacing(14)
        card = QFrame(); card.setProperty("class", "Card"); cl = QVBoxLayout(card); cl.setContentsMargins(20, 18, 20, 18); cl.setSpacing(12)
        lang_row = QHBoxLayout(); self.lang_lbl = QLabel(""); lang_row.addWidget(self.lang_lbl)
        self.lang_combo = QComboBox(); self.lang_combo.addItems(["Русский", "English"])
        self.lang_combo.setCurrentIndex(0 if self.data["settings"].get("language", "ru") == "ru" else 1)
        self.lang_combo.currentIndexChanged.connect(self._on_lang_changed)
        lang_row.addWidget(self.lang_combo); lang_row.addStretch(); cl.addLayout(lang_row)

        self.dark_cb = QCheckBox(""); self.dark_cb.setChecked(self.data["settings"].get("dark", True)); self.dark_cb.toggled.connect(self._on_theme_toggle)
        self.aurora_cb = QCheckBox(""); self.aurora_cb.setChecked(self.data["settings"].get("aurora", True)); self.aurora_cb.toggled.connect(self._on_aurora_toggle)
        cl.addWidget(self.dark_cb); cl.addWidget(self.aurora_cb)

        self.accent_lbl = QLabel(""); cl.addWidget(self.accent_lbl)
        sw_row = QHBoxLayout(); sw_row.setSpacing(12)
        self.swatch_buttons = {}
        for key in ACCENT_PALETTES.keys():
            b = QPushButton("")
            b.setFixedSize(44, 44)
            b.setCursor(Qt.PointingHandCursor)
            b.setToolTip(ACCENT_PALETTES[key]["name"])
            b.clicked.connect(lambda _, k=key: self._on_accent_clicked(k))
            sw_row.addWidget(b)
            self.swatch_buttons[key] = b
        sw_row.addStretch()
        cl.addLayout(sw_row)
        l.addWidget(card)

        net = QFrame(); net.setProperty("class", "Card"); nl = QVBoxLayout(net); nl.setContentsMargins(20, 18, 20, 18); nl.setSpacing(8)
        for key, lbl in [("fragment", "TLS Fragment (DPI bypass)"), ("mux", "Multiplexing (Mux)"), ("sniffing", "Traffic Sniffing"), ("ipv6", "IPv6 Tunnel")]:
            cb = QCheckBox(lbl); cb.setChecked(self.data["settings"].get(key, False))
            cb.toggled.connect(lambda v, k=key: self._set_setting(k, v)); nl.addWidget(cb)
        l.addWidget(net); l.addStretch()
        return page

    def _set_setting(self, key: str, value) -> None:
        self.data["settings"][key] = value; self._save_state()

    def _on_lang_changed(self, idx: int) -> None:
        self._set_setting("language", "ru" if idx == 0 else "en"); self._apply_language()

    def _on_theme_toggle(self, dark: bool) -> None:
        self._set_setting("dark", dark); self._apply_theme()

    def _on_aurora_toggle(self, enabled: bool) -> None:
        self._set_setting("aurora", enabled); self._apply_theme()

    def _on_accent_clicked(self, key: str) -> None:
        self._set_setting("accent", key); self._apply_theme()

    def _refresh_stats(self) -> None:
        self.stats_list.clear()
        for key, rec in self.data.get("server_stats", {}).items():
            sec = rec.get("sec", 0)
            h, m, s = sec // 3600, (sec % 3600) // 60, sec % 60
            self.stats_list.addItem(
                f"{rec.get('name', key)} ({rec.get('proto', '').upper()})  •  ↓ {fmt_bytes(rec.get('rx', 0))}  ↑ {fmt_bytes(rec.get('tx', 0))}  •  ⏱ {h:02d}:{m:02d}:{s:02d}"
            )

    def _reset_stats(self) -> None:
        self.data["server_stats"] = {}; self._save_state(); self._refresh_stats()

    def _refresh_lists(self) -> None:
        self.profiles_list.blockSignals(True); self.profiles_list.clear()
        self.profiles_list.addItem(QListWidgetItem(self._tr("auto_title")))
        sel_id = self.data.get("selected_id", AUTO_ID); sel_row = 0
        for i, p in enumerate(self.data["profiles"], start=1):
            star = "★ " if p.get("is_priority") else ""
            ping = f"  [{p['ping_ms']} ms]" if p.get("ping_ms") is not None else ""
            self.profiles_list.addItem(QListWidgetItem(f"{star}{p['name']} • {p['protocol'].upper()} ({p['address']}:{p['port']}){ping}"))
            if p["id"] == sel_id:
                sel_row = i
        self.profiles_list.setCurrentRow(sel_row); self.profiles_list.blockSignals(False)
        if sel_row == 0:
            self.active_srv_lbl.setText(self._tr("auto_title"))
        else:
            p = self.data["profiles"][sel_row - 1]; self.active_srv_lbl.setText(f"{p['name']} • {p['protocol'].upper()}")
        self._populate_apps_list()
        self._refresh_stats()

    def _on_profile_selected(self, row: int) -> None:
        if row == 0:
            self.data["selected_id"] = AUTO_ID; self.active_srv_lbl.setText(self._tr("auto_title"))
        elif 1 <= row <= len(self.data["profiles"]):
            p = self.data["profiles"][row - 1]; self.data["selected_id"] = p["id"]; self.active_srv_lbl.setText(f"{p['name']} • {p['protocol'].upper()}")
        self._save_state()

    def _toggle_priority(self) -> None:
        row = self.profiles_list.currentRow()
        if 1 <= row <= len(self.data["profiles"]):
            p = self.data["profiles"][row - 1]; p["is_priority"] = not p.get("is_priority", False)
            self._save_state(); self._refresh_lists()

    def _populate_apps_list(self) -> None:
        selected = set(self.data["settings"].get("selected_apps", []))
        all_apps = sorted(self.discovered_apps | selected, key=lambda x: (x not in selected, x.lower()))
        q = self.app_search.text().strip().lower() if hasattr(self, "app_search") else ""
        self.apps_list.blockSignals(True)
        self.apps_list.clear()
        for exe in all_apps:
            if q and q not in exe.lower():
                continue
            item = QListWidgetItem(exe)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            item.setCheckState(Qt.Checked if exe in selected else Qt.Unchecked)
            self.apps_list.addItem(item)
        self.apps_list.blockSignals(False)
        if hasattr(self, "apps_count_lbl"):
            self.apps_count_lbl.setText(f"Выбрано программ: {len(selected)}  (всего в списке: {len(all_apps)})")

    def _on_app_checkbox_changed(self, item: QListWidgetItem) -> None:
        exe = item.text().strip()
        apps = set(self.data["settings"].get("selected_apps", []))
        if item.checkState() == Qt.Checked:
            apps.add(exe)
        else:
            apps.discard(exe)
        self.data["settings"]["selected_apps"] = sorted(apps)
        self._save_state()
        self.apps_count_lbl.setText(f"Выбрано программ: {len(apps)}  (всего в списке: {len(self.discovered_apps | apps)})")

    def _scan_running_apps(self, silent: bool = False) -> None:
        try:
            flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
            out = subprocess.check_output(["tasklist", "/FO", "CSV", "/NH"], text=True, errors="ignore", creationflags=flags)
            exes = {line.split(",")[0].strip('"') for line in out.splitlines() if ".exe" in line.lower()}
            skip = {"svchost.exe", "csrss.exe", "wininit.exe", "services.exe", "lsass.exe", "smss.exe", "System Idle Process"}
            self.discovered_apps.update(e for e in exes if e not in skip)
            self._populate_apps_list()
        except Exception as exc:
            if not silent:
                QMessageBox.warning(self, "Scan", str(exc))

    def _add_app_exe(self) -> None:
        name = self.app_search.text().strip()
        if name:
            if not name.lower().endswith(".exe"):
                name += ".exe"
            self.discovered_apps.add(name)
            apps = set(self.data["settings"].get("selected_apps", []))
            apps.add(name)
            self.data["settings"]["selected_apps"] = sorted(apps)
            self.app_search.clear(); self._save_state(); self._populate_apps_list()

    def _browse_exe(self) -> None:
        fpath, _ = QFileDialog.getOpenFileName(self, "Select .exe", "", "Executables (*.exe)")
        if fpath:
            name = Path(fpath).name
            self.discovered_apps.add(name)
            apps = set(self.data["settings"].get("selected_apps", []))
            apps.add(name)
            self.data["settings"]["selected_apps"] = sorted(apps)
            self._save_state(); self._populate_apps_list()

    def _clear_selected_apps(self) -> None:
        self.data["settings"]["selected_apps"] = []
        self._save_state(); self._populate_apps_list()

    def _add_subscription(self) -> None:
        url, ok = QInputDialog.getText(self, self._tr("add_sub"), "URL (https://...):")
        if not ok or not url.strip():
            return
        try:
            profiles, _ = fetch_subscription(url.strip(), sub_id=url.strip())
            self.data["profiles"].extend(profiles); self._save_state(); self._refresh_lists()
        except Exception as exc:
            QMessageBox.warning(self, "Error", str(exc))

    def _add_key(self) -> None:
        clip = QApplication.clipboard().text()
        text, ok = QInputDialog.getMultiLineText(self, self._tr("add_key"), "vless://, vmess://, trojan://, ss://, hy2://:", clip)
        if ok and text.strip():
            parsed = parse_batch(text)
            if parsed:
                self.data["profiles"].extend(parsed); self._save_state(); self._refresh_lists()

    def _delete_selected_profile(self) -> None:
        row = self.profiles_list.currentRow()
        if 1 <= row <= len(self.data["profiles"]):
            self.data["profiles"].pop(row - 1); self.data["selected_id"] = AUTO_ID
            self._save_state(); self._refresh_lists()

    def _ping_all(self) -> None:
        def worker():
            for p in list(self.data["profiles"]):
                self.bridge.ping_done.emit(p["id"], measure_ping(p["address"], p["port"]))
        threading.Thread(target=worker, daemon=True).start()

    def _on_ping_result(self, pid: str, ms) -> None:
        for p in self.data["profiles"]:
            if p["id"] == pid:
                p["ping_ms"] = ms
        self._save_state(); self._refresh_lists()

    def _run_live_ping(self) -> None:
        if not self.connected or not self.active_profile:
            return
        prof = self.active_profile
        def worker():
            self.bridge.live_ping.emit(measure_ping(prof["address"], prof["port"], timeout=2.0))
        threading.Thread(target=worker, daemon=True).start()

    def _on_live_ping(self, ms) -> None:
        if ms is None:
            self.live_ping_lbl.setText("● Ping: timeout"); self.live_ping_lbl.setStyleSheet("color: #F87171; font-weight: 700; padding: 6px 12px;")
        else:
            col = "#4ADE80" if ms < 100 else ("#FACC15" if ms < 220 else "#F87171")
            self.live_ping_lbl.setText(f"● Ping: {ms} ms"); self.live_ping_lbl.setStyleSheet(f"color: {col}; font-weight: 700; padding: 6px 12px;")

    def _check_both_ips(self) -> None:
        self.direct_ip_lbl.setText("ISP: ...")
        self.exit_ip_lbl.setText("VPN: ..." if self.connected else "VPN: —")
        connected = self.connected
        def worker():
            direct = fetch_ip_info(via_local_proxy=False)
            vpn_exit = fetch_ip_info(via_local_proxy=True) if connected else "—"
            self.bridge.ips_done.emit(direct, vpn_exit)
        threading.Thread(target=worker, daemon=True).start()

    def _on_ips_done(self, direct: str, vpn_exit: str) -> None:
        self.direct_ip_lbl.setText(f"ISP: {direct}")
        self.exit_ip_lbl.setText(f"VPN: {vpn_exit}")

    def _pick_auto_best(self) -> dict | None:
        profs = self.data["profiles"]
        if not profs:
            return None
        prios = [p for p in profs if p.get("is_priority")]
        pool = prios if prios else profs
        best, best_ms = None, 10**9
        for p in pool:
            ms = measure_ping(p["address"], p["port"], timeout=1.5)
            p["ping_ms"] = ms
            if ms is not None and ms < best_ms:
                best, best_ms = p, ms
        return best or profs[0]

    def _toggle_vpn(self) -> None:
        if self.connected:
            self.core_mgr.stop(); self.connected = False; self.active_profile = None
            self.power_orb.set_connected(False); self.aurora_root.set_boost(False)
            self.status_lbl.setText(self._tr("disconnected"))
            self.live_ping_lbl.setText("● Ping: —"); self.exit_ip_lbl.setText("VPN: —")
            return

        s = self.data["settings"]
        mode = s.get("vpn_mode", "proxy_apps")
        if mode == "proxy_apps" and s.get("per_app_policy", "only_selected") == "only_selected" and not s.get("selected_apps"):
            QMessageBox.warning(self, "Albin-vpn", "Выберите хотя бы одну программу во вкладке 'Программы' (или переключитесь на TUN).")
            return
        if not self.is_admin and sys.platform == "win32":
            ans = QMessageBox.question(
                self, "Требуются права администратора",
                "Для строгого TUN (100% трафика) и точной маршрутизации по программам (.exe) нужны права администратора Windows.\nПерезапустить Albin-vpn от имени администратора сейчас?",
            )
            if ans == QMessageBox.Yes:
                self._relaunch_admin()
                return

        sel_id = self.data.get("selected_id", AUTO_ID)
        sel = self._pick_auto_best() if sel_id == AUTO_ID else next((p for p in self.data["profiles"] if p["id"] == sel_id), None)
        if not sel:
            QMessageBox.information(self, "Albin-vpn", "Add a subscription or key first."); return

        if mode == "tun" and not self.is_admin and sys.platform == "win32":
            QMessageBox.warning(self, "Albin-vpn", "Режим TUN (100% трафика) работает только с правами администратора Windows.")
            return

        core = choose_core(sel, mode, self.is_admin)
        use_tun = self.is_admin and (mode in ("tun", "proxy_apps"))
        aux_xray_cfg = None
        if use_tun and core == "xray":
            # Chain Xray (XHTTP/splithttp) on 127.0.0.1:10808 behind sing-box gVisor Wintun TUN!
            aux_xray_cfg = build_xray_config(sel, s)
            cfg = build_singbox_config(sel, s, use_tun=True, upstream_socks_port=10808)
            run_core = "sing-box"
            label_core = "sing-box+xray"
        elif core == "sing-box":
            cfg = build_singbox_config(sel, s, use_tun=use_tun)
            run_core = "sing-box"
            label_core = "sing-box"
        else:
            cfg = build_xray_config(sel, s)
            run_core = "xray"
            label_core = "xray"

        use_sys_proxy = not use_tun
        mode_tag = "TUN" if mode == "tun" else ("Proxy Apps (Wintun)" if use_tun else "System Proxy")

        if self.core_mgr.start(run_core, cfg, use_system_proxy=use_sys_proxy, aux_xray_config=aux_xray_cfg):
            self.connected = True; self.active_profile = sel; self.connect_ts = time.time()
            self.sess_rx, self.sess_tx, self.peak_rx = 0, 0, 0
            self.last_rx, self.last_tx = get_windows_net_bytes()
            self.power_orb.set_connected(True); self.aurora_root.set_boost(True)
            self.active_srv_lbl.setText(f"{'Авто → ' if sel_id == AUTO_ID else ''}{sel['name']}")
            self.status_lbl.setText(f"{self._tr('connected')} ({mode_tag} • {label_core})")
            self._run_live_ping()
            QTimer.singleShot(1200, self._check_both_ips)
        else:
            tail = "\n".join(getattr(self.core_mgr, "last_lines", [])[-6:])
            QMessageBox.warning(self, "Albin-vpn — Ошибка ядра", f"Ядро не запустилось:\n{tail}\n\nОткройте вкладку Журнал для подробностей.")

    def _tick_timer(self) -> None:
        if self.connected and self.core_mgr.proc and self.core_mgr.proc.poll() is not None:
            code = self.core_mgr.proc.returncode
            self.core_mgr.stop()
            self.connected = False; self.active_profile = None
            self.power_orb.set_connected(False); self.aurora_root.set_boost(False)
            self.status_lbl.setText(f"Ошибка ядра (код {code})")
            self.live_ping_lbl.setText("● Ping: —"); self.exit_ip_lbl.setText("VPN: —")
            tail = "\n".join(getattr(self.core_mgr, "last_lines", [])[-5:])
            self._append_log(f"[WATCHDOG] Ядро остановилось (код {code}).")
            QMessageBox.warning(self, "Albin-vpn", f"VPN-ядро остановилось (код {code}):\n{tail}")
            return
        if self.connected and self.active_profile:
            sec = int(time.time() - self.connect_ts)
            h, m, s = sec // 3600, (sec % 3600) // 60, sec % 60
            self.status_lbl.setText(f"{self._tr('connected')} • {h:02d}:{m:02d}:{s:02d}")
            rx, tx = get_windows_net_bytes()
            drx = max(0, rx - self.last_rx); dtx = max(0, tx - self.last_tx)
            self.last_rx, self.last_tx = rx, tx
            self.sess_rx += drx; self.sess_tx += dtx
            if drx > self.peak_rx:
                self.peak_rx = drx
            self.dl_val_lbl.setText(fmt_rate(drx)); self.ul_val_lbl.setText(fmt_rate(dtx))
            self.session_tot_lbl.setText(f"Session: ↓ {fmt_bytes(self.sess_rx)}  •  ↑ {fmt_bytes(self.sess_tx)}  •  Peak: {fmt_rate(self.peak_rx)}")
            self.dl_spark.push_value(max(0.2, drx / 1024.0))
            self.ul_spark.push_value(max(0.2, dtx / 1024.0))

            if sec > 0 and sec % 5 == 0:
                k = f"{self.active_profile['address']}:{self.active_profile['port']}"
                st = self.data.setdefault("server_stats", {}).setdefault(
                    k, {"name": self.active_profile["name"], "proto": self.active_profile["protocol"], "rx": 0, "tx": 0, "sec": 0}
                )
                st["rx"] += drx * 5; st["tx"] += dtx * 5; st["sec"] += 5
                self._save_state()
        else:
            self.dl_spark.push_value(0.15); self.ul_spark.push_value(0.15)

    def _append_log(self, msg: str) -> None:
        self.log_box.appendPlainText(msg)

    def closeEvent(self, event) -> None:
        self.core_mgr.stop(); super().closeEvent(event)
