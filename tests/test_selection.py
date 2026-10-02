import json
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

import codex_model_gate as gate
import gate_selection as selection


class FakeSupervisor:
    def __init__(self, payload, code=0, after=None):
        import threading
        self.cancelled = threading.Event()
        self.payload, self.code, self.after = payload, code, after
        self.command = self.prompt = None

    def cancel(self):
        self.cancelled.set()

    def run(self, command, prompt, workspace, environment, on_log, on_started):
        self.command, self.prompt = command, prompt
        if self.after:
            self.after()
        return self.code, None, json.dumps(self.payload), ''


class SemanticSelectionTests(unittest.TestCase):
    def setUp(self):
        self.skills = [{'name': f'skill-{i}', 'description': 'Descrição completa ' * 30,
                        'scope': f'Competência específica {i}', 'path': f'/{i}/SKILL.md'}
                       for i in range(39)]

    def payload(self, name='skill-38'):
        return {'choices': [{'name': name, 'reason': 'Cobre a análise do documento.'}],
                'attachment_findings': 'O documento contém um contrato.',
                'limitations': '', 'live_web_search': True}

    def test_all_skills_and_full_descriptions_reach_ai_without_fixed_routes(self):
        supervisor = FakeSupervisor(self.payload())
        with patch.object(gate, 'focused_skills_for_task', side_effect=AssertionError('fixed route used')):
            decision = selection.select_skills_with_ai('Analise este documento.', self.skills, [],
                                                      'codex', supervisor)
        self.assertEqual(decision['selected'][0]['name'], 'skill-38')
        for skill in self.skills:
            self.assertIn(skill['name'], supervisor.prompt)
            self.assertIn(skill['description'].strip(), supervisor.prompt)
        self.assertIn('read-only', supervisor.command)
        self.assertIn('--ignore-user-config', supervisor.command)
        self.assertIn('--ephemeral', supervisor.command)
        self.assertIn('--output-schema', supervisor.command)
        self.assertNotIn('workspace-write', supervisor.command)

    def test_file_content_and_image_are_given_to_selector(self):
        with tempfile.TemporaryDirectory() as temporary:
            text = Path(temporary) / 'sem-tema-no-nome.txt'
            text.write_text('Contrato de licenciamento: royalties e confidencialidade.', encoding='utf-8')
            image = Path(temporary) / 'imagem.png'
            image.write_bytes(b'fake image for command validation')
            supervisor = FakeSupervisor(self.payload())
            selection.select_skills_with_ai('Revise os anexos.', self.skills, [text, image], 'codex', supervisor)
            self.assertIn('royalties e confidencialidade', supervisor.prompt)
            self.assertIn('--image', supervisor.command)
            self.assertIn(str(image.resolve()), supervisor.command)

    def test_docx_preview_reads_body_and_preserves_original(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'documento.docx'
            with zipfile.ZipFile(path, 'w') as archive:
                archive.writestr('word/document.xml', '<w:document xmlns:w="urn:w"><w:p><w:t>Nanofluidos automotivos</w:t></w:p></w:document>')
            original = path.read_bytes()
            self.assertIn('Nanofluidos', selection.attachment_preview(path)['text'])
            self.assertEqual(path.read_bytes(), original)

    def test_pdf_preview_extracts_content_without_inferring_from_name(self):
        from reportlab.pdfgen import canvas
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'sem-assunto.pdf'
            document = canvas.Canvas(str(path))
            document.drawString(60, 700, 'Ensaio de nanofluidos: viscosidade e estabilidade.')
            document.save()
            preview = selection.attachment_preview(path)
            self.assertEqual(preview['status'], 'content_excerpt')
            self.assertIn('viscosidade', preview['text'])

    def test_empty_catalog_is_reported_before_model_call(self):
        supervisor = FakeSupervisor(self.payload())
        with self.assertRaisesRegex(ValueError, 'catálogo'):
            selection.select_skills_with_ai('Analise.', [], [], 'codex', supervisor)
        self.assertIsNone(supervisor.command)

    def test_failed_or_invalid_analysis_never_becomes_empty_success(self):
        for payload, code in ((self.payload('inventada'), 0), ({}, 0), (self.payload(), 1),
                              ({**self.payload(), 'choices': [{'name': 'skill-1', 'reason': ''}]}, 0)):
            with self.subTest(payload=payload, code=code):
                with self.assertRaises((ValueError, RuntimeError)):
                    selection.select_skills_with_ai('Consulta.', self.skills, [], 'codex',
                                                   FakeSupervisor(payload, code))

    def test_valid_empty_choice_is_distinct_from_failure(self):
        decision = selection.select_skills_with_ai('Consulta.', self.skills, [], 'codex',
            FakeSupervisor({**self.payload(), 'choices': [], 'limitations': 'Não há competência adequada.'}))
        self.assertEqual(decision['selected'], [])
        self.assertIn('competência', decision['limitations'])

    def test_changed_attachment_invalidates_analysis(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'anexo.txt'
            path.write_text('Contrato', encoding='utf-8')
            supervisor = FakeSupervisor(self.payload(), after=lambda: path.write_text('Outro conteúdo longo', encoding='utf-8'))
            with self.assertRaisesRegex(ValueError, 'mudou'):
                selection.select_skills_with_ai('Analise.', self.skills, [path], 'codex', supervisor)

    def test_cancelled_analysis_and_missing_cli_do_not_run(self):
        supervisor = FakeSupervisor(self.payload())
        supervisor.cancel()
        with self.assertRaises(InterruptedError):
            selection.select_skills_with_ai('Analise.', self.skills, [], 'codex', supervisor)
        self.assertIsNone(supervisor.command)
        with self.assertRaises(RuntimeError):
            selection.select_skills_with_ai('Analise.', self.skills, [], None)

    def test_reconciliation_does_not_overrule_an_intelligent_choice(self):
        choice = self.skills[-1]
        self.assertEqual(gate.reconcile_semantic_selection(
            'Qual a ordem dos candidatos nas eleições?', [choice], self.skills), [choice])

    def test_previous_builtin_updates_but_custom_instructions_survive(self):
        with tempfile.TemporaryDirectory() as temporary:
            library = Path(temporary)
            path = library / gate.ORCHESTRATOR_SKILL_NAME / 'SKILL.md'
            path.parent.mkdir()
            path.write_text(gate.ORCHESTRATOR_SKILL_CONTENT_V11, encoding='utf-8')
            with patch.object(gate, 'managed_skills_dir', return_value=library):
                gate.ensure_orchestrator_skill()
                self.assertIn('ORCHESTRATOR_V12', path.read_text(encoding='utf-8'))
                self.assertEqual(gate.parse_skill(path)['name'], gate.ORCHESTRATOR_SKILL_NAME)
                path.write_text('Instruções personalizadas', encoding='utf-8')
                gate.ensure_orchestrator_skill()
                self.assertEqual(path.read_text(encoding='utf-8'), 'Instruções personalizadas')

    def test_builtin_profile_is_valid_and_scope_is_not_lost(self):
        from gate_skills import skill_profile
        profile = skill_profile(Path('builtin/SKILL.md'), gate.ORCHESTRATOR_SKILL_CONTENT)
        self.assertIsNotNone(profile)
        self.assertEqual(profile['name'], gate.ORCHESTRATOR_SKILL_NAME)
        self.assertIn('análise por IA', profile['scope'])

    def test_prompt_bounds_scope_and_avoids_redundant_orchestrators(self):
        skills = [{'name': 'nova', 'description': 'Competência completa',
                   'scope': 'x' * 6000, 'path': '/nova/SKILL.md'}]
        prompt = gate.semantic_selection_prompt('Analise.', skills)
        self.assertIn('x' * 1400, prompt)
        self.assertNotIn('x' * 1401, prompt)
        self.assertIn('Não selecione outra skill apenas para orquestrar', prompt)
