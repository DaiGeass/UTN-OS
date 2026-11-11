# UTN OS

Distribución educativa basada en **Arch Linux x86_64**, con escritorio **LXQt**, layouts personalizados, bienvenida e instalador gráfico propios. Utiliza el kernel Linux y los paquetes de Arch; este repositorio no implementa un kernel desde cero.

El proyecto está en desarrollo. Las correcciones de lógica tienen pruebas automatizadas; la instalación completa y el arranque deben comprobarse con la ISO compilada antes de distribuirla.

## Componentes

- `iso/`: perfil de archiso, paquetes, servicios y archivos del sistema live.
- `iso/airootfs/usr/local/bin/utn-installer`: asistente de instalación de disco completo.
- `iso/airootfs/usr/local/bin/utn-welcome`: bienvenida y selector de layouts.
- `iso/airootfs/usr/local/bin/utn-startmenu`: menú de inicio PyQt5 con estilo, iconos y aplicaciones por layout.
- `iso/airootfs/usr/share/utn-os/layouts/`: once apariencias de escritorio, cada una con panel, plugins, iconos, fondo y decoración de ventanas propios (Windows XP/7/8/10/11, macOS, Ubuntu, ChromeOS, Moderno, Frutiger Aero y Neon).
- `iso/airootfs/usr/share/utn-os/wallpapers/` e `icons/`: fondo global e icono UTN usados por el live y los layouts.
- `scripts/build-iso.sh`: compilación, checksum SHA-256 y registro de versiones.
- `tests/`: pruebas de regresión sin acceso real a discos ni instalación de paquetes.
- `docs/TESTING.md`: matriz de pruebas con VM y límites conocidos.

## Desarrollo y pruebas

```bash
git clone https://github.com/DaiGeass/UTN-OS.git
cd UTN-OS
python3 -m unittest discover -s tests -v
```

Las pruebas requieren Python 3.11 o posterior y Bash. Simulan Qt y los comandos del sistema; no sustituyen el arranque de una ISO. No requieren root ni PyQt5.

## Compilar la ISO

Usar una VM de compilación **Arch Linux x86_64 actualizada**, conexión a internet y al menos 30 GiB libres para paquetes, archivos de trabajo e imagen. Se recomiendan 4 GiB de RAM o más. Las necesidades concretas dependen de las versiones de los paquetes.

```bash
sudo pacman -Syu --needed archiso git python
sudo bash scripts/build-iso.sh
```

Cada ejecución crea directorios nuevos en `work/` y `out/`. El resultado incluye:

- Imagen `.iso` y archivo `.iso.sha256`, verificado al finalizar.
- `build.log`, versión de archiso, revisión Git y estado del checkout.
- `source-changes.patch` y `source.tar.gz` con el código usado, incluidos archivos nuevos no ignorados por Git, más checksum del archivo fuente.
- Dentro de la ISO, `/usr/share/utn-os/build-packages.txt` registra las versiones instaladas durante la compilación.

El script no publica archivos ni escribe en un USB o disco físico. No instala archiso automáticamente. Conserva los archivos de trabajo cuando falla.

La receta registra los insumos, pero **no promete imágenes idénticas bit a bit**: los repositorios de Arch cambian. Para reproducibilidad estricta se debe fijar un snapshot de Arch Linux Archive, la versión de archiso y `SOURCE_DATE_EPOCH`, y comparar dos compilaciones.

## Instalación y aplicaciones

El instalador borra **todo el disco seleccionado**. No ofrece dual boot ni particionado manual. Probar primero con un disco virtual nuevo de 32 GiB o más; el asistente calcula el mínimo según el sistema copiado, espacio de margen, EFI y swap.

La instalación base funciona sin internet. El perfil incluye Firefox, LibreOffice, Git, herramientas de compilación (`base-devel`) y GDB, además del escritorio. Los extras descargables están desactivados por defecto. Si no hay conexión se omiten con un aviso visible; si una operación de paquetes o arranque falla, la instalación se marca como fallida.

Octopi se retiró del asistente porque es un paquete del AUR y no está disponible mediante el `pacman -S octopi` original con los repositorios configurados. No se compilan paquetes AUR automáticamente como root. La gestión de paquetes sigue disponible mediante pacman. Referencia: [ArchWiki — AUR helpers](https://wiki.archlinux.org/title/AUR_helpers).

## Acceso y recuperación

- El live conserva autologin local de root para el entorno de instalación. **SSH está deshabilitado**, no se incorporan claves públicas de terceros y la configuración prohíbe acceso remoto de root y contraseñas vacías.
- El sistema instalado crea un usuario normal; autologin es opcional y está desactivado inicialmente.
- El instalador permite guardar el registro tanto durante el proceso como al finalizar. Las contraseñas introducidas se ocultan en los mensajes y se eliminan los archivos temporales después de utilizarlos.
- Si falla la instalación, se intenta detener la copia, desactivar la swap creada, desmontar el destino y cerrar el mapper LUKS. El log conserva cualquier fallo de limpieza. Si no se pueden liberar los recursos, reiniciar el live antes de reintentar.
- Con LUKS se exige desactivar swap: esta versión todavía no implementa swap cifrada. El volumen utiliza LUKS2 con PBKDF2 para compatibilidad de GRUB con `/boot` cifrado. Puede pedir la contraseña más de una vez durante el arranque; comprobar el teclado en la VM.

## Autores y licencia

Autores del proyecto: DaiGeass y ZZERO. La licencia del código propio sigue pendiente de definición por sus autores. Arch Linux, Linux, LXQt y las demás dependencias mantienen sus respectivas licencias.
