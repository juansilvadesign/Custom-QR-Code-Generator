# Vendored encoder provenance

`qrcodegen.py` is the Python port of Project Nayuki's QR Code generator. It is
vendored so terminal generation remains available without a network connection.

| Field | Recorded value |
| --- | --- |
| Upstream project | <https://github.com/nayuki/QR-Code-generator> |
| Upstream source | <https://github.com/nayuki/QR-Code-generator/blob/2c9044de6b049ca25cb3cd1649ed7e27aa055138/python/qrcodegen.py> |
| Repository commit checked | `2c9044de6b049ca25cb3cd1649ed7e27aa055138` (2025-01-23) |
| Last commit changing the Python source | `777682a64202fdb837b50e351b25b7ddb27852c4` (2025-01-04) |
| Local SHA-256 | `9f4ed1dd201dcb92b1bc0d6e14f46c754bcff0ce48580c5d7e8ace8f6926c8ef` |
| License | Project Nayuki MIT notice at the top of `qrcodegen.py` |
| Deliberate local modifications | None |

The Milestone C update restores the upstream license notice that was absent from
the previous vendored file and incorporates Nayuki's alignment-pattern spacing
fix from commit `777682a`. No application behavior is patched into the vendored
module.

## Update procedure

1. Choose an immutable upstream commit and download
   `python/qrcodegen.py` from that commit.
2. Verify the upstream repository, commit, source URL, license notice, and file
   diff. Do not mix application rendering or validation into the vendored file.
3. Replace the file byte-for-byte, update the commit and SHA-256 table above, and
   record the change in `CHANGELOG.md`.
4. Install `requirements-dev.txt` in a clean supported Python environment.
5. Run `python -m unittest discover -s tests -v`. This must include exact payload,
   SVG/XML, parity, all-ECL, capacity-boundary, version-32-or-larger, and
   independent ZXing decode coverage.
6. Run the manual device matrix in `docs/milestone-c/DEVICE_MATRIX.md`. Do not
   publish or tag an encoder update until both automated and representative
   real-device evidence pass.
7. Recompute the local checksum with `sha256sum qrcodegen.py` (or a platform
   equivalent), then have a maintainer review the provenance and full diff.
