# UTN OS — Registro de cambios

## v2026.09.19 — "Frutiger Aero" (ISO `utn-os-2026.09.19-x86_64.iso`)

> Cambio de identidad completo: de un respin archiso genérico a **UTN OS** (marca UTN, tema
> verde→azul estilo Frutiger Aero). ISO verificada con `sha256sum` incluido.

### Instalador (`utn-installer`)
- **Nuevo paso "Extras" opcional** antes del resumen, con validación:
  - **Cifrado LUKS** (cryptsetup): formatea la partición raíz con `luks2`, la abre como
    `/dev/mapper/utnroot`, escribe `/etc/crypttab` + hook `encrypt` en mkinitcpio, pasa
    `cryptdevice=UUID=…:utnroot` a GRUB y cierra el mapper (`cryptsetup close`) al final.
    Requiere contraseña ≥ 8 caracteres.
  - **Firewall** nftables: plantilla con políticas `drop` en input/forward y
    `accept` en output, entrada permitida por lo establecido (activado con `systemctl enable nftables`).
  - **Octopi**: gestor de paquetes gráfico (instalado sólo si hay internet en el chroot).
  - **Plymouth**: pantalla de arranque con logo UTN; añade el hook `plymouth` y el
    servicio `plymouth-start` (requiere internet).
  - **Snapper**: snapshots automáticos btrfs (se valida que `/` sea btrfs, `snapper create-config`,
    timers `snapper-timeline`/`snapper-cleanup`).
  - **Actualizaciones**: `pacman -Syu` + regeneración de initramfs al finalizar (si hay internet).
- **Resumen ampliado**: ahora también muestra teclado/X11, zona horaria, idioma y la lista de
  extras elegidos.
- Página **Mac/minimum** con switch de fondo luminoso/oscuro funcional.

### Escritorio / tema
- **Identidad UTN**: nombre de ISO `utn-os-…`, distribuidor `UTN OS` (GRUB, splash, saludo),
  logo esfera de cristal verde→azul (`utn-os.svg`/`utn-os.png`).
- **Tema oscuro uniforme** con gradiente verde→azul en todas las apps LXQt (y modo claro clásico
  UTN) + **xsettingsd** aplicando tema de iconos, cursores y fuentes GTK/GTK2.
- Paquetes nuevos: `papirus-icon-theme`, `breeze-gtk`, `xcursor-themes`, `xsettingsd`,
  `breeze-icons`, `cryptsetup` (base).

### Layouts por sistema imitado
- **Ubuntu**: dock estilo Unity a la izquierda, panel superior.
- **macOS**: menubar arriba + dock abajo.
- **Windows 8/10/11/XP**: barra de tareas inferior, layout metro/glass/X por sistema.
- **ChromeOS**: shelf centrado; **WSL/mint/neon/macos-redone** con temas Kvantum variados
  (KvSimplicity, KvAdapta, KvRoughGlass, KvArc, KvDark…).

### Verificación
- ISO compilada con `mkarchiso` (compresión zstd, zstd nivel 15), checksum `sha256sum` incluido
  en `out/utn-os-2026.09.19-x86_64.iso.sha256` (verificado: `OK`).

## v– (anterior)
- Respin archlinux sin marca UTN. Reemplazado por la versión Frutiger Aero de esta fecha.
