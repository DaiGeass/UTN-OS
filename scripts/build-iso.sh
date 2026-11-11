#!/usr/bin/env bash
# Build only: never writes to a physical disk.
set -euo pipefail
repo_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
for command in mkarchiso pacman python3 git sha256sum; do
    if ! command -v "$command" >/dev/null 2>&1; then
        echo "Falta $command. Compilá en Arch Linux actualizado con archiso instalado." >&2
        exit 1
    fi
done
if (( EUID != 0 )); then
    echo "Ejecutá: sudo bash scripts/build-iso.sh (en una VM de compilación Arch)." >&2
    exit 1
fi
cd -- "$repo_dir"
python3 -m unittest discover -s tests -v
mkdir -p -- "$repo_dir/work" "$repo_dir/out"
build_dir="$(mktemp -d "$repo_dir/work/build.XXXXXX")"
release_dir="$(mktemp -d "$repo_dir/out/build.XXXXXX")"
# Conservamos work y el log en caso de fallo para permitir el diagnóstico.
{
    date -u '+build_started_utc=%Y-%m-%dT%H:%M:%SZ'
    git -c safe.directory="$repo_dir" rev-parse HEAD
    git -c safe.directory="$repo_dir" status --short
    pacman -Q archiso
    printf 'SOURCE_DATE_EPOCH=%s\n' "${SOURCE_DATE_EPOCH:-not_set}"
    printf 'build_directory=%s\n' "$build_dir"
} > "$release_dir/build-info.txt"
git -c safe.directory="$repo_dir" diff --binary HEAD > "$release_dir/source-changes.patch"
python3 - "$repo_dir" "$release_dir/source.tar.gz" <<'PY'
from pathlib import Path
import subprocess
import sys
import tarfile
root = Path(sys.argv[1])
names = subprocess.check_output(['git', '-c', f'safe.directory={root}', 'ls-files', '-z', '--cached', '--others', '--exclude-standard'], cwd=root)
with tarfile.open(sys.argv[2], 'w:gz', dereference=False) as archive:
    for name in sorted(set(names.decode().split('\0')) - {''}):
        path = root / name
        if path.exists() or path.is_symlink():
            archive.add(path, arcname='UTN-OS/' + name, recursive=False)
PY
mkarchiso -v -w "$build_dir" -o "$release_dir" "$repo_dir/iso" 2>&1 | tee "$release_dir/build.log"
shopt -s nullglob
images=("$release_dir"/*.iso)
if (( ${#images[@]} == 0 )); then
    echo "mkarchiso terminó sin generar una ISO." >&2
    exit 1
fi
for image in "${images[@]}"; do
    (
        cd -- "$release_dir"
        sha256sum -- "$(basename -- "$image")" > "$(basename -- "$image").sha256"
        sha256sum --check "$(basename -- "$image").sha256"
    )
done
(cd -- "$release_dir" && sha256sum source.tar.gz > source.tar.gz.sha256)
printf 'ISO, checksum, log y metadatos disponibles en: %s\n' "$release_dir"
printf 'Falta ejecutar la matriz de pruebas en docs/TESTING.md antes de publicar.\n'
