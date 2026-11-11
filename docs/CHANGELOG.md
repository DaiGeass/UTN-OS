# UTN OS — Registro de cambios

## Sin publicar — correcciones de instalación y QA

- Corrección de usabilidad del 8 de noviembre: el explorador de archivos abre una ventana nueva (`pcmanfm-qt --new-window`) desde el menú y desde los accesos rápidos de los once layouts.
- `utn-layout` inicia `pcmanfm-qt --desktop` si el escritorio no está activo, antes de aplicar el fondo; el fondo UTN queda visible sin intervención manual.
- Windows 8 rediseñado como pantalla de inicio fullscreen con mosaicos 160×160, colores Metro, buscador, Charms laterales y acceso “Instalar UTN OS”.
- Barra de tareas de Windows 8 con `showdesktop`, fecha visible y fondo `#1f1f1f`.
- El icono de INSTALAR UTN OS usa `UTNLOGO` mediante `/usr/share/pixmaps/utn-os.png`.
- ISO `utn-os-2026.11.08-x86_64.iso` reconstruida sobre la base `utn-os-2026.11.05-x86_64.iso`; SFS y arranque híbrido verificados, con 37 pruebas de regresión aprobadas.
- Identidad visual: `UTNFONDO` como fondo global, `UTNLOGO` en el botón de menú y `UTNFONDOEFI` en el menú BIOS; iconos de aplicaciones propios para los once layouts.
- Menú de inicio PyQt5 por layout (`utn-startmenu`) con lista o mosaico, búsqueda, instalación y apagado; abierto desde el icono UTN del panel. Probado en BIOS (once layouts) y en UEFI (Windows 7).
- Fondos por layout actualizados en PCManFM-Qt; ISO `utn-os-2026.11.07` repack con SFS verificado y 36 pruebas de regresión aprobadas.
- ISO `utn-os-2026.11.07-x86_64.iso`: repack de layouts sobre la base `utn-os-2026.11.05-x86_64.iso`, con SquashFS regenerado y arranque híbrido BIOS/UEFI verificado.
- QA de layouts en BIOS: los once layouts aplican el tema Openbox esperado, un solo panel y el color de panel declarado; fondos de escritorio capturados. En UEFI se verificó Windows 7.
- Once layouts con identidad visual completa: temas Openbox `UTN-*`, colores/tipografías de ventana, `titleLayout`, iconos de inicio SVG y paneles/plugins específicos por sistema.
- Nuevo layout **Windows 7** (Aero Glass, taskbar oscura, menú Inicio y aurora azul) y Windows XP/8/10/11 diferenciados entre sí.
- Arranque del panel más rápido: menú principal nativo en layouts Windows/ChromeOS en lugar de exploración de `fancymenu`, menos plugins innecesarios y reinicio único del panel al aplicar un layout.
- macOS con menubar claro y dock, Ubuntu con dock izquierdo + barra superior, ChromeOS con shelf claro, Moderno con barra superior + dock y Neon/Frutiger con decoración propia.
- Pruebas de regresión ampliadas a once layouts, iconos, temas Openbox y referencias de panel.
- Configuración privada en `/var/tmp` compatible con arch-chroot; machine-id vacío para conservar la selección de servicios al primer arranque.
- Esperas de nsresourced y swap adaptadas a la lentitud observada en emulación, sin desactivar restricciones BPF.
- Acceso SDDM por software, fondo PCManFM-Qt en modo zoom y mensaje de consola del sistema instalado corregidos.

- Corregida la lectura de progreso rsync, selección de layouts y navegación ante errores.
- Validación de espacio y cuentas reservadas antes de borrar; confirmación de root/LUKS y autologin opcional.
- Directorios del destino y kernel preparados explícitamente; fstab/initramfs/GRUB verificados sin ocultar errores.
- Limpieza de procesos, swap, montajes, mapper y secretos; registro exportable con contraseñas ocultas.
- Retirados SSH de depuración y clave pública fija. Extras offline con avisos; Octopi retirado del asistente.
- Firefox, LibreOffice, Git, base-devel y GDB incluidos en el perfil.
- Script de compilación con checksum, metadatos y manifiesto de paquetes; pruebas de regresión y matriz de VM.
- Paneles LXQt corregidos en todos los layouts, fondo PCManFM-Qt en su ruta real y consejo de bienvenida sin texto recortado.
- Marca de casillas en PNG y dependencia qt5-svg explícita para previsualizar los layouts con PyQt5.
- Picom omitido en máquinas virtuales para evitar bloqueo gráfico con GLX por software.
- Keyring de pacman inicializado offline en el destino y agentes GPG cerrados antes de desmontar.
- Compresión zstd ajustada para facilitar compilación/arranque en emulación; arranque offline sin espera indefinida de NTP.
- Compilación preliminar y arranque BIOS completados; consultar el informe que acompaña la ISO para los resultados de instalación/reinicio.

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
