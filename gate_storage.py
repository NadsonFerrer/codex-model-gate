"""Atomic local persistence and bounded archive extraction."""
from __future__ import annotations

import json
import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path, PurePosixPath
from threading import RLock

SETTINGS_LOCK = RLock()
MAX_ARCHIVE_FILES = 100_000
MAX_ARCHIVE_BYTES = 20 * 1024**3


def atomic_write_text(path: Path, text: str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=path.name + '.', suffix='.tmp', dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        if path.is_file():
            # Keep the preceding complete revision, without risking the final file.
            previous = path.read_bytes()
            backup = path.with_name(path.name + '.bak')
            bfd, bname = tempfile.mkstemp(dir=path.parent, prefix=backup.name)
            try:
                with os.fdopen(bfd, 'wb') as stream:
                    stream.write(previous)
                os.replace(bname, backup)
            finally:
                Path(bname).unlink(missing_ok=True)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def load_json(path: Path, expected_type, default):
    for candidate in (path, path.with_name(path.name + '.bak')):
        try:
            value = json.loads(candidate.read_text(encoding='utf-8'))
            if isinstance(value, expected_type):
                return value
        except (OSError, UnicodeError, ValueError):
            continue
    return default


@contextmanager
def atomic_archive(destination: Path):
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=destination.parent, suffix='.zip.tmp')
    os.close(fd)
    temporary = Path(name)
    try:
        yield temporary
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def safe_relative_path(value: str) -> PurePosixPath:
    raw = str(value).replace('\\', '/')
    path = PurePosixPath(raw)
    if (not raw or path.is_absolute() or not path.parts or
            any(p in {'', '.', '..'} for p in raw.split('/')) or
            any(':' in p or p.endswith((' ', '.')) or re.match(
                r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(?:\.|$)', p, re.I)
                for p in path.parts)):
        raise ValueError('O arquivo contém um caminho inválido para Windows.')
    return path


def confined_target(root: Path, relative: PurePosixPath) -> Path:
    target = root.joinpath(*relative.parts)
    try:
        target.resolve().relative_to(root.resolve())
    except (ValueError, OSError) as exc:
        raise ValueError('O destino está fora da pasta autorizada.') from exc
    return target


def validate_archive(archive) -> None:
    infos = archive.infolist()
    if len(infos) > MAX_ARCHIVE_FILES or sum(i.file_size for i in infos) > MAX_ARCHIVE_BYTES:
        raise ValueError('O arquivo excede os limites de importação (100 mil itens / 20 GiB).')
    seen = set()
    for info in infos:
        key = info.filename.replace('\\', '/').casefold()
        if key in seen:
            raise ValueError('O arquivo contém destinos duplicados.')
        seen.add(key)
        if (info.external_attr >> 16) & 0o170000 == 0o120000:
            raise ValueError('Links simbólicos não são permitidos no arquivo.')


def remap_paths(value, mappings: dict[str, str]):
    """Remap path prefixes in structured metadata, preserving prose and URLs."""
    if isinstance(value, dict):
        return {k: remap_paths(v, mappings) for k, v in value.items()}
    if isinstance(value, list):
        return [remap_paths(v, mappings) for v in value]
    if isinstance(value, str):
        folded = value.replace('\\', '/').rstrip('/')
        for old, new in sorted(mappings.items(), key=lambda pair: -len(pair[0])):
            prefix = old.replace('\\', '/').rstrip('/')
            if folded.casefold() == prefix.casefold():
                return str(Path(new))
            if folded.casefold().startswith(prefix.casefold() + '/'):
                return str(Path(new).joinpath(*folded[len(prefix)+1:].split('/')))
    return value
