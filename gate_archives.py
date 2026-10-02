"""Portable task packages and migration-aware backups, including legacy readers."""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import uuid
import zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath

from gate_storage import (atomic_archive, atomic_write_text, confined_target,
                          remap_paths, safe_relative_path, validate_archive)


def _gate():
    import codex_model_gate
    return codex_model_gate


def _metadata_bytes(archive, name, limit=16 * 1024**2):
    if archive.getinfo(name).file_size > limit:
        raise ValueError('Os metadados do arquivo excedem o limite de leitura.')
    return archive.read(name)


def record_metadata(text: str) -> dict:
    match = re.search(r'<!-- CODEX_MODEL_GATE_RECORD: (.*?) -->', text, re.S)
    if not match:
        raise ValueError('O registro não contém metadados válidos.')
    value = json.loads(match.group(1))
    if not isinstance(value, dict):
        raise ValueError('Os metadados precisam ser um objeto.')
    for field in ('artifacts', 'attachments', 'conversation', 'turn_metrics'):
        if field in value and not isinstance(value[field], list):
            raise ValueError(f'Campo inválido no registro: {field}.')
    return value


def _workspace_files(workspace):
    for path in workspace.rglob('*'):
        if not path.is_file():
            continue
        relative = path.relative_to(workspace)
        if '.codex-model-gate' in relative.parts and 'anexos' not in relative.parts:
            continue
        if path.is_symlink() or not _gate()._path_is_within(path, workspace):
            raise ValueError('A tarefa contém um arquivo fora da pasta autorizada.')
        yield path, relative.as_posix()


def export_task_package(record: dict, destination: Path) -> Path:
    g = _gate()
    workspace = Path(str(record.get('project_folder') or '')).resolve()
    record_path = Path(str(record.get('record_file') or '')).resolve()
    if not record.get('project_folder') or not workspace.is_dir() or not record_path.is_file():
        raise OSError('O registro ou a pasta da tarefa não está disponível.')
    target = destination.expanduser().resolve().with_suffix('.gate')
    if g._path_is_within(target, workspace):
        raise ValueError('Salve o pacote fora da pasta da tarefa.')
    payload = record_metadata(record_path.read_text(encoding='utf-8'))
    payload['artifacts'] = [Path(p).resolve().relative_to(workspace).as_posix()
                            for p in payload.get('artifacts', []) if g._path_is_within(Path(p), workspace)]
    payload['project_folder'] = '.'
    payload['session_id'] = ''
    payload.pop('record_file', None)
    payload['attachments'] = [dict(a, original='') for a in payload.get('attachments', [])
                              if isinstance(a, dict) and a.get('active', True)]
    with atomic_archive(target) as temporary, zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as archive:
        archive.writestr('manifest.json', json.dumps({'format': g.GATE_PACKAGE_FORMAT,
                          'schema_version': 2, 'exported_at': datetime.now().astimezone().isoformat(),
                          'record': 'record.md', 'workspace': 'workspace', 'session_transferable': False}))
        archive.writestr('record.md', g._record_markdown(payload))
        for path, relative in _workspace_files(workspace):
            archive.write(path, 'workspace/' + relative)
    return target


def import_task_package(package: Path, projects_root: Path) -> dict:
    g = _gate()
    source = package.expanduser().resolve()
    if not source.is_file() or source.suffix.lower() != '.gate':
        raise ValueError('Escolha um pacote .gate válido.')
    workspace = None
    try:
        with zipfile.ZipFile(source) as archive:
            validate_archive(archive)
            try:
                manifest = json.loads(_metadata_bytes(archive, 'manifest.json'))
                record = record_metadata(_metadata_bytes(archive, 'record.md').decode('utf-8'))
            except (KeyError, UnicodeError, ValueError) as exc:
                raise ValueError('O pacote .gate está inválido.') from exc
            if not isinstance(manifest, dict) or manifest.get('format') != g.GATE_PACKAGE_FORMAT:
                raise ValueError('O pacote não é compatível com esta versão.')
            entries = []
            for info in archive.infolist():
                if info.is_dir():
                    continue
                name = safe_relative_path(info.filename)
                if name.parts[0] == 'workspace':
                    relative = safe_relative_path('/'.join(name.parts[1:]))
                    if '.codex-model-gate' in relative.parts and 'anexos' not in relative.parts:
                        continue
                    entries.append((info, relative))
            workspace = g.execution_workspace(projects_root, uuid.uuid4().hex, str(record.get('task') or 'importada'))
            for info, relative in entries:
                target = confined_target(workspace, relative)
                target.parent.mkdir(parents=True, exist_ok=True)
                with archive.open(info) as origin, target.open('wb') as output:
                    shutil.copyfileobj(origin, output)
        old = str(record.get('project_folder') or '')
        artifacts = []
        for value in record.get('artifacts', []):
            try:
                rel = (Path(value).relative_to(Path(old)).as_posix()
                       if Path(value).is_absolute() and old not in {'', '.'} else str(value))
                target = confined_target(workspace, safe_relative_path(rel))
                if target.is_file():
                    artifacts.append(str(target))
            except (ValueError, TypeError):
                continue
        record['artifacts'] = artifacts
        for attachment in record.get('attachments', []):
            if not isinstance(attachment, dict):
                continue
            attachment['original'] = ''
            try:
                target = confined_target(workspace, safe_relative_path(attachment.get('staged', '')))
                attachment['active'] = bool(attachment.get('active', True) and target.is_file())
            except ValueError:
                attachment['active'] = False
        record.update(id=uuid.uuid4().hex, project_folder=str(workspace), session_id='',
                      imported_from_package=source.name, status='Importada — pronta para nova conversa',
                      finished_at=datetime.now().astimezone().isoformat(timespec='seconds'))
        record.pop('record_file', None)
        record['record_file'] = str(g.write_execution_record(record))
        return record
    except zipfile.BadZipFile as exc:
        if workspace and g._path_is_within(workspace, projects_root):
            shutil.rmtree(workspace)
        raise ValueError('O pacote não é um ZIP válido.') from exc
    except Exception:
        # Only an exclusively created temporary workspace can be rolled back.
        if workspace and g._path_is_within(workspace, projects_root):
            shutil.rmtree(workspace)
        raise


def create_data_backup(destination: Path) -> Path:
    g = _gate()
    data = g.app_data_dir().resolve()
    target = destination.expanduser().resolve()
    if g._path_is_within(target, data):
        raise ValueError('Salve o backup fora da pasta de dados do Gate.')
    workspaces = {str(r.get('project_folder')) for r in g.read_execution_records() if r.get('project_folder')}
    workspaces.update(g.load_app_settings().get('managed_workspaces', []))
    external = [Path(p).resolve() for p in sorted(workspaces) if Path(p).is_dir() and not g._path_is_within(Path(p), data)]
    if any(g._path_is_within(target, p) for p in external):
        raise ValueError('Salve o backup fora das pastas de tarefa incluídas.')
    sources = []
    for category in ('projetos', 'skills', 'registro'):
        folder = data / category
        if folder.is_dir():
            for path in sorted(folder.rglob('*')):
                if not path.is_file() or path.suffix == '.bak':
                    continue
                if path.is_symlink() or not g._path_is_within(path, data):
                    raise ValueError('O backup contém um link para fora da pasta de dados.')
                if '.codex-model-gate' in path.parts and path.name == 'continuation.json':
                    continue
                sources.append((path, path.relative_to(data).as_posix()))
    for name in ('settings.json', 'history.json'):
        if (data / name).is_file():
            sources.append((data / name, name))
    for folder in external:
        group = 'externo-' + hashlib.sha256(str(folder).encode()).hexdigest()[:12]
        for path, relative in _workspace_files(folder):
            sources.append((path, f'projetos/{group}/{relative}'))
    files, numbers = [], {}
    with atomic_archive(target) as temporary, zipfile.ZipFile(temporary, 'w', zipfile.ZIP_DEFLATED) as archive:
        for path, relative in sources:
            category = relative.split('/')[0]
            if category in {'settings.json', 'history.json'}:
                member = 'c/' + category
            else:
                numbers[category] = numbers.get(category, 0) + 1
                member = g._backup_archive_name(category, numbers[category], path)
            archive.write(path, member)
            files.append({'arquivo': member, 'caminho_original': relative,
                          'origem_absoluta': str(path), 'tamanho_bytes': path.stat().st_size})
        archive.writestr('backup-manifest.json', json.dumps({'formato': 'codex-model-gate-backup-v2',
                           'estrutura': 'compacta-sem-pastas-aninhadas', 'schema_version': 3,
                           'arquivos': files, 'origem_dados': str(data),
                           'external_workspaces': len(external), 'credentials_included': False}, ensure_ascii=False))
        archive.writestr('LEIA-ME-BACKUP.txt', 'Projetos gerenciados, anexos, registros e configurações.\n'
                          'Não transfere credenciais ou sessões autenticadas.\n')
    return target


def restore_data_backup(source: Path, overwrite=False) -> dict:
    g = _gate()
    data = g.app_data_dir().resolve()
    groups, mapping, restored_paths = {}, {}, []
    restored = replaced = skipped = 0
    try:
        with zipfile.ZipFile(source.expanduser().resolve()) as archive:
            validate_archive(archive)
            entries = g._backup_entries(archive)
            if not entries:
                raise ValueError('O backup está vazio.')
            manifest = json.loads(_metadata_bytes(archive, 'backup-manifest.json', 64 * 1024**2)) if 'backup-manifest.json' in archive.namelist() else {}
            origins = {i['arquivo']: i.get('origem_absoluta') for i in manifest.get('arquivos', [])}
            old_root = manifest.get('origem_dados')
            plan = []
            for name, relative in entries:
                if relative.name in {'continuation.json', 'pending-continuation.json'}:
                    skipped += 1; continue
                target = data.joinpath(*relative.parts) if overwrite else g._non_overwriting_restore_path(data, relative, groups)
                if target is None:
                    skipped += 1; continue
                confined_target(data, PurePosixPath(target.relative_to(data).as_posix()))
                if origins.get(name):
                    mapping[str(origins[name])] = str(target)
                if old_root:
                    mapping[str(Path(old_root).joinpath(*relative.parts))] = str(target)
                plan.append((name, target))
            # Older backups stored relative destinations without source roots.
            # Recover only workspace prefixes whose project group is present.
            if not old_root:
                for name, relative in entries:
                    if relative.parts[0] != 'registro' or relative.suffix != '.md':
                        continue
                    try:
                        record = record_metadata(_metadata_bytes(archive, name).decode('utf-8'))
                    except (ValueError, UnicodeError):
                        continue
                    workspace = Path(str(record.get('project_folder') or ''))
                    parts = workspace.parts
                    project_indices = [i for i, part in enumerate(parts) if part.casefold() == 'projetos']
                    if not project_indices:
                        continue
                    index = project_indices[-1]
                    suffix = parts[index:]
                    relative_by_member = dict(entries)
                    for member, destination in plan:
                        relative_file = relative_by_member[member]
                        if relative_file.parts[:len(suffix)] == suffix:
                            new_workspace = destination
                            for _ in relative_file.parts[len(suffix):]:
                                new_workspace = new_workspace.parent
                            mapping[str(workspace)] = str(new_workspace)
                            break
            # Build directory mappings as well as file mappings (including rename groups).
            for old, new in list(mapping.items()):
                op, np = Path(old), Path(new)
                for _ in range(len(op.parts)):
                    op, np = op.parent, np.parent
                    if op == op.parent or np == data or not g._path_is_within(np, data):
                        break
                    mapping.setdefault(str(op), str(np))
            if old_root:
                mapping.setdefault(str(old_root), str(data))
            for name, target in plan:
                existed = target.exists()
                target.parent.mkdir(parents=True, exist_ok=True)
                temp = target.with_name(target.name + '.restore-' + uuid.uuid4().hex)
                try:
                    with archive.open(name) as origin, temp.open('wb') as output:
                        shutil.copyfileobj(origin, output)
                    if target.parent == data / 'registro' and target.suffix == '.md':
                        text = temp.read_text(encoding='utf-8')
                        if '<!-- CODEX_MODEL_GATE_RECORD:' in text:
                            record = remap_paths(record_metadata(text), mapping)
                            if not overwrite or record.get('project_folder') != record_metadata(text).get('project_folder'):
                                record['id'] = uuid.uuid4().hex
                                record['session_id'] = ''
                                record['restored_from_backup'] = True
                            temp.write_text(g._record_markdown(record), encoding='utf-8')
                    elif target.name in {'settings.json', 'history.json'}:
                        value = remap_paths(json.loads(temp.read_text(encoding='utf-8')), mapping)
                        if isinstance(value, dict):
                            value.pop('managed_workspaces', None)
                        temp.write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')
                    temp.replace(target)
                finally:
                    temp.unlink(missing_ok=True)
                restored += 1; replaced += int(existed); restored_paths.append(str(target))
    except zipfile.BadZipFile as exc:
        raise ValueError('O backup não é um ZIP válido.') from exc
    return {'restored': restored, 'overwritten': replaced, 'skipped': skipped, 'data_root': data}
