import ctypes
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import codex_model_gate as gate
from gate_archives import record_metadata
from gate_execution import ProcessSupervisor
from gate_models import local_catalog
from gate_models import latest_cli_release, CLI_CHANGELOG_URL
from gate_records import RecordRepository
from gate_storage import atomic_write_text, load_json, safe_relative_path, validate_archive
from gate_usage import usage_records


class RegressionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.data = self.root / 'dados'
        self.data.mkdir()
        self.mock = patch.object(gate, 'app_data_dir', return_value=self.data)
        self.mock.start()
        self.addCleanup(self.mock.stop)
        settings=patch.object(gate,'app_settings_path',return_value=self.data/'settings.json')
        settings.start();self.addCleanup(settings.stop)

    def test_portuguese_uppercase_is_not_mojibake(self):
        self.assertEqual(gate._text_validation_issues('CONCLUSÃO E REFERÊNCIAS. ÂNCORA.',False,False),[])
        self.assertTrue(gate._text_validation_issues('ConclusÃ£o e referÃªncias',False,False))

    def record(self, workspace, **kwargs):
        return gate.write_execution_record(dict(id='abc123',task='Analisar arquivo',
            model_key='sol',model_id='gpt-6.1-sol',effort='medium',project_folder=str(workspace),
            session_id='session-do-not-migrate',artifacts=[],attachments=[], **kwargs))

    def test_package_survives_source_removal_with_attachments_and_artifacts(self):
        workspace = self.root/'externo'/'tarefa'; workspace.mkdir(parents=True)
        source=self.root/'anexo.txt';source.write_text('conteúdo',encoding='utf-8')
        staged=gate.stage_attachments(workspace,[source],'abc123')
        result=workspace/'resultado.txt';result.write_text('resultado',encoding='utf-8')
        path=gate.write_execution_record(dict(id='abc123',task='Analisar arquivo',project_folder=str(workspace),
            artifacts=[str(result)],attachments=staged,session_id='segredo-sessao'))
        record=record_metadata(path.read_text(encoding='utf-8'));record['record_file']=str(path)
        package=gate.export_task_package(record,self.root/'saida.gate')
        import shutil
        shutil.rmtree(workspace);source.unlink()
        imported=gate.import_task_package(package,self.root/'destino')
        restored=Path(imported['project_folder'])
        self.assertEqual(Path(imported['artifacts'][0]).read_text(encoding='utf-8'),'resultado')
        self.assertEqual((restored/imported['attachments'][0]['staged']).read_text(encoding='utf-8'),'conteúdo')
        self.assertTrue(imported['attachments'][0]['active'])
        self.assertEqual(imported['session_id'],'')
        self.assertEqual(imported['attachments'][0]['original'],'')

    def test_backup_includes_external_workspace_and_remaps_record(self):
        workspace=self.root/'external'/'work';workspace.mkdir(parents=True)
        output=workspace/'report.txt';output.write_text('copiado')
        path=gate.write_execution_record(dict(id='abc',task='test',project_folder=str(workspace),
            artifacts=[str(output)],session_id='old-session'))
        backup=gate.create_data_backup(self.root/'backup.zip')
        destination=self.root/'new-data';destination.mkdir()
        with patch.object(gate,'app_data_dir',return_value=destination):
            gate.restore_data_backup(backup)
            records=gate.read_execution_records()
        self.assertEqual(len(records),1)
        record=records[0]
        self.assertTrue(Path(record['project_folder']).is_relative_to(destination))
        self.assertEqual(Path(record['artifacts'][0]).read_text(),'copiado')
        self.assertEqual(record['session_id'],'')

    def test_restore_no_overwrite_keeps_records_readable_and_remaps_group(self):
        workspace=self.data/'projetos'/'work';workspace.mkdir(parents=True)
        output=workspace/'report.txt';output.write_text('old')
        path=gate.write_execution_record(dict(id='abc',task='test',project_folder=str(workspace),artifacts=[str(output)]))
        backup=gate.create_data_backup(self.root/'backup.zip')
        gate.restore_data_backup(backup,overwrite=False)
        records=gate.read_execution_records()
        self.assertEqual(len(records),2)
        newer=next(r for r in records if r['id']!='abc')
        self.assertTrue(Path(newer['record_file']).name.endswith('.md'))
        self.assertNotEqual(newer['project_folder'],str(workspace))
        self.assertEqual(Path(newer['artifacts'][0]).read_text(),'old')

    def test_legacy_backup_infers_project_prefix(self):
        old=self.root/'computer-old'/'dados'/'projetos'/'work'
        text=gate._record_markdown(dict(id='old',task='test',project_folder=str(old),artifacts=[str(old/'out.txt')]))
        archive=self.root/'legacy.zip'
        with zipfile.ZipFile(archive,'w') as z:
            z.writestr('projetos/work/out.txt','migrated')
            z.writestr('registro/record.md',text)
        gate.restore_data_backup(archive)
        record=gate.read_execution_records()[0]
        self.assertEqual(Path(record['artifacts'][0]).read_text(),'migrated')

    def test_atomic_failure_keeps_old_file(self):
        path=self.root/'settings.json';atomic_write_text(path,'{"good":1}')
        import gate_storage
        original=gate_storage.os.replace
        def fail(source,destination):
            if Path(destination)==path:raise OSError('injected replacement failure')
            return original(source,destination)
        with patch('gate_storage.os.replace',side_effect=fail):
            with self.assertRaises(OSError):atomic_write_text(path,'{"bad":2}')
        self.assertEqual(json.loads(path.read_text()),{'good':1})
        self.assertFalse(list(self.root.glob('*.tmp')))

    def test_settings_fallback_after_corruption(self):
        path=self.data/'settings.json'
        atomic_write_text(path,'{"version":1}');atomic_write_text(path,'{"version":2}')
        path.write_text('{broken')
        self.assertEqual(load_json(path,dict,{}),{'version':1})

    def test_failed_record_update_is_explicit(self):
        with self.assertRaises(OSError):gate.update_execution_record(self.root/'missing.md',quality='ok')

    def test_repository_reuses_unchanged_content_and_recovers_previous_revision(self):
        workspace=self.root/'work';workspace.mkdir()
        path=self.record(workspace)
        repository=RecordRepository();repository.read(path.parent)
        with patch.object(Path,'read_text',side_effect=AssertionError('unexpected file read')):
            self.assertEqual(len(repository.read(path.parent)),1)
        gate.update_execution_record(path,quality='ok')
        path.write_text('broken')
        self.assertEqual(repository.read(path.parent)[0]['id'],'abc123')
        self.assertTrue(repository.issues)

    def test_archive_rejects_windows_collisions(self):
        path=self.root/'collision.zip'
        with zipfile.ZipFile(path,'w') as z:z.writestr('A.txt','a');z.writestr('a.txt','b')
        with zipfile.ZipFile(path) as z:
            with self.assertRaises(ValueError):validate_archive(z)

    def test_unsafe_windows_paths_are_rejected(self):
        for name in ['../outside','C:/outside','a/../b','a//b','NUL.txt','folder./file','/absolute']:
            with self.subTest(name=name),self.assertRaises(ValueError):safe_relative_path(name)

    def test_package_export_inside_workspace_is_rejected(self):
        workspace=self.root/'work';workspace.mkdir()
        path=self.record(workspace)
        record=record_metadata(path.read_text(encoding='utf-8'));record['record_file']=str(path)
        with self.assertRaises(ValueError):gate.export_task_package(record,workspace/'bad.gate')

    def test_package_path_escape_creates_no_workspace(self):
        archive=self.root/'malicious.gate'
        with zipfile.ZipFile(archive,'w') as z:
            z.writestr('manifest.json',json.dumps({'format':gate.GATE_PACKAGE_FORMAT}))
            z.writestr('record.md',gate._record_markdown({'task':'test'}))
            z.writestr('workspace/../escape','x')
        with self.assertRaises(ValueError):gate.import_task_package(archive,self.root/'new-projects')
        self.assertFalse((self.root/'new-projects').exists())

    def test_nested_usage_and_cumulative_do_not_double_count(self):
        raw='\n'.join(json.dumps(e) for e in [
            {'type':'turn.completed','usage':{'input_tokens':100,'input_tokens_details':{'cached_tokens':50},'output_tokens':20}},
            {'type':'token_count','info':{'total_token_usage':{'input_tokens':100,'cached_input_tokens':50,'output_tokens':20}}}])
        self.assertEqual(gate.extract_codex_token_usage(raw),{'input':100,'cached_input':50,'output':20,'reasoning':0})

    def test_usage_turns_keep_separate_dates_and_pricing(self):
        record={'finished_at':'2026-10-01','model_key':'sol','model_id':'gpt-6.1-sol','turn_metrics':[
            {'started_at':'2026-09-30','token_usage':{'input':2},'pricing':{'input':2},'exchange_rates':{'BRL':5}},
            {'started_at':'2026-10-01','token_usage':{'input':3},'pricing':{'input':3}}]}
        records=list(usage_records([record]))
        self.assertEqual([r['finished_at'] for r in records],['2026-09-30','2026-10-01'])
        self.assertEqual(records[0]['exchange_rates'],{'BRL':5})
        self.assertEqual(records[1]['pricing'],{'input':3})

    def test_old_sol_usage_maps_to_legacy_model(self):
        self.assertEqual(list(usage_records([{'model_key':'sol'}]))[0]['model_key'],'sol6')

    def test_new_and_old_sol_records_remain_distinct(self):
        self.assertEqual(gate.record_model_settings({'model_key':'sol','model_id':'gpt-6.1-sol','effort':'medium'}),('sol','medium'))
        self.assertEqual(gate.record_model_settings({'model':'Sol — Médio'}),('sol6','medium'))
        self.assertEqual(gate.record_model_settings({'model':'Sol 6.1 — Médio'}),('sol','medium'))

    def test_cli_model_minimum_and_invalid_effort(self):
        self.assertIsNotNone(gate.cli_model_compatibility_message('codex','sol',(0,159,0)))
        self.assertIsNone(gate.cli_model_compatibility_message('codex','sol',(0,159,1)))
        with self.assertRaises(ValueError):gate.build_codex_exec_command('gpt-6.1-sol','unsupported')

    def test_local_catalog_requires_matching_version_and_valid_public_fields(self):
        path=self.root/'models_cache.json'
        path.write_text(json.dumps({'client_version':'0.159.2','identity':{'private':'not-returned'},'models':[
            {'slug':'gpt-6.1-sol','supported_reasoning_levels':[{'effort':'high'},{'effort':'ultra'}]},
            {'slug':'evil arguments','supported_reasoning_levels':[{'effort':'high'}]}]}))
        self.assertEqual(local_catalog(self.root,(0,159,2)),[{'id':'gpt-6.1-sol','efforts':('high','ultra')}])
        self.assertEqual(local_catalog(self.root,(0,159,1)),[])
        self.assertEqual(local_catalog(self.root,None),[])

    def test_release_check_uses_stable_official_headings(self):
        from unittest.mock import MagicMock
        response=MagicMock()
        response.__enter__.return_value=response
        response.geturl.return_value=CLI_CHANGELOG_URL
        response.read.return_value=b'<h3>Codex CLI 0.159.1</h3><h3>Codex CLI 0.160.0</h3><h3>Codex CLI 0.999.0-alpha</h3>'
        with patch('urllib.request.urlopen',return_value=response):
            self.assertEqual(latest_cli_release(),(0,160,0))

    def test_cancelled_preparation_does_not_copy_inputs(self):
        event=threading.Event();event.set()
        source=self.root/'source.txt';source.write_text('original')
        workspace=self.root/'cancelled';workspace.mkdir()
        with self.assertRaises(InterruptedError):gate.stage_attachments(workspace,[source],'id',event)
        self.assertFalse(list(workspace.rglob('source.txt')))
        self.assertEqual(source.read_text(),'original')

    def test_multiline_yaml_skill_and_missing_description(self):
        path=self.root/'SKILL.md'
        path.write_text('---\nname: skill-test\ndescription: >\n  Primeira linha\n  segunda linha\ngate_outcomes:\n  - document_formatting\n---\n# title\n',encoding='utf-8')
        skill=gate.parse_skill(path)
        self.assertIn('segunda linha',skill['description'])
        self.assertEqual(skill['gate_outcomes'],'document_formatting')
        path.write_text('---\nname: no-description\n---\n')
        self.assertIsNone(gate.parse_skill(path))

    def test_invalid_utf8_skill_does_not_crash_catalog(self):
        path=self.root/'SKILL.md';path.write_bytes(b'\xff\xfe')
        self.assertIsNone(gate.parse_skill(path))

    def test_supervisor_keeps_stderr_out_of_structured_answer(self):
        supervisor=ProcessSupervisor()
        code="import sys,json; sys.stdin.read(); print(json.dumps({'type':'item.completed','item':{'type':'agent_message','text':'resposta'}})); print('diagnostic',file=sys.stderr)"
        status,session,output,raw=supervisor.run([sys.executable,'-c',code],'prompt',self.root,os.environ.copy(),lambda _:None,lambda _:None)
        self.assertEqual(status,0);self.assertEqual(output,'resposta');self.assertNotIn('diagnostic',raw)

    @unittest.skipUnless(os.name=='nt','Windows process-tree test')
    def test_cancellation_terminates_descendants(self):
        marker=self.root/'child.pid'
        code="import subprocess,sys,time; p=subprocess.Popen([sys.executable,'-c','import time; time.sleep(60)']); open('child.pid','w').write(str(p.pid)); time.sleep(60)"
        supervisor=ProcessSupervisor();result=[]
        thread=threading.Thread(target=lambda:result.append(supervisor.run([sys.executable,'-c',code],'',self.root,os.environ.copy(),lambda _:None,lambda _:None)))
        thread.start()
        deadline=time.monotonic()+8
        while not marker.exists() and time.monotonic()<deadline:time.sleep(.02)
        self.assertTrue(marker.exists())
        pid=int(marker.read_text())
        try:
            supervisor.cancel();thread.join(8)
            self.assertFalse(thread.is_alive())
            kernel=ctypes.WinDLL('kernel32',use_last_error=True)
            kernel.OpenProcess.restype=ctypes.c_void_p
            handle=kernel.OpenProcess(0x1000,False,pid)
            if handle:
                kernel.GetExitCodeProcess.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_ulong)]
                kernel.CloseHandle.argtypes=[ctypes.c_void_p]
                exitcode=ctypes.c_ulong();kernel.GetExitCodeProcess(handle,ctypes.byref(exitcode));kernel.CloseHandle(handle)
                self.assertNotEqual(exitcode.value,259)
        finally:
            if thread.is_alive():subprocess.run(['taskkill','/PID',str(supervisor.process.pid),'/T','/F'],capture_output=True)


if __name__=='__main__':unittest.main()
