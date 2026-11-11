"""Regression tests: no real disks, mounts, package installs or chroots are used."""
import ast
import configparser
import importlib.machinery
import importlib.util
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import types
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / 'iso/airootfs/usr/local/bin'

class Signal:
    def __set_name__(self, owner, name): self.name = name
    def __get__(self, obj, owner):
        if obj is None: return self
        return obj.__dict__.setdefault(self.name, types.SimpleNamespace(emit=Mock()))

class Thread:
    def __init__(self, *args): pass

qt = types.SimpleNamespace(
    QtCore=types.SimpleNamespace(QThread=Thread, pyqtSignal=lambda *a: Signal()),
    QtGui=types.SimpleNamespace(),
    QtWidgets=types.SimpleNamespace(QWidget=object, QMessageBox=Mock(), QInputDialog=Mock()))

def load(name, path):
    loader = importlib.machinery.SourceFileLoader(name, str(path))
    spec = importlib.util.spec_from_loader(name, loader)
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {'PyQt5': qt, 'utn_theme': Mock()}):
        loader.exec_module(module)
    return module

installer = load('utn_installer_test', BIN / 'utn-installer')
welcome = load('utn_welcome_test', BIN / 'utn-welcome')

class InstallerTests(unittest.TestCase):
    def setUp(self):
        self.opts = dict(disk='/dev/mock', filesystem='ext4', swap=0, locale='es_MX.UTF-8',
            keyboard='latam', timezone='America/Mexico_City', hostname='utn-pc',
            username='student', fullname='Student', password='private-test-password',
            root_password='private-root-password', layout='macos')
        self.worker = installer.InstallWorker(self.opts.copy())

    def configure(self, temp, command=None, fstab='UUID=test / ext4 defaults 0 1\n'):
        kernel = Path(temp, 'source-kernel')
        kernel.write_bytes(b'kernel fixture')
        target = Path(temp, 'target'); target.mkdir()
        self.worker._kernel_source = str(kernel)
        scripts = []
        def run(cmd, **kwargs):
            if cmd[0] == 'genfstab': return fstab
            if cmd == ['blkid', '-s', 'UUID', '-o', 'value', '/dev/mock2']:
                return 'target-swap\n'
            if cmd[0] == 'arch-chroot':
                script = target / cmd[-1].lstrip('/')
                # Simular el /tmp vacío que arch-chroot monta sobre el destino.
                # El script y las credenciales deben seguir siendo accesibles.
                (target / 'tmp').rename(target / 'tmp-hidden')
                (target / 'tmp').mkdir()
                try:
                    scripts.append(script.read_text())
                    self.assertTrue((script.parent / 'chpasswd.in').is_file())
                finally:
                    (target / 'tmp').rmdir()
                    (target / 'tmp-hidden').rename(target / 'tmp')
                secret = script.parent / 'chpasswd.in'
                self.assertEqual(secret.stat().st_mode & 0o777, 0o600)
                self.assertEqual(secret.parent.stat().st_mode & 0o777, 0o700)
                if command: return command(cmd)
                return 'OK: configuration\n'
            raise AssertionError(f'Unexpected command {cmd}')
        with patch.object(installer, 'MOUNT', str(target)), patch.object(installer, 'run', side_effect=run), patch.object(installer, 'is_uefi', return_value=False):
            self.worker._configure('/dev/mock')
        return target, scripts[0]

    def test_rsync_cr_lf_and_final_line(self):
        stream = io.TextIOWrapper(io.BytesIO(b'42 20%\r84 80%\n100 100%\r\nfinal stats'), newline=None)
        proc = Mock(stdout=stream, returncode=0)
        proc.poll.return_value = 0
        with patch.object(installer.subprocess, 'Popen', return_value=proc):
            self.worker._copy_system()
        values = [c.args[0] for c in self.worker.progress.emit.call_args_list]
        self.assertEqual(values, sorted(values))
        self.assertLess(max(values), 80)
        self.worker.log.emit.assert_any_call('final stats')
        self.assertIsNone(self.worker._copy_process)
        self.assertTrue(stream.closed)

    def test_rsync_failure_is_not_success(self):
        proc = Mock(stdout=io.StringIO('copy failed\n'), returncode=23)
        proc.poll.return_value = 23
        with patch.object(installer.subprocess, 'Popen', return_value=proc):
            with self.assertRaisesRegex(RuntimeError, 'rsync'):
                self.worker._copy_system()
        self.assertIsNone(self.worker._copy_process)

    def test_copy_read_error_terminates_child(self):
        class BrokenStream:
            def __iter__(self): raise OSError('broken pipe')
            def close(self): pass
        proc = Mock(stdout=BrokenStream())
        with patch.object(installer.subprocess, 'Popen', return_value=proc), patch.object(installer, 'stop_process') as stop:
            with self.assertRaises(OSError): self.worker._copy_system()
        stop.assert_called_once_with(proc)

    def test_command_timeout_reaps_process(self):
        proc = Mock()
        proc.communicate.side_effect = subprocess.TimeoutExpired('fake', 1)
        with patch.object(installer.subprocess, 'Popen', return_value=proc), patch.object(installer, 'stop_process') as stop:
            with self.assertRaises(subprocess.TimeoutExpired): installer.run(['fake'], timeout=1)
        stop.assert_called_once_with(proc)

    def test_configure_creates_target_dirs_restores_kernel_and_removes_secrets(self):
        with tempfile.TemporaryDirectory() as temp:
            target, script = self.configure(temp)
            self.assertEqual((target / 'boot/vmlinuz-linux').read_bytes(), b'kernel fixture')
            self.assertEqual((target / 'tmp').stat().st_mode & 0o7777, 0o1777)
            self.assertEqual(list((target / 'tmp').iterdir()), [])
            self.assertEqual((target / 'var/tmp').stat().st_mode & 0o7777, 0o1777)
            self.assertEqual(list((target / 'var/tmp').iterdir()), [])
            self.assertNotIn(self.opts['password'], script)
            subprocess.run(['bash', '-n'], input=script, text=True, check=True)

    def test_secret_cleanup_on_chroot_error(self):
        with tempfile.TemporaryDirectory() as temp:
            def fail(_): raise RuntimeError('chroot failed')
            with self.assertRaisesRegex(RuntimeError, 'chroot failed'):
                self.configure(temp, command=fail)
            self.assertEqual(list(Path(temp, 'target/var/tmp').iterdir()), [])

    def test_machine_id_is_empty_to_preserve_installed_service_choices(self):
        with tempfile.TemporaryDirectory() as temp:
            target, _ = self.configure(temp)
            machine_id = target / 'etc/machine-id'
            self.assertEqual(machine_id.read_bytes(), b'')
            self.assertEqual(machine_id.stat().st_mode & 0o777, 0o444)

    def test_empty_fstab_aborts_before_chroot(self):
        with tempfile.TemporaryDirectory() as temp:
            command = Mock()
            with self.assertRaisesRegex(RuntimeError, 'genfstab'):
                self.configure(temp, command=command, fstab='')
            command.assert_not_called()
            self.assertEqual(list(Path(temp, 'target/tmp').iterdir()), [])

    def test_fstab_excludes_other_live_swap(self):
        with tempfile.TemporaryDirectory() as temp:
            target, _ = self.configure(temp, fstab='UUID=root / ext4 defaults 0 1\nUUID=host-swap none swap defaults 0 0\n')
            self.assertNotIn('host-swap', (target / 'etc/fstab').read_text())

    def test_target_swap_uses_its_uuid_and_allows_slow_device_discovery(self):
        self.worker._swap_device = '/dev/mock2'
        with tempfile.TemporaryDirectory() as temp:
            target, _ = self.configure(temp, fstab='UUID=root / ext4 defaults 0 1\nUUID=host-swap none swap defaults 0 0\n')
            entries = [line.split() for line in (target / 'etc/fstab').read_text().splitlines()]
            swap = [entry for entry in entries if entry[2] == 'swap']
            self.assertEqual(len(swap), 1)
            self.assertEqual(swap[0][0], 'UUID=target-swap')
            self.assertEqual(set(swap[0][3].split(',')), {'defaults', 'nofail', 'x-systemd.device-timeout=5min'})

    def test_generated_initramfs_failure_stops_shell(self):
        with tempfile.TemporaryDirectory() as temp:
            _, script = self.configure(temp)
        command = next(line for line in script.splitlines() if line.startswith('mkinitcpio -P'))
        result = subprocess.run(['bash', '-c', 'set -euo pipefail\nmkinitcpio() { return 7; }\n'+command+'\necho false-success'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 7)
        self.assertNotIn('false-success', result.stdout)

    def test_optional_scripts_have_valid_bash(self):
        self.worker.opts.update(plymouth=True, snapper=True, firewall=True, updates=True, autologin=True)
        with tempfile.TemporaryDirectory() as temp:
            _, script = self.configure(temp)
        subprocess.run(['bash', '-n'], input=script, text=True, check=True)
        self.assertNotIn('|| true\nmkinitcpio', script)

    def test_cleanup_on_install_failure(self):
        self.worker._mounted = True
        self.worker._swap_device = '/dev/mock3'
        self.worker._mapper_open = True
        self.worker.install = Mock(side_effect=RuntimeError('copy failed'))
        with patch.object(installer, 'run') as run:
            self.worker.run()
        self.assertEqual([c.args[0][0] for c in run.call_args_list], ['swapoff', 'umount', 'cryptsetup'])
        self.assertFalse(self.worker.done.emit.call_args.args[0])
        self.assertTrue(self.worker.cleanup_ok)
        self.assertNotIn('password', self.worker.opts)

    def test_cleanup_failure_prevents_success(self):
        self.worker.install = Mock()
        self.worker._mounted = True
        with patch.object(installer, 'run', side_effect=RuntimeError('busy')):
            self.worker.run()
        self.assertFalse(self.worker.done.emit.call_args.args[0])
        self.assertFalse(self.worker.cleanup_ok)
        self.worker.progress.emit.assert_not_called()

    def test_secret_values_are_redacted(self):
        self.worker._log('error '+self.opts['password'])
        self.assertEqual(self.worker.log.emit.call_args.args[0], 'error [oculto]')

    def test_progress_tracks_work_and_success_follows_cleanup(self):
        events=[]
        for method in ['_partition','_format','_mount','_copy_system','_configure','_grub','_verify_boot']:
            setattr(self.worker, method, Mock(side_effect=lambda *a, name=method: events.append(name)))
        self.worker.progress.emit.side_effect=lambda value: events.append(value)
        self.worker._cleanup=Mock(side_effect=lambda: events.append('cleanup') or [])
        with patch.object(installer.os.path,'isfile',return_value=True), patch.object(installer.os.path,'ismount',return_value=False), patch.object(installer.os.path,'exists',return_value=False), patch.object(installer,'username_available',return_value=True), patch.object(installer,'validate_target'), patch.object(installer,'kernel_source',return_value='/fake-kernel'), patch.object(installer.shutil,'which',return_value='/fake-tool'):
            self.worker.run()
        self.assertLess(events.index('_partition'),events.index(8))
        self.assertLess(events.index('_copy_system'),events.index(80))
        self.assertLess(events.index('cleanup'),events.index(100))
        self.assertTrue(self.worker.done.emit.call_args.args[0])

    def test_luks_key_removed_when_format_fails(self):
        self.worker.opts.update(parts=['/dev/mock1'],encrypt=True,luks_passphrase='test-luks-pass')
        keys=[]
        def fail(cmd, **kwargs):
            if cmd[0]=='cryptsetup':
                key=Path(cmd[cmd.index('--key-file')+1]); keys.append(key)
                self.assertEqual(key.stat().st_mode & 0o777,0o600)
                raise RuntimeError('format failed')
        with patch.object(installer,'is_uefi',return_value=False), patch.object(installer,'run',side_effect=fail):
            with self.assertRaises(RuntimeError): self.worker._format('/dev/mock','ext4',0)
        self.assertTrue(keys)
        self.assertFalse(keys[0].exists())

    def test_boot_verification_rejects_missing_kernel_entry(self):
        with tempfile.TemporaryDirectory() as temp:
            for file in ['vmlinuz-linux','initramfs-linux.img','initramfs-linux-fallback.img','grub/grub.cfg']:
                path=Path(temp,'boot',file); path.parent.mkdir(parents=True,exist_ok=True); path.write_text('fixture')
            with patch.object(installer,'MOUNT',temp), patch.object(installer,'is_uefi',return_value=False):
                with self.assertRaisesRegex(RuntimeError,'GRUB'): self.worker._verify_boot()
                Path(temp,'boot/grub/grub.cfg').write_text('linux /boot/vmlinuz-linux root=UUID=test\ninitrd /boot/initramfs-linux.img\n')
                self.worker._verify_boot()

class ValidationTests(unittest.TestCase):
    def check(self,size=32*installer.GIB,swap=0,**kwargs):
        disk=dict(name='/dev/mock',type='disk',size=size,ro=False,mountpoints=[None]); disk.update(kwargs)
        with patch.object(installer,'run',return_value=json.dumps(dict(blockdevices=[disk]))), patch.object(installer,'system_size',return_value=4*installer.GIB), patch.object(installer,'is_uefi',return_value=True):
            installer.validate_target('/dev/mock',swap)

    def test_rejects_small_disk_without_swap(self):
        with self.assertRaisesRegex(RuntimeError,'espacio'): self.check(size=512*1024**2)
    def test_counts_swap_and_efi(self):
        with self.assertRaisesRegex(RuntimeError,'espacio'): self.check(size=16*installer.GIB,swap=4)
    def test_accepts_sufficient_capacity(self): self.check(swap=4)
    def test_rejects_readonly(self):
        with self.assertRaises(RuntimeError): self.check(ro=True)
    def test_rejects_mounted_child(self):
        with self.assertRaisesRegex(RuntimeError,'uso'):
            self.check(children=[dict(type='part',mountpoints=['/run/archiso/bootmnt'])])
    def test_rejects_swap_in_use(self):
        with self.assertRaisesRegex(RuntimeError,'uso'):
            self.check(children=[dict(type='part',mountpoints=['[SWAP]'])])
    def test_rejects_active_unmounted_mapper(self):
        with self.assertRaisesRegex(RuntimeError,'uso'):
            self.check(children=[dict(type='crypt',mountpoints=[None])])
    def test_rejects_root_and_existing_accounts(self):
        self.assertFalse(installer.username_available('root'))
        with patch.object(installer.pwd,'getpwnam',return_value=object()):
            self.assertFalse(installer.username_available('existing'))
        with patch.object(installer.pwd,'getpwnam',side_effect=KeyError):
            self.assertTrue(installer.username_available('newstudent'))
    def test_final_validation_stays_on_summary(self):
        state=types.SimpleNamespace(idx=4)
        window=types.SimpleNamespace(stack=types.SimpleNamespace(currentIndex=lambda:state.idx,setCurrentIndex=lambda n:setattr(state,'idx',n)),
            _validate_users=lambda:True,_validate_extras=lambda:True,_validate_disk=lambda:False,
            disk_status=types.SimpleNamespace(text=lambda:'disk busy'),_start_install=Mock())
        installer.InstallerWindow.next(window)
        self.assertEqual(state.idx,4)
        window._start_install.assert_not_called()
    def test_latin_american_console_keymap(self):
        self.assertEqual(installer.CONSOLE_KEYMAP['latam'],'la-latin1')

class WelcomeTests(unittest.TestCase):
    def check_layout(self,method,accepted=True,one=False):
        ids=['macos'] if one else ['chromeos','frutiger','macos']
        layouts=[dict(id=i,display=i,description=i) for i in ids]
        with patch.object(welcome,'discover_layouts',return_value=layouts), patch.object(welcome.QtWidgets.QInputDialog,'getItem',return_value=('macos  —  macos',accepted)), patch.object(welcome,'run',return_value=types.SimpleNamespace(returncode=0)) as run:
            getattr(welcome.WelcomeWindow,method)(object())
        if accepted: run.assert_called_once_with(['utn-layout','macos'])
        else: run.assert_not_called()
    def test_selected_layout(self):
        for method in ['try_live','pick_layout']:
            with self.subTest(method=method): self.check_layout(method)
    def test_cancel_does_not_change_layout(self):
        for method in ['try_live','pick_layout']:
            with self.subTest(method=method): self.check_layout(method,accepted=False)
    def test_single_layout(self):
        for method in ['try_live','pick_layout']:
            with self.subTest(method=method): self.check_layout(method,one=True)

class ProfileTests(unittest.TestCase):
    def test_layout_panel_references(self):
        for path in (ROOT/'iso/airootfs/usr/share/utn-os/layouts').glob('*/lxqt/panel.conf'):
            with self.subTest(layout=path.parent.parent.name):
                config = configparser.ConfigParser(interpolation=None)
                config.read(path)
                panels = [name.strip() for name in config['General']['panels'].split(',')]
                self.assertTrue(panels)
                used = set()
                for panel in panels:
                    self.assertIn(config[panel]['position'], ('Top', 'Bottom', 'Left', 'Right'))
                    self.assertGreater(config[panel].getint('width'), 0)
                    plugins = [name.strip() for name in config[panel]['plugins'].split(',')]
                    self.assertGreater(len(plugins), 1)
                    for name in plugins:
                        self.assertNotIn(name, used)
                        used.add(name)
                        self.assertTrue(config[name]['type'])
                        self.assertNotIn(config[name]['type'], ('clock', 'configure'))

    def test_layout_window_themes_and_assets(self):
        layouts = ROOT/'iso/airootfs/usr/share/utn-os/layouts'
        themes = ROOT/'iso/airootfs/usr/share/themes'
        ids = sorted(path.name for path in layouts.iterdir() if path.is_dir())
        self.assertEqual(ids, ['chromeos', 'frutiger', 'macos', 'modern', 'neon', 'ubuntu',
                               'windows10', 'windows11', 'windows7', 'windows8', 'windowsxp'])
        for layout in ids:
            with self.subTest(layout=layout):
                start = layouts/layout/'icons/start.svg'
                self.assertTrue(start.is_file())
                self.assertIn('<svg', start.read_text())
                meta = (layouts/layout/'meta.toml').read_text()
                self.assertIn('name = "%s"' % layout, meta)
                rc = (layouts/layout/'openbox/rc.xml').read_text()
                theme = next(line.split('<name>', 1)[1].split('</name>', 1)[0]
                             for line in rc.splitlines() if '<name>UTN-' in line)
                self.assertTrue((themes/theme/'openbox-3/themerc').is_file())
                self.assertIn('<titleLayout>', rc)
                self.assertIn('<font>', rc)
                self.assertTrue((layouts/layout/'wallpaper.jpg').is_file())
                self.assertTrue((layouts/layout/'icons/apps/files.svg').is_file())
                panel = (layouts/layout/'lxqt/panel.conf').read_text()
                self.assertIn('[startmenu]', panel)
                self.assertIn('type=customcommand', panel)
                self.assertIn('icon=/usr/share/utn-os/icons/utn-logo.png', panel)
                self.assertIn('click=/usr/local/bin/utn-startmenu ' + layout, panel)
    def test_utn_visual_assets(self):
        root = ROOT/'iso/airootfs'
        self.assertTrue((root/'usr/local/bin/utn-startmenu').is_file())
        self.assertTrue((root/'usr/share/utn-os/icons/utn-logo.png').is_file())
        self.assertTrue((root/'usr/share/utn-os/wallpapers/utn-fondo.jpg').is_file())
        self.assertTrue((root/'usr/share/utn-os/splash.png').is_file())
        self.assertTrue((ROOT/'iso/syslinux/splash.png').is_file())
        for path in (root/'usr/share/utn-os/applications').glob('utn-*-*.desktop'):
            text = path.read_text()
            self.assertIn('[Desktop Entry]', text)
            self.assertIn('Icon=/usr/share/utn-os/layouts/', text)
    def test_reported_usability_fixes(self):
        root = ROOT/'iso/airootfs'
        logo = (root/'usr/share/utn-os/icons/utn-logo.png').read_bytes()
        self.assertEqual((root/'usr/share/pixmaps/utn-os.png').read_bytes(), logo)
        files = sorted((root/'usr/share/utn-os/applications').glob('*-files.desktop'))
        self.assertEqual(len(files), 11)
        for path in files:
            with self.subTest(desktop=path.name):
                self.assertIn('Exec=pcmanfm-qt --new-window %U', path.read_text())
        layout = (root/'usr/local/bin/utn-layout').read_text()
        self.assertIn('pgrep -x pcmanfm-qt', layout)
        self.assertIn('pcmanfm-qt --desktop --profile=lxqt', layout)
        panel = (root/'usr/share/utn-os/layouts/windows8/lxqt/panel.conf').read_text()
        self.assertIn('type=showdesktop', panel)
        self.assertIn('showDate=true', panel)
        self.assertIn('background-color=#1f1f1f', panel)
        startmenu = (root/'usr/local/bin/utn-startmenu').read_text()
        self.assertIn('self.fullscreen = layout == "windows8"', startmenu)
        self.assertIn('("installer", "Instalar UTN OS", ["/usr/local/bin/utn-installer"])', startmenu)

    def test_no_live_remote_login(self):
        root=ROOT/'iso/airootfs'
        self.assertFalse((root/'etc/systemd/system/multi-user.target.wants/sshd.service').is_symlink())
        conf=(root/'etc/ssh/sshd_config.d/00-utn.conf').read_text()
        self.assertIn('PermitRootLogin no',conf)
        self.assertIn('PermitEmptyPasswords no',conf)
        self.assertNotIn('ssh-ed25519',(root/'root/customize_airootfs.sh').read_text())
    def test_source_syntax(self):
        for p in (ROOT/'iso').rglob('*'):
            if not p.is_file() or p.is_symlink(): continue
            data=p.read_bytes()
            if data.startswith(b'#!/usr/bin/env python3') or p.suffix=='.py': ast.parse(data,filename=str(p))
            if data.startswith((b'#!/usr/bin/env bash',b'#!/bin/bash')):
                subprocess.run(['bash','-n',str(p)],check=True)

if __name__=='__main__': unittest.main()
