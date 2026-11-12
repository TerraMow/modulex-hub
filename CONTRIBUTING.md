# Contributing to TerraMow ModuleX Hub

## Feedback

We welcome model or drawing questions, viewing problems, requests for reference
information, accessory ideas, and documentation corrections. Use the
[feedback form](https://github.com/TerraMow/modulex-hub/issues/new/choose) and
include the snapshot date, filename, and application if relevant. Screenshots
or sketches are optional. A working module is not needed to contribute an idea.

## Pull Requests

Describe what changed and why. Check relative links and keep public-facing
documentation and issue forms in English. Distinguish the published mounting
references from validated manufacturing and integration specifications.

Only submit files you have the right to contribute under GPL-3.0-only. The
repository and mechanical package use [GPL-3.0](LICENSE); see the
[license scope](LICENSES/README.md).

## Mechanical File Updates

Keep the STEP ZIP in `mechanical/step/`, the rendering PDF in
`mechanical/previews/`, and the engineering PDF in `mechanical/drawings/`.
Store the model as a ZIP containing one STEP file. Record its extracted filename,
byte count, and SHA-256 in the manifest's `contained_file` entry. Preserve its
geometry when normalizing public names.

Check PDF titles, author fields, XMP, and other metadata for internal names
before adding files. Preserve drawing content and compare PDF renderings before
and after any metadata cleanup. Replace the PNG previews in `assets/` with
images rendered from the current PDFs.

When files change, update the snapshot, paths, byte counts, and SHA-256 values
in `mechanical/manifest.json`, and update the relevant READMEs, the changelog,
and `docs/release-notes/<release-tag>.md`. The manifest must identify the exact
files intended for the same release.

## Prepare the Preview Package

Python 3 is sufficient; the script uses only the standard library and packages
the reviewed files already in `mechanical/`.

From the repository root:

```bash
python3 scripts/prepare-preview.py
(cd mechanical && sha256sum -c SHA256SUMS.txt)
```

The script checks all three reference files against the manifest, updates
`mechanical/SHA256SUMS.txt`, and writes the following to
`release-assets/preview-2026-11-11/`:

- Copies of the STEP ZIP and both PDFs
- `terramow-x-expansion-bay-preview-2026-11-11.zip`
- `SHA256SUMS.txt` and `FILE-MANIFEST.json`
- `PREVIEW-NOTES.md`, `LICENSE`, `LICENSE-NOTICE.md`, and `RELEASE-NOTES.md`

Generated packages and incoming source files under `release-assets/` are
ignored by Git. The release ZIP contains the model ZIP, both PDFs, preview notes, and the license
text and notice. Rebuild after changing any included document.

To verify the generated files:

```bash
cd release-assets/preview-2026-11-11
sha256sum -c SHA256SUMS.txt
```

For a GitHub release, use `preview-2026-11-11`, target the reviewed commit on
`master`, and select **Set as a pre-release**. Use `RELEASE-NOTES.md` for the
description and attach the ZIP and `SHA256SUMS.txt`.
