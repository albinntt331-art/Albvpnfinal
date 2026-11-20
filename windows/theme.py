"""Albin-vpn v6 Ultimate — Frosted Glass + Living Aurora Theme Engine (6 Google Pixel Palettes)."""

ACCENT_PALETTES = {
    "purple": {
        "name": "Фиолетовый (База)", "swatch": "#8B5CF6",
        "dark": {"primary": "#C084FC", "glow": "#A855F7", "tertiary": "#F472B6", "on_primary": "#FFFFFF", "primary_container": "#5B21B6", "bg": "#090711", "surface": "rgba(21, 16, 38, 218)", "surface_solid": "#151026", "surface_high": "rgba(34, 26, 60, 232)", "text": "#F6F5FA", "text_muted": "#BDC2D6", "border": "#3F3166"},
        "light": {"primary": "#7C3AED", "glow": "#8B5CF6", "tertiary": "#EC4899", "on_primary": "#FFFFFF", "primary_container": "#EDE9FE", "bg": "#FAF7FF", "surface": "rgba(243, 236, 255, 225)", "surface_solid": "#F3ECFF", "surface_high": "rgba(233, 221, 252, 238)", "text": "#151822", "text_muted": "#4F566B", "border": "#D5C4F2"},
    },
    "ultraviolet": {
        "name": "Ультрафиолет", "swatch": "#D946EF",
        "dark": {"primary": "#E879F9", "glow": "#D946EF", "tertiary": "#38BDF8", "on_primary": "#FFFFFF", "primary_container": "#86198F", "bg": "#0A0512", "surface": "rgba(23, 13, 40, 218)", "surface_solid": "#170D28", "surface_high": "rgba(39, 22, 66, 232)", "text": "#FAF5FF", "text_muted": "#CBBCE0", "border": "#572A8A"},
        "light": {"primary": "#A21CAF", "glow": "#D946EF", "tertiary": "#0284C7", "on_primary": "#FFFFFF", "primary_container": "#FAE8FF", "bg": "#FDF7FF", "surface": "rgba(247, 233, 254, 225)", "surface_solid": "#F7E9FE", "surface_high": "rgba(238, 212, 252, 238)", "text": "#1C1024", "text_muted": "#5C476B", "border": "#E5C2FA"},
    },
    "blue": {
        "name": "Синий океан", "swatch": "#0EA5E9",
        "dark": {"primary": "#38BDF8", "glow": "#0EA5E9", "tertiary": "#22D3EE", "on_primary": "#04263B", "primary_container": "#0369A1", "bg": "#050D16", "surface": "rgba(10, 25, 42, 218)", "surface_solid": "#0A192A", "surface_high": "rgba(17, 40, 66, 232)", "text": "#F2F8FF", "text_muted": "#9AC5E6", "border": "#1E4A70"},
        "light": {"primary": "#0284C7", "glow": "#0EA5E9", "tertiary": "#06B6D4", "on_primary": "#FFFFFF", "primary_container": "#E0F2FE", "bg": "#F4FAFF", "surface": "rgba(230, 244, 254, 225)", "surface_solid": "#E6F4FE", "surface_high": "rgba(212, 236, 252, 238)", "text": "#0F1E2E", "text_muted": "#42617D", "border": "#BAE0FA"},
    },
    "emerald": {
        "name": "Кибер-изумруд", "swatch": "#10B981",
        "dark": {"primary": "#34D399", "glow": "#10B981", "tertiary": "#2DD4BF", "on_primary": "#022C22", "primary_container": "#047857", "bg": "#05120E", "surface": "rgba(10, 31, 24, 218)", "surface_solid": "#0A1F18", "surface_high": "rgba(17, 51, 40, 232)", "text": "#ECFAF4", "text_muted": "#A0D9C6", "border": "#21614C"},
        "light": {"primary": "#059669", "glow": "#10B981", "tertiary": "#0D9488", "on_primary": "#FFFFFF", "primary_container": "#D1FAE5", "bg": "#F2FCF8", "surface": "rgba(227, 247, 239, 225)", "surface_solid": "#E3F7EF", "surface_high": "rgba(208, 240, 227, 238)", "text": "#0C221A", "text_muted": "#3B6254", "border": "#B2E5D2"},
    },
    "rose": {
        "name": "Неон-розовый", "swatch": "#EC4899",
        "dark": {"primary": "#F472B6", "glow": "#EC4899", "tertiary": "#FB7185", "on_primary": "#FFFFFF", "primary_container": "#9D174D", "bg": "#14070D", "surface": "rgba(34, 12, 23, 218)", "surface_solid": "#220C17", "surface_high": "rgba(54, 20, 37, 232)", "text": "#FDF2F7", "text_muted": "#E6B5CA", "border": "#662846"},
        "light": {"primary": "#DB2777", "glow": "#EC4899", "tertiary": "#E11D48", "on_primary": "#FFFFFF", "primary_container": "#FCE7F3", "bg": "#FFF7FA", "surface": "rgba(252, 233, 241, 225)", "surface_solid": "#FCE9F1", "surface_high": "rgba(247, 215, 229, 238)", "text": "#2A0F1D", "text_muted": "#663D52", "border": "#F2C0D6"},
    },
    "amber": {
        "name": "Янтарный", "swatch": "#F59E0B",
        "dark": {"primary": "#FBBF24", "glow": "#F59E0B", "tertiary": "#FB923C", "on_primary": "#2E1202", "primary_container": "#B45309", "bg": "#120C05", "surface": "rgba(33, 22, 10, 218)", "surface_solid": "#21160A", "surface_high": "rgba(54, 36, 17, 232)", "text": "#FEF8EE", "text_muted": "#E3C8A8", "border": "#664621"},
        "light": {"primary": "#D97706", "glow": "#F59E0B", "tertiary": "#EA580C", "on_primary": "#FFFFFF", "primary_container": "#FEF3C7", "bg": "#FFFFF5", "surface": "rgba(249, 238, 223, 225)", "surface_solid": "#F9EEDF", "surface_high": "rgba(242, 223, 199, 238)", "text": "#281808", "text_muted": "#664C30", "border": "#E8CDA9"},
    },
}


def get_palette(accent_key: str = "purple", dark: bool = True) -> dict:
    return ACCENT_PALETTES.get(accent_key, ACCENT_PALETTES["purple"])["dark" if dark else "light"]


def build_stylesheet(accent_key: str = "purple", dark: bool = True) -> str:
    pal = get_palette(accent_key, dark)
    return f"""
    QMainWindow {{ background-color: {pal['bg']}; }}
    QWidget {{ background-color: transparent; color: {pal['text']}; font-family: "Segoe UI Variable", "Segoe UI", sans-serif; font-size: 13px; }}
    QFrame#NavRail {{
        background-color: {pal['surface']};
        border-right: 1px solid {pal['border']};
    }}
    QPushButton.NavBtn {{
        background-color: transparent;
        color: {pal['text_muted']};
        border: 1px solid transparent;
        border-radius: 18px;
        padding: 11px 16px;
        text-align: left;
        font-weight: 600;
    }}
    QPushButton.NavBtn:hover {{
        background-color: {pal['surface_high']};
        color: {pal['text']};
    }}
    QPushButton.NavBtn[active="true"] {{
        background-color: {pal['primary_container']};
        border: 1px solid {pal['primary']};
        color: #FFFFFF;
    }}
    QFrame.Card {{
        background-color: {pal['surface']};
        border: 1px solid {pal['border']};
        border-radius: 26px;
    }}
    QFrame#ModePill {{
        background-color: {pal['surface']};
        border: 1px solid {pal['border']};
        border-radius: 24px;
    }}
    QPushButton.ModeTab {{
        background-color: transparent;
        color: {pal['text_muted']};
        border: none;
        border-radius: 20px;
        padding: 9px 18px;
        font-weight: 600;
    }}
    QPushButton.ModeTab[active="true"] {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {pal['primary']}, stop:1 {pal['tertiary']});
        color: #FFFFFF;
        font-weight: 700;
    }}
    QPushButton.PrimaryBtn {{
        background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {pal['primary']}, stop:1 {pal['tertiary']});
        color: #FFFFFF;
        border: none;
        border-radius: 18px;
        padding: 9px 18px;
        font-weight: 700;
    }}
    QPushButton.PrimaryBtn:hover {{
        background-color: {pal['glow']};
    }}
    QPushButton.TonalBtn {{
        background-color: {pal['surface_high']};
        color: {pal['text']};
        border: 1px solid {pal['border']};
        border-radius: 18px;
        padding: 8px 15px;
        font-weight: 600;
    }}
    QPushButton.TonalBtn:hover {{
        border: 1px solid {pal['primary']};
    }}
    QLineEdit, QComboBox, QPlainTextEdit, QListWidget {{
        background-color: {pal['surface_high']};
        color: {pal['text']};
        border: 1px solid {pal['border']};
        border-radius: 18px;
        padding: 9px 12px;
    }}
    QComboBox QAbstractItemView {{
        background-color: {pal['surface_solid']};
        color: {pal['text']};
        selection-background-color: {pal['primary_container']};
    }}
    QListWidget::item {{
        padding: 12px;
        border-radius: 14px;
        margin: 3px 0px;
    }}
    QListWidget::item:selected {{
        background-color: {pal['primary_container']};
        border: 1px solid {pal['primary']};
        color: #FFFFFF;
    }}
    QCheckBox {{ spacing: 9px; font-weight: 500; }}
    QLabel.Muted {{ color: {pal['text_muted']}; }}
    """
