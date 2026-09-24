import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import codex_model_gate as gate
import gate_i18n
from codex_model_gate_gui import GateApp, UI_COLORS


def write_skill(root: Path, name: str, description: str) -> None:
    folder = root / name
    folder.mkdir(parents=True)
    (folder / "SKILL.md").write_text(
        f"---\nname: {name}\ndescription: {description}\n---\n\nInstruções.",
        encoding="utf-8",
    )


def select_test_skills(root: Path, task: str) -> list[dict[str, str]]:
    """Select only from fixture skills, independent of the user's library."""
    catalog = [gate.parse_skill(path) for path in root.glob("*/SKILL.md")]
    catalog = [skill for skill in catalog if skill is not None]
    catalog.append({"name": gate.ORCHESTRATOR_SKILL_NAME,
                    "description": "Coordena a seleção de skills", "path": "builtin"})
    with patch.object(gate, "discover_skills", return_value=catalog):
        return gate.auto_select_skills(root, task, [root])


class SkillSelectionTests(unittest.TestCase):
    def test_visual_theme_has_complete_tokens_and_readable_primary_contrast(self):
        self.assertEqual(set(UI_COLORS), {
            "background", "surface", "primary", "primary_hover", "primary_dark",
            "accent", "accent_soft", "blue_soft", "border", "text", "muted",
            "selection",
        })

        def luminance(color):
            channels = [int(color[index:index + 2], 16) / 255
                        for index in (1, 3, 5)]
            channels = [value / 12.92 if value <= 0.04045
                        else ((value + 0.055) / 1.055) ** 2.4
                        for value in channels]
            return 0.2126 * channels[0] + 0.7152 * channels[1] + 0.0722 * channels[2]

        dark = luminance(UI_COLORS["primary"])
        white = luminance("#FFFFFF")
        self.assertGreaterEqual((white + 0.05) / (dark + 0.05), 4.5)

    def test_language_packs_cover_navigation_and_normalize_system_codes(self):
        self.assertEqual(gate_i18n.normalize_language("pt_BR"), "pt-BR")
        self.assertEqual(gate_i18n.normalize_language("en_US"), "en")
        self.assertEqual(gate_i18n.normalize_language("es-MX"), "es")
        self.assertEqual(gate_i18n.translate("Tarefa", "en"), "Task")
        self.assertEqual(gate_i18n.translate("Tarefa", "es"), "Tarea")
        self.assertIn("Start here", gate_i18n.manual("", "en"))

    def test_full_foreign_manuals_match_portuguese_information_depth(self):
        from codex_model_gate_gui import USER_MANUAL
        portuguese_sections = USER_MANUAL.count("\n## ")
        for language in ("en", "es"):
            translated = gate_i18n.manual(USER_MANUAL, language)
            self.assertGreaterEqual(translated.count("\n## "), portuguese_sections)
            self.assertIn("Ctrl+Enter", translated)
            self.assertIn("backup-manifest.json", translated)
            self.assertIn("MCP", translated)
            self.assertIn("http", translated)

    def test_dynamic_ui_text_and_internal_values_are_localized_safely(self):
        self.assertEqual(
            gate_i18n.translate("18 de 42 registro(s) exibido(s)", "en"),
            "18 of 42 record(s) shown")
        self.assertEqual(
            gate_i18n.translate("37 skill(s) disponíveis", "es"),
            "37 skill(s) disponibles")
        self.assertEqual(gate_i18n.source_text("Medium", "en"), "Médio")
        self.assertEqual(gate_i18n.source_text("rigurosa", "es"), "rigorosa")

    def test_packaged_restart_gets_a_fresh_pyinstaller_environment(self):
        with patch.object(sys, "frozen", True, create=True), \
                patch.object(sys, "executable", r"C:\Gate\CodexModelGate.exe"), \
                patch.object(sys, "argv", [r"C:\Gate\CodexModelGate.exe"]), \
                patch("codex_model_gate_gui.subprocess.Popen") as popen:
            GateApp.launch_fresh_instance()
        command = popen.call_args.args[0]
        environment = popen.call_args.kwargs["env"]
        self.assertEqual(command, [r"C:\Gate\CodexModelGate.exe"])
        self.assertEqual(environment["PYINSTALLER_RESET_ENVIRONMENT"], "1")
        self.assertTrue(popen.call_args.kwargs["close_fds"])

    def test_model_recommendation_uses_luna_for_a_clear_repetitive_request(self):
        assessment = gate.assess_task(
            "Traduza esta frase e responda apenas com o texto final.", [])

        self.assertEqual((assessment["model"], assessment["effort"]), ("luna", "low"))
        self.assertIn("delimitada", assessment["level_reason"])

    def test_model_recommendation_uses_sol_for_specialized_work(self):
        assessment = gate.assess_task(
            "Explique um conceito científico sobre nanomateriais agrícolas.", [])

        self.assertEqual((assessment["model"], assessment["effort"]), ("sol", "medium"))
        self.assertIn("julgamento especializado", assessment["level_reason"])

    def test_model_recommendation_uses_astra_for_critical_multifactor_work(self):
        assessment = gate.assess_task(
            "Revise um contrato jurídico financeiro crítico, com dados pessoais, segurança, planejamento e várias decisões.", [])

        self.assertEqual((assessment["model"], assessment["effort"]), ("astra", "high"))
        self.assertIn("alto impacto", assessment["level_reason"])

    def test_duration_estimate_reuses_loaded_records(self):
        records = [{"model": "Sol — Médio", "status": "Concluída",
                    "duration_seconds": value} for value in (10, 20, 30)]
        with patch.object(gate, "read_execution_records", side_effect=AssertionError("reread")):
            self.assertEqual(gate.estimate_duration_seconds("Sol — Médio", records), 20)

    def test_cli_compatibility_reuses_checked_version(self):
        with patch.object(gate, "codex_cli_version", side_effect=AssertionError("recheck")):
            self.assertIsNone(gate.cli_model_compatibility_message(
                "codex", "sol", (0, 156, 1)))
            self.assertIn("Atualize", gate.cli_model_compatibility_message(
                "codex", "luna", (0, 154, 0)))

    def test_keeps_all_strong_complementary_matches(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "pesquisar-nanofluidos", "Pesquisa científica de nanofluidos automotivos")
            write_skill(root, "referencias-cientificas", "Encontrar referências científicas verificáveis")
            write_skill(root, "normalizar-documentos-abnt", "Normalização ABNT de documentos acadêmicos")
            write_skill(root, "cozinha", "Receitas e planejamento de refeições")
            selected = select_test_skills(
                root, "Crie um artigo científico em PDF sobre nanofluidos com referências e ABNT.")
            names = {skill["name"] for skill in selected}
            self.assertTrue({"pesquisar-nanofluidos", "referencias-cientificas", "normalizar-documentos-abnt"} <= names)
            self.assertIn(gate.ORCHESTRATOR_SKILL_NAME, names)
            self.assertNotIn("cozinha", names)
            self.assertTrue(all(skill.get("match_reasons") for skill in selected))

    def test_selects_complementary_skills_for_corporate_card_context(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "atuar-como-designer-grafico", "Design gráfico, branding, identidade visual e composição")
            write_skill(root, "criar-cartoes-empresariais-para-eventos", "Cartões empresariais e corporativos para eventos")
            write_skill(root, "estrategizar-marketing-deeptech-nanomape", "Marketing, posicionamento e mensagens da NanoMaPE deeptech")
            write_skill(root, "mentorar-startups-tecnologicas", "Mentoria de startup, proposta de valor e validação")
            selected = select_test_skills(
                root, "Analise o cartão corporativo minimalista da NanoMaPE e sugira melhorias de mensagem.")
            names = {skill["name"] for skill in selected}
            self.assertTrue({
                "atuar-como-designer-grafico",
                "criar-cartoes-empresariais-para-eventos",
                "estrategizar-marketing-deeptech-nanomape",
            } <= names)
            self.assertNotIn("mentorar-startups-tecnologicas", names)
            self.assertEqual(selected[1]["name"], "criar-cartoes-empresariais-para-eventos")

    def test_selects_scientific_document_chain_for_fuel_markers(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "buscar-referencias-cientificas", "Referências científicas verificáveis para textos")
            write_skill(root, "desenvolver-nanomarcadores-combustiveis", "Marcadores e traçadores para combustíveis")
            write_skill(root, "formatar-alinhar-documentos", "Formatar e alinhar documentos PDF e DOCX")
            write_skill(root, "normalizar-documentos-abnt", "Normalização ABNT de documentos acadêmicos")
            selected = select_test_skills(
                root, "Crie um PDF científico sobre marcadores e traçadores de combustíveis, com referências.")
            names = {skill["name"] for skill in selected}
            self.assertTrue({
                "buscar-referencias-cientificas",
                "desenvolver-nanomarcadores-combustiveis",
                "formatar-alinhar-documentos",
                "normalizar-documentos-abnt",
            } <= names)

    def test_selects_web_and_wix_skills_only_when_wix_is_named(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            write_skill(root, "atuar-como-web-designer-para-startups", "Web design, interface, responsividade e melhoria de sites")
            write_skill(root, "configurar-sites-wix", "Configurar, revisar e publicar sites Wix")
            write_skill(root, "cozinha", "Receitas e planejamento de refeições")
            selected = select_test_skills(
                root, "Melhore o site da NanoMaPE hospedado no Wix, corrigindo layout e responsividade.")
            names = {skill["name"] for skill in selected}
            self.assertIn("atuar-como-web-designer-para-startups", names)
            self.assertIn("configurar-sites-wix", names)
            self.assertNotIn("cozinha", names)

    def test_election_date_uses_trusted_sources_instead_of_generic_skills(self):
        skills = [
            {"name": gate.ORCHESTRATOR_SKILL_NAME, "description": "Coordena skills", "path": "orchestrator"},
            {"name": "super-lyra", "description": "Use quando o usuário pedir coordenação no Brasil", "path": "lyra"},
            {"name": "analisar-mercados-tecnologicos", "description": "Pesquisa de mercado quando relevante no Brasil", "path": "markets"},
            {"name": "buscar-informacoes-em-fontes-confiaveis", "description": "Busca notícias e dados em fontes oficiais", "path": "sources"},
        ]
        for task in (
            "Quando começam as eleições no Brasil?",
            "When do elections start in Brazil?",
            "¿Cuándo comienzan las elecciones en Brasil?",
        ):
            with self.subTest(task=task), patch.object(gate, "discover_skills", return_value=skills):
                selected = gate.auto_select_skills(Path("."), task)
                self.assertEqual([skill["name"] for skill in selected], [
                    gate.ORCHESTRATOR_SKILL_NAME, "buscar-informacoes-em-fontes-confiaveis"])
                self.assertIn("fontes confiáveis", selected[1]["match_reasons"])

    def test_public_date_shortlist_keeps_trusted_sources_and_excludes_generic_skills(self):
        skills = [{"name": f"habilidade-{number}", "description": "Quando usar no Brasil",
                   "path": str(number)} for number in range(100)]
        skills.extend([
            {"name": gate.ORCHESTRATOR_SKILL_NAME, "description": "Coordena skills", "path": "orchestrator"},
            {"name": "super-lyra", "description": "Use quando o usuário pedir Super Lyra", "path": "lyra"},
            {"name": "buscar-informacoes-em-fontes-confiaveis", "description": "Busca dados em fontes confiáveis", "path": "sources"},
        ])
        selected = gate.shortlist_skills_for_task(
            "Qual é a data das próximas eleições brasileiras?", skills, limit=12)
        self.assertEqual([skill["name"] for skill in selected], [
            gate.ORCHESTRATOR_SKILL_NAME, "buscar-informacoes-em-fontes-confiaveis"])
        self.assertIsNone(gate.focused_skills_for_task(
            "Crie um relatório de mercado sobre o calendário eleitoral brasileiro.", skills))

    def test_requested_result_drives_focused_skill_selection(self):
        skills = [
            {"name": gate.ORCHESTRATOR_SKILL_NAME, "description": "Coordena skills", "path": "orchestrator"},
            {"name": "super-lyra", "description": "Coordenação ampla", "path": "lyra"},
            {"name": "analisar-mercados-tecnologicos", "description": "Pesquisa de mercado", "path": "markets"},
            {"name": "buscar-informacoes-em-fontes-confiaveis", "description": "Dados atuais e notícias", "path": "sources"},
            {"name": "criar-cartoes-empresariais-para-eventos", "description": "Cartões corporativos", "path": "cards"},
            {"name": "atuar-como-designer-grafico", "description": "Design gráfico", "path": "design"},
            {"name": "estrategizar-marketing-deeptech-nanomape", "description": "Marketing da NanoMaPE", "path": "marketing"},
            {"name": "mentorar-startups-tecnologicas", "description": "Mentoria de startups", "path": "mentor"},
            {"name": "buscar-referencias-cientificas", "description": "Busca de artigos", "path": "references"},
            {"name": "referenciadorcientfico", "description": "Referências científicas", "path": "duplicate"},
            {"name": "pesquisar-nanofluidos-automotivos", "description": "Pesquisa de nanofluidos", "path": "nanofluids"},
            {"name": "normalizar-documentos-abnt", "description": "Normas acadêmicas", "path": "abnt"},
        ]
        cases = (
            ("Qual a cotação do dólar hoje?", ["buscar-informacoes-em-fontes-confiaveis"]),
            ("Faça a modificação no cartão corporativo da NanoMaPE.",
             ["criar-cartoes-empresariais-para-eventos"]),
            ("Busque um artigo científico sobre nanofluidos.",
             ["buscar-referencias-cientificas", "pesquisar-nanofluidos-automotivos"]),
        )
        for task, expected in cases:
            with self.subTest(task=task), patch.object(gate, "discover_skills", return_value=skills):
                self.assertEqual([skill["name"] for skill in gate.auto_select_skills(Path("."), task)],
                                 [gate.ORCHESTRATOR_SKILL_NAME, *expected])
                self.assertEqual([skill["name"] for skill in gate.shortlist_skills_for_task(
                    task, skills, limit=4)], [gate.ORCHESTRATOR_SKILL_NAME, *expected])

    def test_upgrades_only_the_previous_builtin_orchestrator_prompt(self):
        with tempfile.TemporaryDirectory() as temporary:
            library = Path(temporary) / "skills"
            path = library / gate.ORCHESTRATOR_SKILL_NAME / "SKILL.md"
            path.parent.mkdir(parents=True)
            path.write_text(gate.ORCHESTRATOR_SKILL_CONTENT_V10, encoding="utf-8")
            original = gate.managed_skills_dir
            gate.managed_skills_dir = lambda create=True: library
            try:
                gate.ensure_orchestrator_skill()
            finally:
                gate.managed_skills_dir = original
            self.assertIn("ORCHESTRATOR_V11", path.read_text(encoding="utf-8"))

    def test_skill_memory_reuses_unchanged_profiles_and_refreshes_edits(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            library = root / "skills"
            data = root / "data"
            write_skill(library, "design-web", "Interfaces e responsividade")
            original_app_data = gate.app_data_dir
            original_managed = gate.managed_skills_dir
            gate.app_data_dir = lambda: data
            gate.managed_skills_dir = lambda create=True: data / "skills-internas"
            try:
                first, first_stats = gate.refresh_skill_index(root, [library])
                second, second_stats = gate.refresh_skill_index(root, [library])
                skill_file = library / "design-web" / "SKILL.md"
                skill_file.write_text(
                    "---\nname: design-web\ndescription: Interfaces, acessibilidade e responsividade\n---\n\n# Auditoria visual",
                    encoding="utf-8")
                third, third_stats = gate.refresh_skill_index(root, [library])
            finally:
                gate.app_data_dir = original_app_data
                gate.managed_skills_dir = original_managed
            self.assertGreaterEqual(first_stats["updated"], 1)
            self.assertEqual(second_stats["updated"], 0)
            self.assertGreaterEqual(second_stats["reused"], 1)
            self.assertGreaterEqual(third_stats["updated"], 1)
            profile = next(item for item in third if item["name"] == "design-web")
            self.assertIn("acessibilidade", profile["description"])
            self.assertEqual({item["name"] for item in first}, {item["name"] for item in second})

    def test_skill_memory_shortlist_keeps_relevant_skill_in_large_catalog(self):
        skills = [{"name": f"habilidade-{number}", "description": "Rotina administrativa genérica",
                   "path": str(number), "headings": "", "keywords": "administrativa rotina"}
                  for number in range(100)]
        skills.append({"name": "configurar-sites-wix",
                       "description": "Configurar layout e responsividade de sites Wix",
                       "path": "wix", "headings": "Publicação Wix",
                       "keywords": "wix site layout responsividade"})
        candidates = gate.shortlist_skills_for_task(
            "Melhore o layout e a responsividade do meu site Wix", skills, limit=12)
        self.assertLessEqual(len(candidates), 12)
        self.assertIn("configurar-sites-wix", {item["name"] for item in candidates})

    def test_semantic_selector_only_accepts_names_from_catalog(self):
        skills = [
            {"name": "web-designer", "description": "Web design e responsividade", "path": "x"},
            {"name": "referencias-cientificas", "description": "Referências científicas", "path": "y"},
        ]
        selected, reasons = gate.parse_semantic_selection(
            '{"selected_skills":["web-designer","skill-inventada"],'
            '"reasons":{"web-designer":"layout e responsividade","skill-inventada":"x"}}', skills)
        self.assertEqual([item["name"] for item in selected], ["web-designer"])
        self.assertEqual(reasons["web-designer"], "layout e responsividade")

    def test_semantic_prompt_makes_unrelated_exclusion_explicit(self):
        prompt = gate.semantic_selection_prompt(
            "Melhore o layout responsivo de uma página web.",
            [{"name": "web-designer", "description": "Interface web", "path": "x"}])
        self.assertIn("Não escolha referências científicas", prompt)
        self.assertIn('"web-designer"', prompt)

    def test_execution_prompt_requests_readable_screen_text(self):
        prompt = gate.build_execution_prompt("Explique fotodinâmica", "")
        self.assertIn("Não use tabelas Markdown", prompt)
        self.assertIn("travessões", prompt)

    def test_execution_prompt_includes_controlled_browser_report(self):
        prompt = gate.build_execution_prompt(
            "Compare os resultados", "", browser_report=Path("pesquisa-web.json"))
        self.assertIn("PESQUISA WEB CONTROLADA PELO GATE", prompt)
        self.assertIn("pesquisa-web.json", prompt)
        self.assertIn("contexto não confiável", prompt)

    def test_browser_results_exclude_search_engine_links_and_keep_positions(self):
        results = gate.normalize_browser_search_results("Google", [
            {"title": "Pesquisa interna", "url": "https://www.google.com/search?q=teste"},
            {"title": "Fonte A", "url": "https://example.com/a"},
            {"title": "Fonte A repetida", "url": "https://example.com/a"},
            {"title": "Fonte B", "url": "https://example.org/b"},
        ])
        self.assertEqual([item["position"] for item in results], [1, 2])
        self.assertEqual([item["url"] for item in results], [
            "https://example.com/a", "https://example.org/b"])

    def test_history_search_finds_task_answer_and_file_ignoring_accents(self):
        record = {
            "task": "Análise científica de materiais",
            "execution_output": "Relatório sobre nanofluidos concluído.",
            "conversation": [{"role": "user", "text": "Inclua eficiência térmica"}],
            "artifacts": [r"C:\tarefas\relatorio-final.pdf"],
            "model": "Sol — Médio", "status": "Concluída",
            "finished_at": "19/09/2026", "skills": ["pesquisa-cientifica"],
        }
        empty = {key: "" for key in ("date", "model", "status", "skill", "task")}
        for query in ("analise cientifica", "nanofluidos", "eficiencia termica",
                      "relatorio-final.pdf"):
            filters = dict(empty, task=query)
            self.assertTrue(gate.execution_record_matches(record, filters), query)
        self.assertFalse(gate.execution_record_matches(
            record, dict(empty, task="contrato societário")))

    def test_reading_text_preserves_and_normalizes_scientific_symbols(self):
        clean = GateApp.clean_reading_text(
            "Luz — visível. O₂•⁻, H₂O₂, •OH, O_2^{\\bullet -}, x^2, A\\cdotB e \\alpha.")
        self.assertNotIn("—", clean)
        self.assertIn("O₂•⁻", clean)
        self.assertIn("H₂O₂", clean)
        self.assertIn("O₂•⁻", clean)
        self.assertIn("x²", clean)
        self.assertIn("A·B", clean)
        self.assertIn("α", clean)

    def test_reading_marks_middle_dot_as_a_technical_symbol(self):
        class RecordingText:
            def __init__(self):
                self.calls = []

            def insert(self, *args):
                self.calls.append(args)

        widget = RecordingText()
        GateApp.insert_markdown_inline(widget, r"A\cdotB")

        dot_calls = [call for call in widget.calls if len(call) >= 3 and call[1] == "·"]
        self.assertEqual(len(dot_calls), 1)
        self.assertEqual(dot_calls[0][2], "symbol")

    def test_reading_turns_markdown_and_plain_urls_into_safe_links(self):
        class RecordingText:
            def __init__(self):
                self.calls = []
                self.bindings = {}

            def insert(self, *args):
                self.calls.append(args)

            def tag_configure(self, *_args, **_kwargs):
                pass

            def tag_bind(self, tag, event, callback):
                self.bindings[(tag, event)] = callback

            def configure(self, **_kwargs):
                pass

        widget = RecordingText()
        GateApp.insert_markdown_inline(
            widget,
            "Veja [documentação](https://example.com/docs) e https://openai.com/teste.")

        linked_text = [call[1] for call in widget.calls
                       if len(call) >= 3 and "web_link" in call[2]]
        self.assertEqual(linked_text, ["documentação", "https://openai.com/teste"])
        self.assertEqual(len([key for key in widget.bindings if key[1] == "<Button-1>"]), 2)
        self.assertTrue(GateApp.is_safe_web_url("https://example.com/caminho"))
        self.assertFalse(GateApp.is_safe_web_url("file:///C:/segredo.txt"))
        self.assertFalse(GateApp.is_safe_web_url("https://usuario:senha@example.com"))

    def test_execution_workspace_is_unique_and_inside_projects_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "projetos"
            workspace = gate.execution_workspace(root, "abcdef123456", "Criar relatório técnico")
            self.assertTrue(workspace.is_dir())
            self.assertEqual(workspace.parent, root.resolve())

    def test_created_skill_is_installed_in_program_library(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "tarefa"
            write_skill(workspace / "skill-output", "minha-skill", "Uma skill de teste")
            original = gate.managed_skills_dir
            library = root / "skills"
            gate.managed_skills_dir = lambda create=True: library
            try:
                installed, issues = gate.import_generated_skills(
                    "Crie uma skill para testes", workspace)
            finally:
                gate.managed_skills_dir = original
            self.assertFalse(issues)
            self.assertEqual(len(installed), 1)
            self.assertTrue((installed[0] / "SKILL.md").is_file())

    def test_backup_contains_projects_skills_and_records(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            data = root / "CodexModelGate-Dados"
            for folder, filename in (("projetos", "resultado.txt"), ("skills", "SKILL.md"), ("registro", "registro.md")):
                target = data / folder
                target.mkdir(parents=True)
                (target / filename).write_text(folder, encoding="utf-8")
            original = gate.app_data_dir
            gate.app_data_dir = lambda: data
            try:
                backup = gate.create_data_backup(root / "backup.zip")
                preview = gate.inspect_data_backup(backup)
            finally:
                gate.app_data_dir = original
            with zipfile.ZipFile(backup) as archive:
                names = set(archive.namelist())
                self.assertEqual(
                    names,
                    {"p/000001.txt", "s/000001.md", "r/000001.md",
                     "backup-manifest.json", "LEIA-ME-BACKUP.txt"},
                )
                self.assertLessEqual(max(len(name) for name in names), 24)
                manifest = json.loads(archive.read("backup-manifest.json"))
                self.assertEqual(manifest["estrutura"], "compacta-sem-pastas-aninhadas")
                self.assertEqual(
                    {item["caminho_original"] for item in manifest["arquivos"]},
                    {"projetos/resultado.txt", "skills/SKILL.md", "registro/registro.md"},
                )
            self.assertEqual(preview["files"], 3)
            self.assertEqual(preview["counts"], {
                "projetos": 1, "skills": 1, "registro": 1,
                "configuracoes": 0})

    def test_skill_search_matches_part_of_name_ignoring_case_and_accents(self):
        skills = [
            {"name": "desenvolver-apps-windows-desktop", "path": "one"},
            {"name": "Criar-Cartões-Empresariais", "path": "two"},
            {"name": "quimica-coordenacao", "path": "three"},
        ]
        self.assertEqual(
            [skill["name"] for skill in gate.filter_skills_by_name(skills, "WINDOWS")],
            ["desenvolver-apps-windows-desktop"],
        )
        self.assertEqual(
            [skill["name"] for skill in gate.filter_skills_by_name(skills, "cartoes")],
            ["Criar-Cartões-Empresariais"],
        )
        self.assertEqual(gate.filter_skills_by_name(skills, ""), skills)

    def test_restore_compact_backup_on_a_new_computer_data_folder(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_data = root / "computer-a" / "CodexModelGate"
            target_data = root / "computer-b" / "CodexModelGate"
            (source_data / "projetos" / "tarefa-a").mkdir(parents=True)
            (source_data / "projetos" / "tarefa-a" / "resultado.txt").write_text(
                "resultado", encoding="utf-8")
            (source_data / "skills" / "minha-skill").mkdir(parents=True)
            (source_data / "skills" / "minha-skill" / "SKILL.md").write_text(
                "skill", encoding="utf-8")
            (source_data / "registro").mkdir(parents=True)
            (source_data / "registro" / "registro.md").write_text("registro", encoding="utf-8")
            (source_data / "settings.json").write_text("{}", encoding="utf-8")
            original = gate.app_data_dir
            try:
                gate.app_data_dir = lambda: source_data
                backup = gate.create_data_backup(root / "gate-backup.zip")
                gate.app_data_dir = lambda: target_data
                result = gate.restore_data_backup(backup)
            finally:
                gate.app_data_dir = original
            self.assertEqual(result["restored"], 4)
            self.assertEqual((target_data / "projetos" / "tarefa-a" / "resultado.txt").read_text(encoding="utf-8"), "resultado")
            self.assertEqual((target_data / "skills" / "minha-skill" / "SKILL.md").read_text(encoding="utf-8"), "skill")
            self.assertTrue((target_data / "registro" / "registro.md").is_file())
            self.assertTrue((target_data / "settings.json").is_file())

    def test_restore_without_overwrite_preserves_existing_skill_folder(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source_data = root / "source"
            target_data = root / "target"
            (source_data / "skills" / "duplicada").mkdir(parents=True)
            (source_data / "skills" / "duplicada" / "SKILL.md").write_text(
                "nova", encoding="utf-8")
            target_skill = target_data / "skills" / "duplicada"
            target_skill.mkdir(parents=True)
            (target_skill / "SKILL.md").write_text("antiga", encoding="utf-8")
            original = gate.app_data_dir
            try:
                gate.app_data_dir = lambda: source_data
                backup = gate.create_data_backup(root / "gate-backup.zip")
                gate.app_data_dir = lambda: target_data
                result = gate.restore_data_backup(backup, overwrite=False)
            finally:
                gate.app_data_dir = original
            self.assertEqual(result["overwritten"], 0)
            self.assertEqual((target_skill / "SKILL.md").read_text(encoding="utf-8"), "antiga")
            restored = target_data / "skills" / "duplicada-restaurado-1" / "SKILL.md"
            self.assertEqual(restored.read_text(encoding="utf-8"), "nova")

    def test_restore_rejects_backup_path_outside_gate_data(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            backup = root / "invalido.zip"
            with zipfile.ZipFile(backup, "w") as archive:
                archive.writestr("projetos/../../fora.txt", "não escrever")
            original = gate.app_data_dir
            gate.app_data_dir = lambda: root / "target"
            try:
                with self.assertRaises(ValueError):
                    gate.restore_data_backup(backup)
            finally:
                gate.app_data_dir = original


class ContinuationStateTests(unittest.TestCase):
    def setUp(self):
        self._data_directory = tempfile.TemporaryDirectory()
        self._original_app_data_dir = gate.app_data_dir
        gate.app_data_dir = lambda: Path(self._data_directory.name)

    def tearDown(self):
        gate.app_data_dir = self._original_app_data_dir
        self._data_directory.cleanup()

    def test_save_load_find_and_clear_task_local_continuation(self):
        with tempfile.TemporaryDirectory() as temporary:
            projects = Path(temporary) / "projetos"
            older_workspace = projects / "tarefa-antiga"
            newer_workspace = projects / "tarefa-nova"
            older_workspace.mkdir(parents=True)
            newer_workspace.mkdir()

            older_path = gate.save_continuation_state(older_workspace, {
                "session_id": "thread-antiga",
                "question": "Qual arquivo deve ser usado?",
            })
            newer_path = gate.save_continuation_state(newer_workspace, {
                "session_id": "thread-nova",
                "question": "Qual formato você prefere?",
            })

            loaded = gate.load_continuation_state(newer_workspace)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded["session_id"], "thread-nova")
            self.assertEqual(loaded["project_folder"], str(newer_workspace.resolve()))
            self.assertEqual(older_path.name, gate.CONTINUATION_FILE_NAME)
            self.assertEqual(older_path.parent.name, ".codex-model-gate")

            now = time.time()
            os.utime(older_path, (now - 20, now - 20))
            os.utime(newer_path, (now, now))
            latest = gate.find_latest_pending_continuation(projects)
            self.assertIsNotNone(latest)
            self.assertEqual(latest["session_id"], "thread-nova")

            gate.clear_continuation_state(newer_workspace)
            self.assertIsNone(gate.load_continuation_state(newer_workspace))
            remaining = gate.find_latest_pending_continuation(projects)
            self.assertIsNotNone(remaining)
            self.assertEqual(remaining["session_id"], "thread-antiga")

    def test_load_rejects_state_that_points_to_another_workspace(self):
        with tempfile.TemporaryDirectory() as temporary:
            projects = Path(temporary) / "projetos"
            workspace = projects / "tarefa"
            unrelated = Path(temporary) / "fora"
            workspace.mkdir(parents=True)
            unrelated.mkdir()
            path = gate.save_continuation_state(workspace, {
                "session_id": "thread-segura",
                "question": "Posso continuar?",
            })
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["project_folder"] = str(unrelated)
            path.write_text(json.dumps(payload), encoding="utf-8")

            self.assertIsNone(gate.load_continuation_state(workspace))

    def test_reading_a_missing_continuation_never_creates_a_task_folder(self):
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "projetos" / "tarefa-sem-pendencia"
            workspace.mkdir(parents=True)

            self.assertFalse((workspace / ".codex-model-gate").exists())
            self.assertIsNone(gate.load_continuation_state(workspace))
            self.assertFalse((workspace / ".codex-model-gate").exists())

    def test_global_index_restores_a_continuation_from_a_custom_projects_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            custom_root = Path(temporary) / "outros-projetos"
            workspace = custom_root / "tarefa"
            workspace.mkdir(parents=True)
            gate.save_continuation_state(workspace, {
                "session_id": "thread-personalizada",
                "question": "Em qual formato devo salvar?",
            })

            restored = gate.find_latest_pending_continuation(
                Path(temporary) / "projetos-padrao")

            self.assertIsNotNone(restored)
            self.assertEqual(restored["session_id"], "thread-personalizada")
            portable_root = Path(temporary) / "projetos-portateis"
            portable_root.mkdir()
            self.assertIsNone(gate.find_latest_pending_continuation(
                portable_root, allow_indexed_external=False))


class ScheduledTaskTests(unittest.TestCase):
    def setUp(self):
        self._directory = tempfile.TemporaryDirectory()
        self._original = gate.app_data_dir
        self._original_settings = gate.app_settings_path
        gate.app_data_dir = lambda: Path(self._directory.name)
        gate.app_settings_path = lambda: Path(self._directory.name) / "settings.json"

    def tearDown(self):
        gate.app_data_dir = self._original
        gate.app_settings_path = self._original_settings
        self._directory.cleanup()

    def test_due_daily_task_is_advanced_and_one_time_task_is_retired(self):
        now = datetime.now().astimezone().replace(second=0, microsecond=0)
        daily = {"id": "daily", "task": "Relatório", "recurrence": "daily",
                 "next_run": (now - timedelta(minutes=1)).isoformat()}
        once = {"id": "once", "task": "Revisão", "recurrence": "once",
                "next_run": (now - timedelta(minutes=1)).isoformat()}
        gate.save_scheduled_tasks([daily, once])

        self.assertEqual({item["id"] for item in gate.due_scheduled_tasks(now)},
                         {"daily", "once"})
        advanced = gate.advance_scheduled_task(daily, now)
        self.assertIsNotNone(advanced)
        self.assertGreater(datetime.fromisoformat(advanced["next_run"]), now)
        self.assertIsNone(gate.advance_scheduled_task(once, now))


class GatePackageTests(unittest.TestCase):
    def test_export_and_import_restores_workspace_without_transferring_session(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original_records_dir = gate.records_dir
            gate.records_dir = lambda: root / "registro"
            (root / "registro").mkdir()
            workspace = root / "origem"
            workspace.mkdir()
            (workspace / "resultado.txt").write_text("resultado", encoding="utf-8")
            record_file = root / "record.md"
            record_file.write_text(gate._record_markdown({
                "id": "original", "task": "Criar resumo", "project_folder": str(workspace),
                "session_id": "thread-original", "conversation": []}), encoding="utf-8")
            package = gate.export_task_package(
                {"record_file": str(record_file), "project_folder": str(workspace)}, root / "tarefa.gate")

            try:
                imported = gate.import_task_package(package, root / "projetos")
            finally:
                gate.records_dir = original_records_dir

            self.assertTrue(Path(imported["record_file"]).is_file())
            self.assertEqual(imported["session_id"], "")
            self.assertTrue((Path(imported["project_folder"]) / "resultado.txt").is_file())


class TokenCostTests(unittest.TestCase):
    def test_usage_and_cost_include_cached_input_and_output(self):
        raw = '{"type":"turn.completed","usage":{"input_tokens":1000000,"cached_input_tokens":500000,"output_tokens":1000000,"reasoning_tokens":200}}'
        usage = gate.extract_codex_token_usage(raw)
        self.assertEqual(usage["reasoning"], 200)
        self.assertAlmostEqual(gate.estimate_token_cost("terra", usage, "USD"), 13.1)
        self.assertAlmostEqual(gate.estimate_token_cost("terra", usage, "BRL"), 13.1 * 5.1575)


class CodexContinuationProtocolTests(unittest.TestCase):
    def test_completed_task_followup_prompt_preserves_conversation_intent(self):
        prompt = gate.build_task_followup_prompt(
            "Revise o relatório e acrescente uma conclusão.")

        self.assertIn("MESMA TAREFA", prompt)
        self.assertIn("mesma tarefa", prompt.lower())
        self.assertIn(gate.CONTINUATION_MARKER, prompt)
        with self.assertRaises(ValueError):
            gate.build_task_followup_prompt("   ")

    def test_followup_context_includes_only_active_attachments(self):
        prompt = gate.build_task_followup_prompt("Revise o arquivo.", [
            {"staged": ".codex-model-gate/anexos/novo.pdf", "active": True},
            {"staged": ".codex-model-gate/anexos/antigo.pdf", "active": False},
        ])

        self.assertIn("novo.pdf", prompt)
        self.assertNotIn("antigo.pdf", prompt)

    def test_continuation_staging_preserves_existing_files(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            workspace = root / "tarefa"
            workspace.mkdir()
            source = root / "apoio.txt"
            source.write_text("contexto", encoding="utf-8")

            staged = gate.stage_continuation_attachments(workspace, [source])

            self.assertEqual(len(staged), 1)
            self.assertTrue(staged[0]["active"])
            self.assertTrue((workspace / staged[0]["staged"]).is_file())

    def test_record_model_settings_supports_new_and_older_records(self):
        self.assertEqual(
            gate.record_model_settings({"model_key": "sol", "effort": "medium"}),
            ("sol", "medium"))
        self.assertEqual(
            gate.record_model_settings({"model": "Astra — Extra alto"}),
            ("astra", "xhigh"))
        with self.assertRaises(ValueError):
            gate.record_model_settings({"model": "modelo desconhecido"})

    def test_execution_record_preserves_session_and_conversation(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            original_records_dir = gate.records_dir
            gate.records_dir = lambda: root
            try:
                path = gate.write_execution_record({
                    "id": "registro-continuo",
                    "task": "Criar relatório",
                    "session_id": "thread-123",
                    "conversation": [
                        {"role": "user", "text": "Criar relatório", "at": "inicio"},
                        {"role": "assistant", "text": "Relatório criado.", "at": "fim"},
                    ],
                })
                records = gate.read_execution_records()
            finally:
                gate.records_dir = original_records_dir

            self.assertTrue(path.is_file())
            self.assertEqual(records[0]["session_id"], "thread-123")
            self.assertEqual(len(records[0]["conversation"]), 2)
            visible = path.read_text(encoding="utf-8")
            self.assertIn("Conversa pode ser retomada:** Sim", visible)
            self.assertIn("## Conversa da tarefa", visible)

    def test_parses_jsonl_session_and_agent_messages(self):
        raw_output = "\n".join((
            '{"type":"thread.started","thread_id":"thread-123"}',
            '{"type":"item.completed","item":{"type":"agent_message","content":[{"type":"output_text","text":"Primeira resposta."}]}}',
            '{"type":"item.completed","item":{"type":"assistant_message","text":"Segunda resposta."}}',
            "diagnóstico não estruturado",
        ))

        session_id, visible = gate.parse_codex_json_output(raw_output)

        self.assertEqual(session_id, "thread-123")
        self.assertIn("Primeira resposta.", visible)
        self.assertIn("Segunda resposta.", visible)
        self.assertNotIn("diagnóstico não estruturado", visible)

    def test_jsonl_parser_uses_non_json_output_as_diagnostic_when_no_message_exists(self):
        session_id, visible = gate.parse_codex_json_output(
            '{"type":"thread.started","thread_id":"thread-sem-mensagem"}\nfalha útil')

        self.assertEqual(session_id, "thread-sem-mensagem")
        self.assertEqual(visible, "falha útil")

    def test_turn_lifecycle_events_do_not_pollute_the_user_answer(self):
        self.assertEqual(
            gate.codex_event_display_text('{"type":"turn.started"}'), "")
        self.assertEqual(
            gate.codex_event_display_text('{"type":"turn.completed"}'), "")
        self.assertEqual(
            gate.codex_event_display_text(
                '{"type":"item.completed","item":{"type":"agent_message","text":"Resposta final."}}'),
            "Resposta final.\n")

    def test_extracts_only_an_explicit_pending_question_marker(self):
        marked = gate.extract_continuation_question(
            "Preciso de uma decisão.\n[[gate_continue: Qual formato\n você prefere?]]")
        unmarked_question = gate.extract_continuation_question(
            "Antes de prosseguir, você confirma que posso substituir o arquivo?")

        self.assertEqual(marked, "Qual formato você prefere?")
        self.assertIsNone(unmarked_question)
        self.assertIsNone(gate.extract_continuation_question("Tudo pronto?"))

    def test_exec_and_resume_commands_keep_the_recorded_safe_context(self):
        execute = gate.build_codex_exec_command("gpt-5.6-terra", "high")
        resume = gate.build_codex_resume_command(
            "thread-123", "gpt-5.6-terra", "high")

        sandbox_index = execute.index("--sandbox")
        self.assertEqual(execute[sandbox_index + 1], "workspace-write")
        self.assertIn("--skip-git-repo-check", execute)
        self.assertIn("--json", execute)
        self.assertIn("--skip-git-repo-check", resume)
        self.assertIn("--json", resume)
        self.assertIn("thread-123", resume)
        self.assertEqual(resume[resume.index("--sandbox") + 1], "workspace-write")
        self.assertIn("model_reasoning_effort=high", resume)
        self.assertLess(resume.index("--sandbox"), resume.index("resume"))
        self.assertNotIn("--last", execute)
        self.assertNotIn("--last", resume)
        self.assertNotIn("--add-dir", resume)
        with self.assertRaises(ValueError):
            gate.build_codex_resume_command("--last", "gpt-5.6-terra", "high")

    def test_browser_authorization_adds_task_scoped_mcp_server(self):
        with tempfile.TemporaryDirectory() as temporary:
            command = gate.build_codex_exec_command(
                "gpt-5.6-terra", "medium", Path(temporary))
        joined = "\n".join(command)
        self.assertIn("mcp_servers.gate_browser.command", joined)
        self.assertIn("--mcp-browser-server", joined)
        self.assertIn("mcp_servers.gate_browser.cwd", joined)
        self.assertIn("default_tools_approval_mode=\"approve\"", joined)
        self.assertIn("mcp_servers.gate_browser.required=false", joined)
        self.assertNotIn(
            "mcp_servers.gate_browser",
            "\n".join(gate.build_codex_exec_command(
                "gpt-5.6-terra", "medium")))

    def test_embedded_browser_mcp_lists_its_tools_over_stdio(self):
        requests = "\n".join((
            json.dumps({"jsonrpc": "2.0", "id": 1, "method": "initialize",
                        "params": {"protocolVersion": "2024-11-05"}}),
            json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}),
            json.dumps({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}),
            "",
        ))
        completed = subprocess.run(
            [sys.executable, str(Path(gate.__file__).with_name("gate_browser_mcp.py"))],
            input=requests, text=True, encoding="utf-8", capture_output=True,
            timeout=10)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        responses = [json.loads(line) for line in completed.stdout.splitlines()]
        names = {item["name"] for item in responses[1]["result"]["tools"]}
        self.assertEqual(names, {
            "gate_browser_search", "gate_browser_open",
            "gate_browser_snapshot", "gate_browser_close"})


class ManualSkillInstallationTests(unittest.TestCase):
    def test_manual_install_creates_a_new_copy_without_overwriting_existing_skill(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            library = root / "skills"
            incoming = root / "recebida"
            write_skill(library, "minha-skill", "Versão original")
            write_skill(incoming, "minha-skill", "Versão importada")
            source = incoming / "minha-skill"
            (source / "referencia.txt").write_text("conteúdo da skill", encoding="utf-8")
            existing = library / "minha-skill"
            original_content = (existing / "SKILL.md").read_text(encoding="utf-8")
            original_managed_skills_dir = gate.managed_skills_dir
            gate.managed_skills_dir = lambda create=True: library
            try:
                installed = gate.install_skill(source)
            finally:
                gate.managed_skills_dir = original_managed_skills_dir

            self.assertNotEqual(installed, existing)
            self.assertTrue((installed / "SKILL.md").is_file())
            self.assertTrue((installed / "referencia.txt").is_file())
            self.assertEqual((existing / "SKILL.md").read_text(encoding="utf-8"), original_content)
            self.assertEqual(gate.parse_skill(installed / "SKILL.md")["description"], "Versão importada")


class PortableStorageTests(unittest.TestCase):
    def test_formats_sizes_and_calculates_portable_capacity(self):
        self.assertEqual(gate.format_storage_size(-1), "0 B")
        self.assertEqual(gate.format_storage_size(1024), "1.0 KB")
        self.assertEqual(gate.format_storage_size(1536 * 1024), "1.5 MB")

        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            program = root / "pendrive"
            data = program / "CodexModelGate-Dados"
            program.mkdir()
            data.mkdir()
            original_program_dir = gate.program_dir
            original_app_data_dir = gate.app_data_dir
            original_directory_size = gate.directory_size
            original_disk_usage = gate.shutil.disk_usage
            additional = 96 * 1024 * 1024
            required = gate.PORTABLE_MIN_FREE_BYTES + additional
            gate.program_dir = lambda: program
            gate.app_data_dir = lambda: data
            gate.directory_size = lambda path: 24 if Path(path) == data else 12
            gate.shutil.disk_usage = lambda path: SimpleNamespace(
                free=required - 1, total=2 * required)
            try:
                estimate = gate.portable_storage_estimate(additional)
            finally:
                gate.program_dir = original_program_dir
                gate.app_data_dir = original_app_data_dir
                gate.directory_size = original_directory_size
                gate.shutil.disk_usage = original_disk_usage

            self.assertEqual(estimate["app_size"], 12)
            self.assertEqual(estimate["data_size"], 24)
            self.assertEqual(estimate["additional_size"], additional)
            self.assertEqual(estimate["required_free"], required)
            self.assertEqual(estimate["free"], required - 1)
            self.assertFalse(estimate["sufficient"])

    def test_portable_codex_environment_and_skills_stay_inside_data_root(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "pendrive"
            data = root / "CodexModelGate-Dados"
            projects = data / "projetos"
            external = Path(temporary) / "skills-do-host"
            projects.mkdir(parents=True)
            external.mkdir()
            original_portable = gate.is_portable_mode
            original_data = gate.app_data_dir
            original_managed = gate.managed_skills_dir
            gate.is_portable_mode = lambda: True
            gate.app_data_dir = lambda: data
            gate.managed_skills_dir = lambda create=True: data / "skills"
            try:
                environment = gate.codex_process_environment()
                roots = gate.skill_roots(projects, [external])
            finally:
                gate.is_portable_mode = original_portable
                gate.app_data_dir = original_data
                gate.managed_skills_dir = original_managed

            self.assertEqual(environment["CODEX_HOME"], str(data / "codex-cli"))
            self.assertEqual(environment["TEMP"], str(data / "temporarios"))
            self.assertTrue((data / "codex-cli").is_dir())
            self.assertTrue((data / "temporarios").is_dir())
            self.assertTrue(all(gate._path_is_within(path, data) for path in roots))
            self.assertNotIn(external.resolve(), roots)


if __name__ == "__main__":
    unittest.main()
