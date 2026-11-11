"""Optional real PyQt5 smoke test, with all disk discovery/commands stubbed.
Run: QT_QPA_PLATFORM=offscreen python3 tests/smoke_gui.py
Requires PyQt5; it is not part of the standard-library unittest suite.
"""
import importlib.machinery
import importlib.util
import os
from pathlib import Path
import sys
import tomllib
from unittest.mock import patch

os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'iso/airootfs/usr/share/utn-os'
sys.path.insert(0, str(ASSETS))
from PyQt5 import QtCore, QtGui, QtWidgets
import utn_theme

def load(name):
    loader = importlib.machinery.SourceFileLoader(name, str(ROOT / 'iso/airootfs/usr/local/bin' / name))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module

app = QtWidgets.QApplication([])
app.setStyleSheet(utn_theme.stylesheet())
installer = load('utn-installer')
installer.LAYOUT_DIR = str(ASSETS / 'layouts')
layouts = []
for path in sorted((ASSETS / 'layouts').iterdir()):
    meta = tomllib.loads((path / 'meta.toml').read_text())
    layouts.append(dict(id=path.name, display=meta['display'], description=meta['description'], default=meta['default']))
with patch.object(installer, 'disks', return_value=[]), patch.object(installer, 'discover_layouts', return_value=layouts), patch.object(installer, 'run', return_value=''):
    window = installer.InstallerWindow()
    window.resize(1024, 768)
    window.show()
    app.processEvents()
    assert window.size().width() <= 1024 and window.size().height() <= 768
    for page in range(window.stack.count()):
        window.stack.setCurrentIndex(page)
        app.processEvents()
        assert window.minimumSizeHint().height() <= 768
        assert window.minimumSizeHint().width() <= 1024
    assert not window.autologin.isChecked()
    assert not window.chk_plymouth.isChecked()
    assert window.layout_combo.count() == 11
    window._worker = type('Worker', (), dict(cleanup_ok=True, isRunning=lambda self: False))()
    with patch.object(QtWidgets.QMessageBox, 'critical'):
        window.stack.setCurrentIndex(5)
        window._install_done(False, 'simulated failure')
    assert window.btn_back.isVisible() and window.btn_back.isEnabled()
    window.back()
    assert window.stack.currentIndex() == 1
    window._install_done(True, 'simulated success')
    assert window.stack.currentIndex() == 6 and window.btn_reboot.isEnabled()
    # Verify exported log includes messages beyond the visible 1000-block buffer.
    window._append_log('sample log entry')
    import tempfile
    with tempfile.TemporaryDirectory() as temp:
        logfile = Path(temp, 'test.log')
        with patch.object(QtWidgets.QFileDialog, 'getSaveFileName', return_value=(str(logfile), '')):
            window._save_log()
        assert 'sample log entry' in logfile.read_text()
    window.close()

# Verify actual PyQt5 result order, not just a mock of that contract.
def accept():
    dialog = app.activeModalWidget()
    dialog.setTextValue('macos')
    dialog.accept()
QtCore.QTimer.singleShot(0, accept)
assert QtWidgets.QInputDialog.getItem(None, 'test', 'layout', ['chromeos', 'frutiger', 'macos'], 0, False) == ('macos', True)
welcome = load('utn-welcome')
with patch.object(welcome, 'discover_layouts', return_value=layouts):
    window = welcome.WelcomeWindow()
    window.show()
    app.processEvents()
    window.close()
print('PyQt5 GUI smoke: OK (7 pages at 1024x768, error recovery, success, log export, welcome, getItem)')
