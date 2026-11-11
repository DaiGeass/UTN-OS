#!/usr/bin/env bash
set -e

# Layout por defecto (el que tenga default = true en su meta.toml)
LAYOUT=/usr/share/utn-os/layouts/macos
for meta in /usr/share/utn-os/layouts/*/meta.toml; do
    if grep -q '^default[[:space:]]*=[[:space:]]*true' "$meta"; then
        LAYOUT=$(dirname "$meta")
        break
    fi
done

install -Dm644 -o 0 -g 0 "$LAYOUT/lxqt/panel.conf" /etc/xdg/lxqt/panel.conf
install -Dm644 -o 0 -g 0 "$LAYOUT/lxqt/lxqt.conf" /etc/xdg/lxqt/lxqt.conf
install -Dm644 -o 0 -g 0 "$LAYOUT/openbox/rc.xml" /etc/xdg/openbox/rc.xml
install -Dm644 -o 0 -g 0 "$LAYOUT/pcmanfm/settings.conf" /etc/xdg/pcmanfm-qt/lxqt/settings.conf
install -Dm644 -o 0 -g 0 "$LAYOUT/picom.conf" /etc/xdg/picom.conf
if [ -f "$LAYOUT/kvantum/kvantum.kvconfig" ]; then
    install -Dm644 -o 0 -g 0 "$LAYOUT/kvantum/kvantum.kvconfig" /etc/xdg/Kvantum/kvantum.kvconfig
fi

# El live no expone SSH ni instala claves de acceso remoto.
systemctl disable sshd.service
# El live debe completar el arranque aun sin conexión a un servidor NTP.
systemctl disable systemd-time-wait-sync.service

# Arranque live automático: escritorio LXQt con SDDM (autologin root en conf.d)
systemctl enable sddm 2>/dev/null || true

# Tema por defecto del live (verde+azul, modo oscuro)
install -Dm644 -o 0 -g 0 /dev/null /etc/utn-os/theme
printf 'dark\n' > /etc/utn-os/theme

# Iconos y accesos directos en escritorio (live) y skel (sistema instalado)
chmod +x /usr/share/applications/utn-os-installer.desktop \
         /usr/share/applications/utn-os-welcome.desktop
for f in /usr/share/applications/utn-os-installer.desktop \
         /usr/share/applications/utn-os-welcome.desktop \
         /usr/share/applications/qterminal.desktop \
         /usr/share/applications/pcmanfm-qt.desktop; do
    [ -f "$f" ] || continue
    install -m755 "$f" /root/Desktop/ || true
    install -m755 "$f" /etc/skel/Desktop/ || true
done

# Apariencia GTK + cursor uniformes (Breeze + Papirus + DMZ-White)
install -Dm644 -o 0 -g 0 /dev/null /etc/gtk-2.0/gtkrc-2.0
cat > /etc/gtk-2.0/gtkrc-2.0 <<'GTK2'
gtk-theme-name="Breeze"
gtk-icon-theme-name="Papirus"
gtk-cursor-theme-name="DMZ-White"
gtk-font-name="Noto Sans 10"
GTK2
install -Dm644 -o 0 -g 0 /dev/null /etc/gtk-3.0/settings.ini
cat > /etc/gtk-3.0/settings.ini <<'GTK3'
[Settings]
gtk-theme-name=Breeze
gtk-icon-theme-name=Papirus
gtk-cursor-theme-name=DMZ-White
gtk-font-name=Noto Sans 10
gtk-cursor-theme-size=24
GTK3

# Cursor por defecto de X11
install -Dm644 -o 0 -g 0 /dev/null /usr/share/icons/default/index.theme
printf '[Icon Theme]\nInherits=DMZ-White\n' > /usr/share/icons/default/index.theme

# xsettingsd: aplica tema/iconos/cursor a las apps GTK del live
install -Dm644 -o 0 -g 0 /dev/null /etc/xdg/xsettingsd/xsettingsd.conf
cat > /etc/xdg/xsettingsd/xsettingsd.conf <<'XSET'
Net/ThemeName "Breeze"
Net/IconThemeName "Papirus"
Gtk/CursorThemeName "DMZ-White"
Gtk/CursorThemeSize 24
XSET
install -Dm644 -o 0 -g 0 /dev/null /etc/xdg/autostart/utn-xsettingsd.desktop
cat > /etc/xdg/autostart/utn-xsettingsd.desktop <<'XDG'
[Desktop Entry]
Type=Application
Name=XSettingsd
Comment=Aplica tema e iconos al GTK
Exec=/usr/bin/xsettingsd
NoDisplay=true
X-LXQt-Need-Config=true
OnlyShowIn=LXQt;
XDG