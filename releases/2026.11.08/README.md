# UTN OS 2026.11.08 — ISO x86_64

ISO educativa de UTN OS basada en Arch Linux x86_64, partida en trozos de 90 MiB
para poder publicarse en GitHub (límite de 100 MB por archivo).

## Contenido

- `utn-os-2026.11.08-x86_64.iso.part-00` ... `part-27` (28 partes, 2.589.917.184 bytes en total)
- `SHA256SUMS`: hashes de cada parte y del ISO reconstruido

Hash SHA-256 del ISO completo:

```text
54db1abd4e3a2ededc31f2655fdf6f214ae1cb8ef2eb816c0034f9720ece4733
```

## Reconstruir el ISO en Linux/macOS

```bash
cat utn-os-2026.11.08-x86_64.iso.part-* > utn-os-2026.11.08-x86_64.iso
sha256sum -c SHA256SUMS
```

Debe terminar con:

```text
utn-os-2026.11.08-x86_64.iso: OK
```

## Reconstruir el ISO en Windows (CMD)

```bat
copy /b utn-os-2026.11.08-x86_64.iso.part-00+utn-os-2026.11.08-x86_64.iso.part-01+utn-os-2026.11.08-x86_64.iso.part-02+utn-os-2026.11.08-x86_64.iso.part-03+utn-os-2026.11.08-x86_64.iso.part-04+utn-os-2026.11.08-x86_64.iso.part-05+utn-os-2026.11.08-x86_64.iso.part-06+utn-os-2026.11.08-x86_64.iso.part-07+utn-os-2026.11.08-x86_64.iso.part-08+utn-os-2026.11.08-x86_64.iso.part-09+utn-os-2026.11.08-x86_64.iso.part-10+utn-os-2026.11.08-x86_64.iso.part-11+utn-os-2026.11.08-x86_64.iso.part-12+utn-os-2026.11.08-x86_64.iso.part-13+utn-os-2026.11.08-x86_64.iso.part-14+utn-os-2026.11.08-x86_64.iso.part-15+utn-os-2026.11.08-x86_64.iso.part-16+utn-os-2026.11.08-x86_64.iso.part-17+utn-os-2026.11.08-x86_64.iso.part-18+utn-os-2026.11.08-x86_64.iso.part-19+utn-os-2026.11.08-x86_64.iso.part-20+utn-os-2026.11.08-x86_64.iso.part-21+utn-os-2026.11.08-x86_64.iso.part-22+utn-os-2026.11.08-x86_64.iso.part-23+utn-os-2026.11.08-x86_64.iso.part-24+utn-os-2026.11.08-x86_64.iso.part-25+utn-os-2026.11.08-x86_64.iso.part-26+utn-os-2026.11.08-x86_64.iso.part-27 utn-os-2026.11.08-x86_64.iso
```

Luego verifica el hash con `certutil -hashfile utn-os-2026.11.08-x86_64.iso SHA256`.

## Notas

- Arranque BIOS y UEFI validado en QEMU; no validado en hardware físico.
- No implementa Secure Boot.
- No hay reproducibilidad bit a bit.
- El ISO no está firmado con GPG; usa `SHA256SUMS` para verificar integridad.
