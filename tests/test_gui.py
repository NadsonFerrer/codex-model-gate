"""Integration checks against real Tk widgets; no paid CLI calls or real data."""
import json
import sys
import tempfile
import time
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch

import codex_model_gate as gate
import codex_model_gate_gui as gui


class GuiRegressionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            window=tk.Tk();window.withdraw();window.destroy()
        except tk.TclError as exc:
            raise unittest.SkipTest(f'Tcl/Tk unavailable in this environment: {exc}')

    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve()
        self.errors=[]
        patches=[patch.object(gate,'app_data_dir',return_value=self.root/'data'),
            patch.object(gate,'app_settings_path',return_value=self.root/'data'/'settings.json'),
            patch.object(gate,'resolve_codex_executable',return_value=sys.executable),
            patch.object(gate,'codex_cli_version',return_value=(0,160,0)),
            patch.object(gui.GateApp,'restore_pending_continuation'),
            patch.object(gui,'select_skills_with_ai',return_value={'selected': [], 'reasons': {}, 'model': gate.MODELS['sol'], 'attachment_findings': '', 'limitations': '', 'live_web_search': False, 'attachment_signature': [], 'usage': {}}),
            patch.object(gui.GateApp,'show_onboarding_if_needed'),
            patch.object(gui.GateApp,'check_scheduled_tasks'),
            patch.object(gui.GateApp,'install_localized_dialogs'),
            patch.object(gui.messagebox,'showerror',side_effect=lambda *args,**kwargs:self.errors.append(args)),
            patch.object(gui.messagebox,'showwarning',side_effect=lambda *args,**kwargs:self.errors.append(args)),
            patch.object(gui.messagebox,'showinfo'),patch.object(gui.messagebox,'askyesno',return_value=True)]
        for item in patches:item.start();self.addCleanup(item.stop)
        self.app=gui.GateApp();self.app.attributes('-alpha',0)
        self.app.report_callback_exception=lambda *exc:self.errors.append(exc)
        self.app.path_var.set(str(self.root/'projects'))
        self.addCleanup(self.close_app)
        self.pump(lambda:not self.app.pending_jobs)
        self.app.language='pt-BR';self.app.policy_var.set('equilibrada')

    def close_app(self):
        for identifier in self.app.tk.call('after','info'):
            self.app.after_cancel(identifier)
        self.app.destroy()

    def pump(self,predicate,timeout=4):
        end=time.monotonic()+timeout
        while time.monotonic()<end:
            self.app.update()
            if predicate():return
            time.sleep(.02)
        self.fail('GUI background work did not finish')

    def recommend(self):
        self.app.task.insert('1.0','Reescreva um título de relatório.')
        self.app.recommend();self.pump(lambda:not self.app.pending_jobs);self.assertIsNotNone(self.app.pending)

    def test_small_window_modes_keep_footer_visible_and_update_decision(self):
        self.app.geometry('620x500');self.app.update()
        for mode in [True,False,True,False]:
            self.app.ui_mode_var.set(mode);self.app.apply_ui_mode();self.app.update()
        self.assertTrue(self.app.run_button.winfo_viewable())
        self.assertLess(self.app.run_button.winfo_rooty(),self.app.winfo_rooty()+self.app.winfo_height())
        self.recommend()
        self.app.model_var.set('Astra');self.app.effort_var.set('Alto');self.app.sync_decision_settings()
        self.assertEqual(self.app.pending['model'],'astra')
        self.assertIn('Selecionado: Astra',self.app.decision_text.get())
        self.assertFalse(self.errors)

    def test_language_restart_is_blocked_during_execution(self):
        self.app.running=True
        with patch.object(self.app,'launch_fresh_instance') as restart:
            self.app.language_var.set('Español');self.app.change_language()
            restart.assert_not_called()
        self.app.running=False

    def test_new_user_starts_with_empty_task_and_no_attachments(self):
        self.assertEqual(self.app.task.get('1.0', tk.END).strip(), '')
        self.assertEqual(self.app.attachments, [])
        self.assertIsNone(self.app.pending)

    def test_existing_user_restores_only_their_saved_local_draft(self):
        attachment = self.root / 'meu-anexo.txt'
        attachment.write_text('Arquivo fictício deste perfil.', encoding='utf-8')
        gate.save_app_settings({'draft': {'task': 'Rascunho fictício deste usuário.',
            'attachments': [str(attachment)], 'root': str(self.root / 'meus-projetos')}})
        self.close_app()
        self.app = gui.GateApp()
        self.app.attributes('-alpha', 0)
        self.app.report_callback_exception=lambda *exc:self.errors.append(exc)
        self.pump(lambda:not self.app.pending_jobs)
        self.assertEqual(self.app.task.get('1.0', tk.END).strip(), 'Rascunho fictício deste usuário.')
        self.assertEqual(self.app.attachments, [attachment])
        self.assertEqual(self.app.path_var.get(), str(self.root / 'meus-projetos'))
        self.assertIsNone(self.app.pending)

    def test_ai_failure_unlocks_controls_and_requires_new_analysis(self):
        self.app.task.insert('1.0', 'Analise a tarefa.')
        with patch.object(gui, 'select_skills_with_ai', side_effect=RuntimeError('CLI indisponível')):
            self.app.recommend()
            self.pump(lambda:not self.app.pending_jobs)
        self.assertFalse(self.app.selecting_skills)
        self.assertFalse(self.app.busy_operation)
        self.assertIsNone(self.app.pending)
        self.assertEqual(str(self.app.recommend_button['state']), 'normal')
        self.assertIn('CLI indisponível', self.app.status.get())

    def test_ai_choices_and_reasons_reach_review_without_rule_override(self):
        skill = {'name': 'competencia-nova', 'description': 'Entende o arquivo',
                 'path': 'fixture', 'match_reasons': 'Conteúdo do anexo pede esta competência.'}
        self.app.task.insert('1.0', 'Qual a ordem dos candidatos nas eleições?')
        decision = {'selected': [skill], 'reasons': {skill['name']: skill['match_reasons']},
                    'model': gate.MODELS['sol'], 'attachment_findings': '', 'limitations': '',
                    'live_web_search': True, 'attachment_signature': [], 'usage': {}}
        with patch.object(gui, 'select_skills_with_ai', return_value=decision), \
                patch.object(gate, 'discover_skills', return_value=[skill]), \
                patch.object(gate, 'focused_skills_for_task', side_effect=AssertionError('fixed route')):
            self.app.recommend()
            self.pump(lambda:not self.app.pending_jobs)
        self.assertEqual(self.app.pending['skills'], [skill['name']])
        self.assertEqual(self.app.pending['skill_selection']['reasons'], decision['reasons'])
        self.assertTrue(self.app.pending['live_web_search'])
        self.assertFalse(self.errors)

    def test_authorization_uses_edited_root_and_policy_and_saves_result(self):
        self.recommend()
        edited=self.root/'edited-root';self.app.path_var.set(str(edited))
        self.app.policy_var.set('rigorosa')
        self.app.model_var.set('Sol 6.1');self.app.effort_var.set('Médio')
        received=[]
        def fake_run(command,instructions):
            received.append((self.app.cwd,self.app.pending['policy'],command))
            (self.app.cwd/'result.txt').write_text('resultado',encoding='utf-8')
            raw=json.dumps({'type':'turn.completed','usage':{'input_tokens':100,'cached_input_tokens':40,'output_tokens':10}})
            self.app.events.put(('done',0,'Resposta de teste','fake-session',raw))
        with patch.object(self.app,'run_prepared_task',side_effect=fake_run),patch.object(gui.simpledialog,'askstring',return_value='EXECUTAR'):
            self.app.authorize_run()
            self.pump(lambda:bool(self.app.record_note_path) and not self.app.busy_operation and not self.app.running)
        self.assertEqual(len(received),1)
        self.assertTrue(received[0][0].is_relative_to(edited))
        self.assertEqual(received[0][1],'rigorosa')
        self.assertIn('gpt-6.1-sol',received[0][2])
        record=gate.read_execution_records()[0]
        self.assertEqual(record['model_id'],'gpt-6.1-sol')
        self.assertEqual(record['token_usage']['cached_input'],40)
        self.assertEqual(Path(record['artifacts'][0]).read_text(encoding='utf-8'),'resultado')
        self.assertEqual(self.app.last_response_text,'Resposta de teste')
        self.assertFalse(self.errors)

    def test_write_failure_is_visible_and_response_survives(self):
        self.recommend()
        self.app.cwd=self.root/'work';self.app.cwd.mkdir()
        self.app.pending['project_folder']=str(self.app.cwd)
        self.app.show_response('resultado preservado')
        with patch.object(gate,'write_execution_record',side_effect=OSError('falha simulada')):
            self.app.save_execution_record('Concluída',[],'resultado preservado')
            self.pump(lambda:not self.app.pending_jobs)
        self.assertEqual(self.app.phase_var.get(),'Falha ao salvar registro')
        self.assertEqual(self.app.last_response_text,'resultado preservado')
        self.assertTrue(self.errors)

    def test_imported_task_starts_new_session_in_restored_workspace(self):
        workspace=self.root/'imported';workspace.mkdir()
        path=gate.write_execution_record(dict(id='imported',task='Reescrever título',
            project_folder=str(workspace),model_key='sol',model_id='gpt-6.1-sol',effort='medium',
            session_id='',imported_from_package='task.gate',conversation=[{'role':'user','text':'Pedido anterior'},
            {'role':'assistant','text':'Resposta anterior'}]))
        record=gate.read_execution_records()[0]
        self.assertTrue(self.app.record_can_continue(record))
        received=[]
        with patch.object(self.app,'selected_record',return_value=record):
            self.app.continue_selected_record_conversation()
        self.app.continuation_answer.insert('1.0','Faça um resumo do resultado anterior.')
        def run(command,prompt):
            received.append((command,prompt,self.app.cwd))
            self.app.events.put(('done',0,'Resumo atualizado','new-real-session',''))
        with patch.object(self.app,'_run_codex',side_effect=run):
            self.app.continue_current_task()
            self.pump(lambda:bool(received) and not self.app.running and not self.app.busy_operation)
        self.assertNotIn('resume',received[0][0])
        self.assertIn('Resposta anterior',received[0][1])
        self.assertEqual(received[0][2],workspace)
        self.assertEqual(gate.read_execution_records()[0]['session_id'],'new-real-session')
        self.assertFalse(self.errors)
