#!/usr/bin/env python3
"""Verify the repository's mechanical files and build the preview release package."""

import hashlib
import io
import json
from pathlib import Path
import shutil
import zipfile


def main():
    root = Path(__file__).resolve().parent.parent
    manifest = json.loads((root / 'mechanical/manifest.json').read_text())
    snapshot = manifest['snapshot']
    output = root / 'release-assets' / manifest['release_tag']
    archive = output / manifest['archive']
    files = []
    repository_checksums = []

    # Verify all source files first to avoid mixing models and drawings from different snapshots.
    for item in manifest['files']:
        source = root / item['path']
        content = source.read_bytes()
        checksum = hashlib.sha256(content).hexdigest()
        if len(content) != item['bytes'] or checksum != item['sha256']:
            raise SystemExit(f"File does not match the release manifest; check its revision: {source.name}")
        if item['role'] == 'step':
            # Verify both the model archive and the extracted STEP to ensure consistent model content.
            contained = item['contained_file']
            with zipfile.ZipFile(io.BytesIO(content)) as model_zip:
                if model_zip.namelist() != [contained['name']] or model_zip.testzip() is not None:
                    raise SystemExit('STEP ZIP contents do not match the manifest')
                model = model_zip.read(contained['name'])
            if len(model) != contained['bytes'] or hashlib.sha256(model).hexdigest() != contained['sha256']:
                raise SystemExit('Extracted STEP does not match the manifest')
        files.append((source.name, content))
        relative = source.relative_to(root / 'mechanical').as_posix()
        repository_checksums.append(f'{checksum}  {relative}\n')

    notes = (root / 'docs/release-notes' / f"{manifest['release_tag']}.md").read_bytes()
    license_text = (root / 'LICENSE').read_bytes()
    license_notice = (root / 'LICENSES/README.md').read_bytes().replace(b'(../LICENSE)', b'(LICENSE)')
    entries = files + [
        ('PREVIEW-NOTES.md', notes),
        ('LICENSE', license_text),
        ('LICENSE-NOTICE.md', license_notice),
    ]
    output.mkdir(parents=True, exist_ok=True)

    # Fix timestamps and permissions for reproducible builds with the same inputs and compression environment.
    stamp = tuple(map(int, snapshot.split('-'))) + (0, 0, 0)
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as bundle:
        for name, content in entries:
            entry = zipfile.ZipInfo(name, date_time=stamp)
            entry.create_system = 3
            entry.external_attr = 0o100644 << 16
            # Store the already compressed model ZIP without recompression.
            entry.compress_type = zipfile.ZIP_STORED if name.endswith('.zip') else zipfile.ZIP_DEFLATED
            bundle.writestr(entry, content, compresslevel=6)

    # Write individual file copies for checking the download package and extracted files.
    checksums = [f"{hashlib.sha256(archive.read_bytes()).hexdigest()}  {archive.name}\n"]
    for name, content in entries:
        (output / name).write_bytes(content)
        checksums.append(f'{hashlib.sha256(content).hexdigest()}  {name}\n')
    (output / 'SHA256SUMS.txt').write_text(''.join(checksums), encoding='utf-8')
    (output / 'RELEASE-NOTES.md').write_bytes(notes)
    (root / 'mechanical/SHA256SUMS.txt').write_text(''.join(repository_checksums), encoding='utf-8')
    shutil.copyfile(root / 'mechanical/manifest.json', output / 'FILE-MANIFEST.json')
    print(f'Release assets directory: {output}')
    print(f'ZIP size: {archive.stat().st_size:,} bytes')
    print('Generated STEP ZIP, two PDFs, combined ZIP, checksum lists, and release notes.')


if __name__ == '__main__':
    main()
