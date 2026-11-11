# Verificación de UTN OS

## Estado de esta revisión

La compilación preliminar con archiso 92 terminó y su SHA-256 se verificó. El live arrancó en BIOS mediante QEMU TCG. La prueba real detectó problemas de configuración del panel, ruta de PCManFM-Qt y compositor GLX en VM; están corregidos en esta revisión. La instalación offline y la reconstrucción con esos cambios se están verificando: consultar el informe de ejecución que acompaña la ISO para los resultados finales.

Pasaron 37 pruebas de regresión de lógica/sintaxis con procesos y widgets simulados. La prueba con PyQt5 5.15.11 real en plataforma offscreen se ejecuta en un entorno con PyQt5 instalado: siete páginas a 1024×768, once layouts, recuperación tras error, finalización, exportación del registro, bienvenida y retorno de getItem. Estas pruebas no sustituyen el reinicio del sistema instalado. En la ISO del 8 de noviembre se abrieron los once menús de inicio en BIOS; Windows 8 se capturó fullscreen, se comprobó la apertura real de Archivos desde su mosaico y desde el acceso rápido del panel, y se verificó que `utn-layout` inicia el escritorio y pinta el fondo UTN en los once layouts. En UEFI se comprobó el escritorio Windows 8, el menú fullscreen y la apertura de Archivos. Evidencia en `evidence/startmenu-qa-2026.11.08/`, `evidence/wallpapers-2026.11.08/`, `evidence/uefi-startmenu-windows8-2026.11.08.png` y `evidence/uefi-files-window-2026.11.08.png`.

```bash
python3 -m unittest discover -s tests -v
```

Para repetir la prueba de interfaz en un entorno con PyQt5 instalado:

```bash
QT_QPA_PLATFORM=offscreen python3 tests/smoke_gui.py
```

La suite cubre lectura de progreso CR/LF, errores de copia y timeout, creación de directorios y permisos de secretos, generación de fstab, errores de initramfs, limpieza tras fallo, avance por etapas, capacidad de disco, cuentas reservadas, selección/cancelación de layouts y ausencia de acceso SSH de depuración.

## Pruebas en máquina virtual

Crear una VM nueva con 4 GiB de RAM y disco virtual de 32 GiB o más. No pasar discos físicos del host. Usar una VM BIOS y otra UEFI con Secure Boot desactivado; Secure Boot no está implementado ni validado por este proyecto.

| Caso | Pasos | Resultado requerido | Estado |
|---|---|---|---|
| Compilación | Ejecutar `scripts/build-iso.sh` en Arch actualizado | ISO generada, checksum OK y log sin errores | Pendiente |
| Arranque BIOS y UEFI | Arrancar la ISO en ambas VMs | Escritorio, bienvenida e instalador operativos | Pendiente |
| Base offline | Desconectar red; instalar ext4 sin extras; expulsar ISO y reiniciar | Arranca el disco instalado y permite iniciar sesión | Pendiente |
| Aplicaciones | Abrir Firefox, LibreOffice y terminal; probar Git/GCC/GDB | Aplicaciones disponibles sin descargar paquetes | Pendiente |
| Extras online | Seleccionar Plymouth y actualizaciones | Resultado real en log, initramfs válido y reinicio correcto | Pendiente |
| Extras offline | Seleccionar extras sin red | Aviso de omisión, instalación base válida, sin hooks inexistentes | Pendiente |
| LUKS | Desactivar swap; confirmar contraseña; instalar y reiniciar | GRUB y sistema desbloquean la raíz con el teclado correcto | Pendiente |
| btrfs/Snapper | Seleccionar btrfs y Snapper con red | Crear y listar snapshot; documentar recuperación | Pendiente |
| Validaciones | Disco pequeño, ocupado, sólo lectura y desconectado | Rechazo antes de borrar datos | Pendiente |
| Error intermedio | En VM descartable, provocar fallo de copia/configuración | Log exportable, recursos liberados o error explícito de limpieza | Pendiente |
| Layouts | Elegir cada una de las once opciones; cancelar | Se aplica la seleccionada, cambian panel/ventanas/iconos; cancelar conserva el estado | Pendiente |
| Usuario | Probar root, nombre existente, contraseñas distintas | Rechazo claro; usuario válido obtiene sesión normal | Pendiente |
| Acceso remoto | Revisar SSH del live y del instalado | Servicio deshabilitado, sin clave prefijada y sin login remoto de root | Pendiente |
| Hardware/GUI | Red, DNS, sonido, suspensión, 1024×768 y HiDPI | Funcionamiento real y controles accesibles | Pendiente |

Para registrar cada ejecución: guardar checksum de ISO, firmware de VM, RAM/disco, opciones elegidas, resultado, log y captura del fallo si existe. El éxito del instalador comprueba archivos de arranque, pero la aceptación requiere reiniciar sin la ISO.

## Correcciones y límites

- Copia rsync corregida y proceso hijo recogido tanto al terminar como al fallar.
- Directorios del destino creados antes del chroot; kernel restaurado desde el live.
- fstab, initramfs, GRUB y limpieza deben terminar correctamente para mostrar éxito.
- Espacio mínimo calculado para todo el sistema, con EFI, swap y margen.
- Secretos temporales privados en `/var/tmp` (visible dentro de `arch-chroot`), eliminados en caminos de éxito/error.
- `machine-id` vacío en el destino para generar una identidad propia sin reactivar servicios por presets de primer arranque.
- Greeter SDDM por software y modos de fondo compatibles con PCManFM-Qt.
- Mayor margen de arranque de nsresourced en VMs y detección de swap durante cinco minutos; swap no impide el arranque si falta.
- Progreso vinculado a las etapas reales; navegación y exportación del registro tras fallos.
- Selección de layouts corregida, incluyendo cancelación y una sola opción.
- Contraseñas de root/LUKS confirmadas, nombres reservados rechazados, autologin opcional.
- Teclado de consola latinoamericano `la-latin1`; campo de prueba de teclado X11.
- SSH de depuración y clave pública fija retirados.
- Nuevas aplicaciones incluidas en el perfil; registrar el tamaño y consumo de cada ISO en su informe de ejecución.

No implementado: particionado manual/dual boot, Secure Boot, swap cifrada, restauración gráfica de snapshots ni una compilación estrictamente reproducible con paquetes fijados. La compatibilidad de cada filesystem ofrecido y el cifrado se debe validar en ambos modos de firmware.
