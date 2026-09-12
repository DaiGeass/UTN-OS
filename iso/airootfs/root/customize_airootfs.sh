#!/usr/bin/env bash
set -e

LAYOUT=/usr/share/utn-os/layouts/modern
ROOT_CONF=/root/.config

install -Dm644 -o 0 -g 0 "$LAYOUT/lxqt/panel.conf" /etc/xdg/lxqt/panel.conf
install -Dm644 -o 0 -g 0 "$LAYOUT/lxqt/lxqt.conf" /etc/xdg/lxqt/lxqt.conf
install -Dm644 -o 0 -g 0 "$LAYOUT/openbox/rc.xml" /etc/xdg/openbox/rc.xml
install -Dm644 -o 0 -g 0 "$LAYOUT/pcmanfm/settings.conf" /etc/xdg/pcmanfm/lxqt/settings.conf
install -Dm644 -o 0 -g 0 "$LAYOUT/picom.conf" "$ROOT_CONF/picom.conf"
install -Dm644 -o 0 -g 0 "$LAYOUT/kvantum/kvantum.kvconfig" "$ROOT_CONF/Kvantum/kvantum.kvconfig"
install -Dm644 -o 0 -g 0 "$LAYOUT/lxqt/panel.conf" "$ROOT_CONF/lxqt/panel.conf"
install -Dm644 -o 0 -g 0 "$LAYOUT/lxqt/lxqt.conf" "$ROOT_CONF/lxqt/lxqt.conf"

install -Dm644 -o 0 -g 0 /dev/null /etc/xdg/autostart/picom.desktop
printf '[Desktop Entry]\nType=Application\nName=picom\nExec=/usr/bin/picom --config /root/.config/picom.conf\nX-GNOME-Autostart-enabled=true\n' > /etc/xdg/autostart/picom.desktop