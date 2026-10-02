"""Incremental repository for readable task records, with previous-revision recovery."""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from threading import RLock


class RecordRepository:
    def __init__(self):
        self._cache = {}
        self._lock = RLock()
        self.issues = []

    def read(self, folder: Path):
        records, issues, retained = [], [], {}
        with self._lock:
            for path in sorted(folder.glob('*.md'), reverse=True):
                if path.name == 'relatorio_registros.md':
                    continue
                try:
                    stat = path.stat()
                    stamp = (stat.st_size, stat.st_mtime_ns)
                    cached = self._cache.get(str(path))
                    if cached and cached[0] == stamp:
                        record = cached[1]
                        warning = cached[2]
                        if warning:
                            issues.append(warning)
                    else:
                        record = None
                        warning = None
                        for source in (path, path.with_name(path.name + '.bak')):
                            try:
                                text = source.read_text(encoding='utf-8')
                                match = re.search(r'<!-- CODEX_MODEL_GATE_RECORD: (.*?) -->', text, re.S)
                                candidate = json.loads(match.group(1)) if match else None
                                if isinstance(candidate, dict) and all(
                                        field not in candidate or isinstance(candidate[field], list)
                                        for field in ('artifacts', 'attachments', 'conversation', 'turn_metrics')):
                                    record = candidate
                                    if source != path:
                                        warning = f'{path.name}: revisão anterior recuperada.'
                                        issues.append(warning)
                                    break
                            except (OSError, UnicodeError, ValueError):
                                continue
                        if record is None:
                            issues.append(f'{path.name}: metadados indisponíveis.')
                            continue
                    retained[str(path)] = (stamp, record, warning)
                    records.append({**copy.deepcopy(record), 'record_file': str(path)})
                except OSError as exc:
                    issues.append(f'{path.name}: {exc}')
            self._cache = retained
            self.issues = issues
        return records


REPOSITORY = RecordRepository()
