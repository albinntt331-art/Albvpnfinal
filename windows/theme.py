"""Albin-vpn v5 Final Material 3 Expressive theme engine (Purple default, Pure Ocean Blue)."""

ACCENT_PALETTES = {
    "purple": {
        "name": "Фиолетовый (База)", "swatch": "#8B5CF6",
        "dark": {"primary": "#C084FC", "glow": "#A855F7", "on_primary": "#FFFFFF", "primary_container": "#5B21B6", "bg": "#090711", "surface": "#151026", "surface_high": "#221A3C", "text": "#F6F5FA", "text_muted": "#BDC2D6", "border": "#392D5C"},
        "light": {"primary": "#7C3AED", "glow": "#8B5CF6", "on_primary": "#FFFFFF", "primary_container": "#EDE9FE", "bg": "#FAF7FF", "surface": "#F3ECFF", "surface_high": "#E9DDFC", "text": "#151822", "text_muted": "#4F566B", "border": "#D5C4F2"},
    },
    "blue": {
        "name": "Синий океан", "swatch": "#0EA5E9",
        "dark": {"primary": "#38BDF8", "glow": "#0EA5E9", "on_primary": "#04263B", "primary_container": "#0369A1", "bg": "#050D16", "surface": "#0A192A", "surface_high": "#112842", "text": "#F2F8FF", "text_muted": "#9AC5E6", "border": "#1A3F5F"},
        "light": {"primary": "#0284C7", "glow": "#0EA5E9", "on_primary": "#FFFFFF", "primary_container": "#E0F2FE", "bg": "#F4FAFF", "surface": "#E6F4FE", "surface_high": "#D4ECFC", "text": "#0F1E2E", "text_muted": "#42617D", "border": "#BAE0FA"},
    },
    "emerald": {
        "name": "Кибер-изумруд", "swatch": "#10B981",
        "dark": {"primary": "#34D399", "glow": "#10B981", "on_primary": "#022C22", "primary_container": "#047857", "bg": "#05120E", "surface": "#0A1F18", "surface_high": "#113328", "text": "#ECFAF4", "text_muted": "#A0D9C6", "border": "#1D5744"},
        "light": {"primary": "#059669", "glow": "#10B981", "on_primary": "#FFFFFF", "primary_container": "#D1FAE5", "bg": "#F2FCF8", "surface": "#E3F7EF", "surface_high": "#D0F0E3", "text": "#0C221A", "text_muted": "#3B6254", "border": "#B2E5D2"},
    },
    "rose": {
        "name": "Неон-розовый", "swatch": "#EC4899",
        "dark": {"primary": "#F472B6", "glow": "#EC4899", "on_primary": "#FFFFFF", "primary_container": "#9D174D", "bg": "#14070D", "surface": "#220C17", "surface_high": "#361425", "text": "#FDF2F7", "text_muted": "#E6B5CA", "border": "#5E2440"},
        "light": {"primary": "#DB2777", "glow": "#EC4899", "on_primary": "#FFFFFF", "primary_container": "#FCE7F3", "bg": "#FFF7FA", "surface": "#FCE9F1", "surface_high": "#F7D7E5", "text": "#2A0F1D", "text_muted": "#663D52", "border": "#F2C0D6"},
    },
    "amber": {
        "name": "Янтарный", "swatch": "#F59E0B",
        "dark": {"primary": "#FBBF24", "glow": "#F59E0B", "on_primary": "#2E1202", "primary_container": "#B45309", "bg": "#120C05", "surface": "#21160A", "surface_high": "#362411", "text": "#FEF8EE", "text_muted": "#E3C8A8", "border": "#5E401E"},
        "light": {"primary": "#D97706", "glow": "#F59E0B", "on_primary": "#FFFFFF", "primary_container": "#FEF3C7", "bg": "#FFFFF5", "surface": "#F9EEDF", "surface_high": "#F2DFC7", "text": "#281808", "text_muted": "#664C30", "border": "#E8CDA9"},
    },
}


def get_palette(accent_key: str = "purple", dark: bool = True) -> dict:
    return ACCENT_PALETTES.get(accent_key, ACCENT_PALETTES["purple"])["dark" if dark else "light"]


def build_stylesheet(accent_key: str = "purple", dark: bool = True) -> str:
    pal = get_palette(accent_key, dark)
    return f"""
    QMainWindow, QWidget {{ background-color: {pal['bg']}; color: {pal['text']}; font-family: "Segoe UI Variable", "Segoe UI", sans-serif; font-size: 13px; }}
    QFrame#NavRail {{ background-color: {pal['surface']}; border-right: 1px solid {pal['border']}; }}
    QPushButton.NavBtn {{ background-color: transparent; color: {pal['text_muted']}; border: 1px solid transparent; border-radius: 18px; padding: 11px 16px; text-align: left; font-weight: 600; }}
    QPushButton.NavBtn:hover {{ background-color: {pal['surface_high']}; color: {pal['text']}; }}
    QPushButton.NavBtn[active="true"] {{ background-color: {pal['primary_container']}; border: 1px solid {pal['primary']}; color: {pal['text']}; }}
    QFrame.Card {{ background-color: {pal['surface']}; border: 1px solid {pal['border']}; border-radius: 24px; }}
    QPushButton.PrimaryBtn {{ background-color: {pal['primary']}; color: {pal['on_primary']}; border: none; border-radius: 16px; padding: 9px 18px; font-weight: 700; }}
    QPushButton.PrimaryBtn:hover {{ background-color: {pal['glow']}; color: #FFFFFF; }}
    QPushButton.TonalBtn {{ background-color: {pal['surface_high']}; color: {pal['text']}; border: 1px solid {pal['border']}; border-radius: 16px; padding: 8px 15px; font-weight: 600; }}
    QPushButton.TonalBtn:hover {{ border: 1px solid {pal['primary']}; }}
    QLineEdit, QComboBox, QPlainTextEdit, QListWidget {{ background-color: {pal['surface_high']}; color: {pal['text']}; border: 1px solid {pal['border']}; border-radius: 16px; padding: 9px 12px; }}
    QListWidget::item {{ padding: 12px; border-radius: 14px; margin: 3px 0px; }}
    QListWidget::item:selected {{ background-color: {pal['primary_container']}; border: 1px solid {pal['primary']}; color: {pal['text']}; }}
    QCheckBox {{ spacing: 9px; font-weight: 500; }}
    QLabel.Muted {{ color: {pal['text_muted']}; }}
    """
