import os

THEME_FILE = "/etc/utn-os/theme"

UTN_GREEN = "#1C9E3F"
UTN_BLUE = "#2E6FD0"

PALETTES = {
    "dark": {
        "bg": "#0B0E0B", "panel": "#131813", "border": "#2A3B28",
        "text": "#E6F4E8", "muted": "#8FAF97", "input": "#0A0D0A",
        "hover": "#1A2318", "pressed": "#0F1410",
        "accent": "#1C9E3F", "accent_hover": "#24B54C", "accent_pressed": "#178B38",
        "blue": "#2E6FD0", "title": "#2E6FD0", "cta_text": "#FFFFFF",
        "selection": "#1C9E3F", "selection_text": "#06100A",
        "danger": "#7A2838", "danger_hover": "#963245", "danger_text": "#F5D7DC",
        "grad": ("qlineargradient(x1:0,y1:0,x2:1,y2:0, "
                 "stop:0 #1C9E3F, stop:0.55 #238F57, stop:1 #2E6FD0)"),
    },
    "light": {
        "bg": "#F4F7F5", "panel": "#E7EEEA", "border": "#B8C8BE",
        "text": "#10231A", "muted": "#5E7A6A", "input": "#FFFFFF",
        "hover": "#DCE7E1", "pressed": "#D2DFD8",
        "accent": "#17913B", "accent_hover": "#1FA84A", "accent_pressed": "#147B31",
        "blue": "#2E6FD0", "title": "#2E6FD0", "cta_text": "#FFFFFF",
        "selection": "#1C9E3F", "selection_text": "#0A1A10",
        "danger": "#C62828", "danger_hover": "#DC3535", "danger_text": "#FFFFFF",
        "grad": ("qlineargradient(x1:0,y1:0,x2:1,y2:0, "
                 "stop:0 #1C9E3F, stop:0.55 #259A58, stop:1 #2E6FD0)"),
    },
}


def current_theme():
    try:
        with open(THEME_FILE) as fh:
            mode = fh.read().strip()
            if mode in PALETTES:
                return mode
    except OSError:
        pass
    return "dark"


def save_theme(mode):
    try:
        os.makedirs("/etc/utn-os", exist_ok=True)
        with open(THEME_FILE, "w") as fh:
            fh.write(mode + "\n")
    except OSError:
        pass


def ui_scale():
    from PyQt5 import QtWidgets
    try:
        screen = QtWidgets.QApplication.primaryScreen()
        geo = screen.geometry()
        return max(1.0, min(2.5, min(geo.width() / 1920.0,
                                     geo.height() / 1080.0)))
    except Exception:
        return 1.0


def stylesheet(mode="dark", scale=1.0):
    P = PALETTES[mode]
    fs = lambda n: int(n * scale)
    return f"""
QWidget {{ background-color:{P['bg']}; color:{P['text']}; font-size:{fs(14)}px; }}
QFrame, QDialog, QMessageBox {{ background-color:{P['bg']}; }}
QLabel {{ background:transparent; color:{P['text']}; }}
QToolTip {{ background-color:{P['panel']}; color:{P['text']}; border:1px solid {P['border']}; }}
QPushButton {{
    background-color:{P['panel']}; border:1px solid {P['border']};
    border-radius:{fs(10)}px; padding:{fs(12)}px; text-align:left; padding-left:{fs(20)}px;
    color:{P['text']};
}}
QPushButton:hover {{ background-color:{P['hover']}; }}
QPushButton:pressed {{ background-color:{P['pressed']}; }}
QPushButton:disabled {{ color:{P['muted']}; background-color:{P['panel']}; }}
QPushButton#accent {{
    background:{P['grad']}; border:none; font-weight:bold; text-align:center;
    color:{P['cta_text']};
}}
QPushButton#accent:hover {{ background:{P['grad']}; }}
QPushButton#toggle {{
    background:transparent; border:1px solid {P['border']}; border-radius:{fs(8)}px;
    padding:{fs(6)}px; padding-left:{fs(12)}px; padding-right:{fs(12)}px;
    text-align:center; color:{P['text']};
}}
QPushButton#toggle:hover {{ background-color:{P['hover']}; }}
QPushButton#danger {{ background-color:{P['danger']}; border:none; text-align:center; color:{P['danger_text']}; }}
QPushButton#danger:hover {{ background-color:{P['danger_hover']}; }}
QComboBox {{
    background-color:{P['panel']}; border:1px solid {P['border']};
    border-radius:{fs(6)}px; padding:{fs(6)}px; color:{P['text']};
}}
QComboBox QAbstractItemView {{
    background-color:{P['panel']}; color:{P['text']};
    selection-background-color:{P['selection']};
}}
QProgressBar {{
    background-color:{P['panel']}; border:1px solid {P['border']};
    border-radius:{fs(8)}px; text-align:center; color:{P['text']};
}}
QProgressBar::chunk {{ background:{P['grad']}; border-radius:{fs(8)}px; }}
QPlainTextEdit, QLineEdit {{
    background-color:{P['input']}; border:1px solid {P['border']};
    border-radius:{fs(8)}px; padding:{fs(6)}px; color:{P['text']};
}}
QCheckBox {{ background:transparent; color:{P['text']}; spacing:{fs(8)}px; }}
QSpinBox {{
    background-color:{P['panel']}; border:1px solid {P['border']};
    border-radius:{fs(6)}px; padding:{fs(4)}px; color:{P['text']};
}}
QGroupBox {{{{
    border:1px solid {P['border']}; border-radius:{fs(10)}px;
    margin-top:{fs(14)}px; padding-top:{fs(10)}px;
}}}}
QGroupBox::title {{
    subcontrol-origin:margin; left:{fs(12)}px; padding:0 {fs(6)}px;
    color:{P['title']}; font-weight:bold;
}}
QInputDialog {{ background-color:{P['bg']}; }}
"""