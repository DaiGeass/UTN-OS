#!/usr/bin/env bash
set -e

LAYOUT=/usr/share/utn-os/layouts/modern

install -Dm644 -o 0 -g 0 "$LAYOUT/lxqt/panel.conf" /etc/xdg/lxqt/panel.conf
install -Dm644 -o 0 -g 0 "$LAYOUT/lxqt/lxqt.conf" /etc/xdg/lxqt/lxqt.conf
install -Dm644 -o 0 -g 0 "$LAYOUT/openbox/rc.xml" /etc/xdg/openbox/rc.xml
install -Dm644 -o 0 -g 0 "$LAYOUT/pcmanfm/settings.conf" /etc/xdg/pcmanfm/lxqt/settings.conf