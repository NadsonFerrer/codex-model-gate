#!/usr/bin/env python3
"""Local graphical front-end for reliable Codex CLI decisions on Windows."""
from __future__ import annotations

import json
import os
import queue
import re
import subprocess
import sys
import threading
import time as clock
import traceback
import tkinter as tk
import uuid
import webbrowser
import zipfile
from datetime import date, datetime, timedelta
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk
from urllib.parse import urlparse

import codex_model_gate as gate
import gate_i18n
from gate_models import APP_VERSION, CLI_DOWNLOAD_URL, CLI_CHANGELOG_URL, model_label, model_key, local_catalog, latest_cli_release
from gate_execution import AuthorizedTask, ProcessSupervisor, prepare_task
from gate_selection import select_skills_with_ai, attachment_signature
from gate_storage import atomic_write_text, load_json
from gate_usage import usage_records

_MESSAGEBOX_FUNCTIONS = {
    name: getattr(messagebox, name) for name in (
        "showinfo", "showwarning", "showerror", "askyesno", "askyesnocancel")
}
_SIMPLEDIALOG_ASKSTRING = simpledialog.askstring
_FILEDIALOG_FUNCTIONS = {
    name: getattr(filedialog, name) for name in (
        "askdirectory", "asksaveasfilename", "askopenfilename", "askopenfilenames")
}

try:
    from PIL import Image, ImageTk
except ImportError:  # The list remains useful even in a minimal installation.
    Image = ImageTk = None


CODEX_WINDOWS_INSTALLER = "https://chatgpt.com/codex/install.ps1"
CODEX_INSTALL_GUIDE_URL = CLI_DOWNLOAD_URL

UI_COLORS = {
    "background": "#F2F7FA",
    "surface": "#FFFFFF",
    "primary": "#136F8A",
    "primary_hover": "#0D5A70",
    "primary_dark": "#123B5D",
    "accent": "#2A9D78",
    "accent_soft": "#E5F5EF",
    "blue_soft": "#E6F2F7",
    "border": "#B9CDD8",
    "text": "#19333F",
    "muted": "#5D727D",
    "selection": "#CBE8F2",
}
TASK_TEMPLATES = {
    "Escolha um modelo...": "",
    "Criar documento": "Crie um documento sobre [tema], com [seções desejadas], em formato [DOCX/PDF]. Use linguagem [tom] e salve o resultado final na pasta da tarefa.",
    "Analisar arquivo": "Analise os arquivos anexados. Explique os principais achados, apresente pontos de atenção e crie um resumo em [formato desejado].",
    "Gerar imagem": "Crie uma imagem de [assunto], para uso em [finalidade], com estilo [estilo], proporção [proporção] e texto [se houver]. Salve o arquivo final na pasta da tarefa.",
    "Pesquisar referências": "Pesquise referências confiáveis sobre [tema]. Entregue uma síntese objetiva e uma lista de fontes verificáveis em [formato de citação].",
    "Organizar dados": "Organize os dados ou arquivos anexados. Explique os critérios usados, identifique inconsistências e gere [arquivo final desejado].",
}
from gate_manuals import MANUALS
USER_MANUAL = MANUALS['pt-BR']


def hidden_windows_process_options() -> dict:
    """Prevent a console window from flashing for background CLI work."""
    if os.name != "nt":
        return {}
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startupinfo.wShowWindow = subprocess.SW_HIDE
    return {
        "creationflags": getattr(subprocess, "CREATE_NO_WINDOW", 0),
        "startupinfo": startupinfo,
    }


def add_vertical_scrollbar(container, widget):
    """Attach a standard Windows scrollbar, including its arrow buttons."""
    if isinstance(widget, ttk.Treeview):
        horizontal = ttk.Scrollbar(container, orient='horizontal', command=widget.xview)
        widget.configure(xscrollcommand=horizontal.set)
        horizontal.pack(side='bottom', fill='x')
    scrollbar = ttk.Scrollbar(container, orient="vertical", command=widget.yview)
    widget.configure(yscrollcommand=scrollbar.set)
    scrollbar.pack(side="right", fill="y")
    widget.pack(side="left", fill="both", expand=True)
    return scrollbar


class GateApp(tk.Tk):
    def report_callback_exception(self, exc_type, exc_value, exc_traceback):
        """Surface Tk callback failures that a windowed build would hide."""
        details = "".join(traceback.format_exception(
            exc_type, exc_value, exc_traceback))
        try:
            workspace = getattr(self, "cwd", None)
            folder = (gate.gate_dir(workspace) if isinstance(workspace, Path) and
                      workspace.is_dir() else gate.app_data_dir())
            with (folder / "gui-error.txt").open("a", encoding="utf-8") as log:
                log.write(details + "\n")
        except OSError:
            pass
        try:
            self.status.set("A interface encontrou uma falha. A tarefa não foi confirmada como concluída.")
            messagebox.showerror("Falha na interface", str(exc_value))
        except (AttributeError, tk.TclError):
            pass

    def __init__(self):
        super().__init__()
        saved_settings = gate.load_app_settings()
        self.language = gate_i18n.normalize_language(
            str(saved_settings.get("language") or "en"))
        self.install_localized_dialogs()
        self.title(self.tr("Codex Model Gate — Decisão Confiável de IA") +
                   f" v{APP_VERSION}")
        self.geometry(f"{min(1040, self.winfo_screenwidth()-80)}x{min(900, self.winfo_screenheight()-100)}")
        self.minsize(620, 500)
        self.projects_root = gate.projects_dir()
        self.cwd = self.projects_root
        self.pending, self.skills, self.filtered_skill_items, self.artifacts = None, [], [], []
        self.artifact_preview_image = None
        self.current_session_id = None
        self.pending_question = None
        self.continuation_mode = "question"
        self.conversation_record_path = None
        self.conversation_turns = []
        self.sent_continuation_message = ""
        self.current_followup_request = ""
        self.last_response_text = ""
        self.current_token_usage = None
        self.consumption_var = tk.StringVar(
            value="Consumo desta tarefa: aguardando execução do Codex.")
        self.continuation_window = None
        self.continuation_answer = None
        self.last_continuation_answer = ""
        self.continuation_in_flight = False
        self.record_items = {}
        self.record_cache = None
        self.cli_executable = None
        self.cli_version = None
        self.cli_signature = None
        self.record_artifact_items = []
        self.files_context_var = tk.StringVar(
            value="Selecione uma tarefa na aba “Tarefas anteriores” para ver seus arquivos.")
        self.show_only_unqualified = False
        self.record_filter_vars = {key: tk.StringVar() for key in (
            "date", "model", "status", "skill", "task")}
        self.record_filter_status = tk.StringVar(
            value="Carregando registros...")
        self.usage_period_var = tk.StringVar(value="Este mês")
        self.usage_currency_var = tk.StringVar(value="Automática")
        self.usage_model_var = tk.StringVar(value="Todos os modelos")
        self.recalculate_costs_var = tk.BooleanVar(value=False)
        self.usage_summary_var = tk.StringVar(value="Carregando consumo registrado...")
        self.usage_records_var = tk.StringVar(value="")
        self.usage_range_var = tk.StringVar(value="")
        self.usage_excluded_var = tk.StringVar(value="")
        self.usage_custom_error = False
        self.history_search_after_id = None
        self.auto_open_outputs_var = tk.BooleanVar(value=bool(saved_settings.get("auto_open_outputs",False)))
        self.attachments = []
        self.active_skill_items = []
        self.running = False
        self.busy_operation = False
        self.pending_jobs = 0
        self.exclusive_jobs = 0
        self.supervisor = ProcessSupervisor()
        self._history_request = 0
        self._record_reload = True
        self._completion_data = None
        self.action_executed = False
        self.selecting_skills = False
        self.cancel_requested = False
        self.active_process = None
        self.before_files = {}
        self.events = queue.Queue()
        self.run_id = None
        self.record_note_path = None
        self.execution_started_at = None
        self.execution_started_monotonic = None
        self.execution_duration_seconds = None
        self.estimated_total_seconds = None
        self.model_var, self.effort_var = tk.StringVar(), tk.StringVar()
        self.decision_model_card_var = tk.StringVar(value="Analise a tarefa")
        self.decision_effort_card_var = tk.StringVar(value="—")
        self.decision_risk_card_var = tk.StringVar(value="—")
        self.decision_skills_card_var = tk.StringVar(value="—")
        self.simple_progress_var = tk.StringVar(
            value="Aguardando você descrever uma tarefa.")
        self.cli_status_var = tk.StringVar()
        self.portable_storage_var = tk.StringVar()
        self.policy_var = tk.StringVar(value="equilibrada")
        self.quality_var = tk.StringVar(value="Não avaliado")
        self.ui_mode_var = tk.BooleanVar(value=False)
        self.browser_research_var = tk.BooleanVar(value=False)
        self.browser_query_var = tk.StringVar()
        self.template_var = tk.StringVar(value="Escolha um modelo...")
        self.decision_checklist_var = tk.StringVar(
            value="Depois de analisar a tarefa, confirme o resultado esperado, os anexos e a pasta de destino.")
        self.manual_skills_var = tk.BooleanVar(value=False)
        self.skill_search_var = tk.StringVar()
        self.skill_search_status = tk.StringVar(value="")
        saved_library = gate.saved_skill_library()
        self.skill_library_var = tk.StringVar(
            value=str(saved_library) if saved_library else "")
        self.skill_library_status = tk.StringVar(
            value="Nenhuma biblioteca de skills vinculada.")
        self._build()
        self.localize_interface()
        from gate_widgets import install_flow_rows
        install_flow_rows(self)
        self.task.bind("<<Modified>>", self.on_task_modified, add="+")
        draft = saved_settings.get('draft', {})
        if isinstance(draft, dict):
            self.task.insert('1.0', str(draft.get('task') or ''))
            self.attachments = [Path(p) for p in draft.get('attachments', []) if isinstance(p, str) and Path(p).is_file()]
            self.refresh_attachments()
            if draft.get('root'):
                self.path_var.set(str(draft['root']))
        self.task.edit_modified(False)
        self.update_action_buttons()
        self.apply_ui_mode()
        self.after(100, self.refresh_skills)
        self.after(150, self.load_history)
        self.after(50, self.refresh_codex_cli_status)
        self.refresh_portable_storage_status()
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(100, self.poll_events)
        self.after(250, self.restore_pending_continuation)
        self.after(1000, self.check_scheduled_tasks)
        self.after(500, self.show_onboarding_if_needed)

    def _build(self):
        style = ttk.Style(self)
        self.style = style
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        colors = UI_COLORS
        self.configure(bg=colors["background"])
        style.configure("TFrame", background=colors["surface"])
        style.configure("TLabel", background=colors["surface"], foreground=colors["text"])
        style.configure("TCheckbutton", background=colors["surface"], foreground=colors["text"])
        style.map("TCheckbutton", background=[("active", colors["surface"])] ,
                  foreground=[("disabled", colors["muted"])])
        style.configure("TLabelframe", background=colors["surface"], bordercolor=colors["border"],
                        lightcolor=colors["border"], darkcolor=colors["border"], relief="solid")
        style.configure("TLabelframe.Label", background=colors["surface"],
                        foreground=colors["primary_dark"], font=("Segoe UI", 9, "bold"))
        style.configure("Step.TLabel", padding=(10, 7), font=("Segoe UI", 9, "bold"),
                        background=colors["blue_soft"], foreground=colors["primary_dark"])
        style.configure("Card.TLabelframe", background=colors["blue_soft"],
                        bordercolor=colors["border"], relief="solid")
        style.configure("Card.TLabelframe.Label", background=colors["blue_soft"])
        style.configure("CardTitle.TLabel", background=colors["blue_soft"],
                        foreground=colors["muted"], font=("Segoe UI", 9, "bold"))
        style.configure("CardValue.TLabel", background=colors["blue_soft"],
                        foreground=colors["primary_dark"], font=("Segoe UI", 12, "bold"))
        style.configure("Hint.TLabel", foreground=colors["muted"], font=("Segoe UI", 9))
        style.configure("TButton", padding=(10, 6), background=colors["surface"],
                        foreground=colors["primary_dark"], bordercolor=colors["border"])
        style.map("TButton", background=[("active", colors["blue_soft"]),
                                         ("pressed", colors["selection"])],
                  foreground=[("disabled", colors["muted"])])
        style.configure("Primary.TButton", font=("Segoe UI", 10, "bold"), padding=(14, 9),
                        background=colors["primary"], foreground="#FFFFFF",
                        bordercolor=colors["primary"])
        style.map("Primary.TButton", background=[("active", colors["primary_hover"]),
                                                  ("pressed", colors["primary_dark"]),
                                                  ("disabled", "#9BB9C5")],
                  foreground=[("disabled", "#F1F5F7")])
        style.configure("WaitingAction.TButton", font=("Segoe UI", 10, "bold"),
                        padding=(14, 9), background=colors["blue_soft"],
                        foreground=colors["primary_dark"], bordercolor=colors["border"])
        style.map("WaitingAction.TButton",
                  background=[("disabled", colors["blue_soft"]),
                              ("active", colors["selection"])])
        style.configure("ActivatedAction.TButton", font=("Segoe UI", 10, "bold"),
                        padding=(14, 9), background="#176349",
                        foreground="#FFFFFF", bordercolor=colors["accent"])
        style.map("ActivatedAction.TButton",
                  background=[("disabled", "#8FC9B5"),
                              ("pressed", "#11523C"),
                              ("active", "#238463")],
                  foreground=[("disabled", "#176349")])
        style.configure("SecondaryAction.TButton", font=("Segoe UI", 10), padding=(12, 8),
                        background=colors["accent_soft"], foreground="#176349",
                        bordercolor="#8FC9B5")
        style.map("SecondaryAction.TButton", background=[("active", "#CFEADF"),
                                                          ("pressed", "#B9DFD0")])
        style.configure("TNotebook", background=colors["background"], borderwidth=0)
        style.configure("TNotebook.Tab", padding=(16, 9), background="#DCEAF0",
                        foreground=colors["primary_dark"], font=("Segoe UI", 9, "bold"))
        style.map("TNotebook.Tab", background=[("selected", colors["surface"]),
                                                ("active", colors["blue_soft"])],
                  foreground=[("selected", colors["primary"])] )
        style.configure("TEntry", fieldbackground=colors["surface"], foreground=colors["text"],
                        bordercolor=colors["border"], lightcolor=colors["border"],
                        darkcolor=colors["border"], padding=5)
        style.configure("TCombobox", fieldbackground=colors["surface"], foreground=colors["text"],
                        bordercolor=colors["border"], arrowsize=15, padding=4)
        style.map("TCombobox", fieldbackground=[("readonly", colors["surface"])],
                  selectbackground=[("readonly", colors["surface"])],
                  selectforeground=[("readonly", colors["text"])])
        style.configure("Treeview", background=colors["surface"], fieldbackground=colors["surface"],
                        foreground=colors["text"], rowheight=27, bordercolor=colors["border"])
        style.configure("Treeview.Heading", background=colors["primary_dark"],
                        foreground="#FFFFFF", font=("Segoe UI", 9, "bold"), padding=6)
        style.map("Treeview", background=[("selected", colors["primary"])],
                  foreground=[("selected", "#FFFFFF")])
        style.map("Treeview.Heading", background=[("active", colors["primary_hover"])])
        style.configure("Horizontal.TProgressbar", background=colors["accent"],
                        troughcolor=colors["blue_soft"], bordercolor=colors["border"])

        brand_header = tk.Frame(self, bg=colors["primary_dark"], height=58)
        brand_header.pack(fill="x")
        brand_header.pack_propagate(False)
        tk.Label(brand_header, text="CODEX MODEL GATE", bg=colors["primary_dark"],
                 fg="#FFFFFF", font=("Segoe UI", 15, "bold")).pack(
                     side="left", padx=(18, 12), pady=12)
        tk.Label(brand_header, text="Decisão clara. Execução sob seu controle.",
                 bg=colors["primary_dark"], fg="#BFE4EE",
                 font=("Segoe UI", 9)).pack(side="left", pady=(18, 12))
        self.main_notebook = ttk.Notebook(self)
        self.main_notebook.pack(fill="both", expand=True, padx=10, pady=10)
        work_host, self.response_tab, self.history_tab, self.files_tab, self.usage_tab, self.manual_tab = (
            ttk.Frame(self.main_notebook), ttk.Frame(self.main_notebook, padding=6),
            ttk.Frame(self.main_notebook, padding=6), ttk.Frame(self.main_notebook, padding=6),
            ttk.Frame(self.main_notebook, padding=6), ttk.Frame(self.main_notebook, padding=6))
        self.main_notebook.add(work_host, text="Tarefa")
        self.main_notebook.add(self.response_tab, text="Resposta")
        self.main_notebook.add(self.history_tab, text="Tarefas anteriores")
        self.main_notebook.add(self.files_tab, text="Arquivos")
        self.main_notebook.add(self.usage_tab, text="Consumo")
        self.main_notebook.add(self.manual_tab, text="Manual")

        ttk.Label(self.response_tab, text="Resposta final da tarefa",
                  font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(0, 4))
        ttk.Label(self.response_tab,
                  text="Esta tela é aberta automaticamente quando a execução termina.",
                  style="Hint.TLabel").pack(anchor="w", pady=(0, 8))
        self.response_consumption = ttk.Label(
            self.response_tab, textvariable=self.consumption_var,
            style="Hint.TLabel", wraplength=880, justify="left")
        self.response_consumption.pack(anchor="w", pady=(0, 8))
        response_holder = ttk.Frame(self.response_tab)
        response_holder.pack(fill="both", expand=True)
        self.response_text = tk.Text(
            response_holder, wrap="word", state="disabled", font=("Segoe UI", 11),
            padx=24, pady=20, bg="#ffffff", fg="#222222", relief="flat")
        add_vertical_scrollbar(response_holder, self.response_text)
        response_controls = ttk.Frame(self.response_tab)
        response_controls.pack(fill="x", pady=(8, 0))
        response_tools = ttk.Frame(self.response_tab)
        response_tools.pack(fill='x', pady=4)
        ttk.Button(response_tools, text='Copiar resposta', command=self.copy_response).pack(side='left')
        ttk.Button(response_tools, text='Exportar resposta...', command=self.export_response).pack(side='left', padx=6)
        ttk.Button(response_tools, text='Abrir pasta da tarefa', command=self.open_current_task_folder).pack(side='left')
        ttk.Button(response_tools, text='Abrir diagnóstico', command=self.open_diagnostics).pack(side='left', padx=6)
        ttk.Button(response_controls, text="Abrir leitura em tela cheia",
                   command=self.abrir_leitor_focado).pack(side="left")
        ttk.Button(response_controls, text="Enviar arquivo à conversa...",
                   command=self.add_continuation_attachments).pack(side="left", padx=(8, 0))
        ttk.Button(response_controls, text="Remover arquivo da conversa...",
                   command=self.remove_continuation_attachment).pack(side="left", padx=(8, 0))

        # The task form can be taller than a notebook screen, especially when
        # Windows display scaling is 125% or 150%. Keep the whole form inside a
        # vertically scrollable canvas while Text/Listbox widgets retain their
        # own scrolling behaviour.
        self.work_canvas = tk.Canvas(
            work_host, highlightthickness=0, borderwidth=0)
        self.work_scrollbar = ttk.Scrollbar(
            work_host, orient="vertical", command=self.work_canvas.yview)
        self.work_canvas.configure(yscrollcommand=self.work_scrollbar.set)
        self.work_scrollbar.pack(side="right", fill="y")
        self.work_canvas.pack(side="left", fill="both", expand=True)
        self.work_tab = ttk.Frame(self.work_canvas, padding=6)
        self.work_canvas_window = self.work_canvas.create_window(
            (0, 0), window=self.work_tab, anchor="nw")
        self.work_tab.bind("<Configure>", self._update_work_scrollregion)
        self.work_canvas.bind("<Configure>", self._resize_work_content)
        self.bind_all("<MouseWheel>", self._on_main_mousewheel, add="+")
        self.bind_all("<Prior>", self._on_page_scroll, add="+")
        self.bind_all("<Next>", self._on_page_scroll, add="+")

        workflow = ttk.LabelFrame(self.work_tab, text="Fluxo da tarefa", padding=6)
        workflow.pack(fill="x", pady=(0, 10))
        for index, text in enumerate((
            "1. Preparar", "2. Descrever", "3. Conferir decisão",
            "4. Autorizar", "5. Conferir resultado")):
            ttk.Label(workflow, text=text, style="Step.TLabel").grid(
                row=0, column=index, sticky="ew", padx=(0 if index == 0 else 4, 0))
            workflow.columnconfigure(index, weight=1)
        ttk.Label(workflow, text="Você mantém a decisão final: revise modelo, skills e destino antes de executar.", style="Hint.TLabel", wraplength=840).grid(
            row=1, column=0, columnspan=5, sticky="w", pady=(5, 0))

        mode_bar = ttk.Frame(self.work_tab)
        mode_bar.pack(fill="x", pady=(0, 8))
        ttk.Label(mode_bar, text="Modo de uso:").pack(side="left")
        self.advanced_mode_toggle = ttk.Checkbutton(
            mode_bar, text="Mostrar opções avançadas", variable=self.ui_mode_var,
            command=self.apply_ui_mode)
        self.advanced_mode_toggle.pack(side="left", padx=(8, 0))
        ttk.Button(mode_bar, text="Como funciona?", command=self.show_manual_tab).pack(
            side="left", padx=(12, 0))
        ttk.Label(mode_bar, text="Idioma / Language:").pack(side="left", padx=(20, 0))
        self.language_var = tk.StringVar(value=gate_i18n.LANGUAGES[self.language])
        self.language_box = ttk.Combobox(
            mode_bar, textvariable=self.language_var,
            values=list(gate_i18n.LANGUAGES.values()), state="readonly", width=19)
        self.language_box.pack(side="left", padx=(6, 0))
        self.language_box.bind("<<ComboboxSelected>>", self.change_language)

        cli_box = ttk.LabelFrame(self.work_tab, text="Codex CLI", padding=6)
        cli_box.pack(fill="x", pady=(0, 10))
        ttk.Label(cli_box, textvariable=self.cli_status_var, wraplength=850).pack(
            anchor="w")
        cli_links = ttk.Frame(cli_box)
        cli_links.pack(fill='x', pady=(5, 0))
        self.cli_download_button = ttk.Button(cli_links, text='Download / atualização oficial', command=self.open_codex_install_guide)
        self.cli_download_button.pack(side='left')
        self.cli_check_button = ttk.Button(cli_links, text='Verificar novamente', command=self.refresh_codex_cli_status)
        self.cli_check_button.pack(side='left', padx=6)
        self.cli_release_button = ttk.Button(cli_links, text='Consultar novas versões', command=self.check_cli_updates)
        self.cli_release_button.pack(side='left')
        self.cli_controls = ttk.Frame(cli_box)
        self.cli_controls.pack(anchor="w", pady=(6, 0))
        ttk.Checkbutton(cli_box, text="Abrir até 3 arquivos após validação", variable=self.auto_open_outputs_var, command=lambda:gate.save_app_settings({"auto_open_outputs":self.auto_open_outputs_var.get()})).pack(anchor="w",pady=(4,0))
        self.install_cli_button = ttk.Button(
            self.cli_controls, text="Instalar Codex CLI...", command=self.install_codex_cli)
        self.install_cli_button.pack(side="left")
        ttk.Button(self.cli_controls, text="Abrir instruções oficiais", command=self.open_codex_install_guide).pack(
            side="left", padx=8)
        ttk.Button(self.cli_controls, text="Verificar novamente", command=self.refresh_codex_cli_status).pack(
            side="left")

        self.portable_storage_box = ttk.LabelFrame(
            self.work_tab, text="Armazenamento da versão portátil", padding=6)
        if gate.is_portable_mode():
            self.portable_storage_box.pack(fill="x", pady=(0, 10))
            ttk.Label(self.portable_storage_box, textvariable=self.portable_storage_var,
                      wraplength=850, justify="left").pack(anchor="w")

        ttk.Label(self.work_tab, text="Pasta de projetos (cada tarefa cria uma subpasta exclusiva):").pack(anchor="w")
        row = ttk.Frame(self.work_tab)
        row.pack(fill="x", pady=(2, 10))
        self.path_var = tk.StringVar(value=str(self.cwd))
        self.path_entry = ttk.Entry(row, textvariable=self.path_var)
        self.path_entry.pack(side="left", fill="x", expand=True)
        self.choose_button = ttk.Button(
            row, text="Escolher...", command=self.choose_dir)
        self.choose_button.pack(side="left", padx=(8, 0))
        self.open_folder_button = ttk.Button(
            row, text="Abrir projetos", command=self.open_project_folder)
        self.open_folder_button.pack(side="left", padx=(8, 0))
        self.open_gate_data_button = ttk.Button(
            row, text="Abrir dados do Gate", command=self.open_gate_data_folder)
        self.open_gate_data_button.pack(side="left", padx=(8, 0))
        self.backup_button = ttk.Button(
            row, text="Fazer backup...", command=self.backup_gate_data)
        self.backup_button.pack(side="left", padx=(8, 0))
        self.restore_backup_button = ttk.Button(
            row, text="Restaurar backup...", command=self.restore_gate_data)
        self.restore_backup_button.pack(side="left", padx=(8, 0))
        self.library_box = ttk.LabelFrame(self.work_tab, text="Biblioteca de conhecimentos (skills)", padding=6)
        self.library_box.pack(fill="x", pady=(0, 8))
        library_row = ttk.Frame(self.library_box)
        library_row.pack(fill="x", pady=(0, 2))
        self.skill_library_entry = ttk.Entry(
            library_row, textvariable=self.skill_library_var)
        self.skill_library_entry.pack(side="left", fill="x", expand=True)
        self.choose_skill_library_button = ttk.Button(
            library_row, text="Vincular biblioteca...", command=self.choose_skill_library)
        self.choose_skill_library_button.pack(side="left", padx=(8, 0))
        self.open_skill_library_button = ttk.Button(
            library_row, text="Abrir biblioteca", command=self.open_skill_library)
        self.open_skill_library_button.pack(side="left", padx=(8, 0))
        self.library_refresh_button = ttk.Button(
            library_row, text="Atualizar skills", command=self.refresh_skills)
        self.library_refresh_button.pack(side="left", padx=(8, 0))
        ttk.Label(self.library_box, textvariable=self.skill_library_status,
                  wraplength=860).pack(anchor="w", pady=(0, 8))
        template_row = ttk.Frame(self.work_tab)
        template_row.pack(fill="x", pady=(0, 2))
        ttk.Label(template_row, text="Começar com um modelo:").pack(side="left")
        self.template_box = ttk.Combobox(
            template_row, textvariable=self.template_var, values=list(TASK_TEMPLATES),
            state="readonly", width=28)
        self.template_box.pack(side="left", padx=(8, 0))
        self.template_box.bind("<<ComboboxSelected>>", self.apply_task_template)
        ttk.Label(self.work_tab, text="O que você quer fazer?").pack(anchor="w")
        task_holder = ttk.Frame(self.work_tab)
        task_holder.pack(fill="x", pady=(2, 10))
        self.task = tk.Text(task_holder, height=5, wrap="word")
        add_vertical_scrollbar(task_holder, self.task)
        browser_box = ttk.LabelFrame(
            self.work_tab, text="Pesquisa web controlada", padding=6)
        browser_box.pack(fill="x", pady=(0, 8))
        self.browser_research_toggle = ttk.Checkbutton(
            browser_box, text="Permitir navegador visual do Gate (Edge)",
            variable=self.browser_research_var)
        self.browser_research_toggle.pack(anchor="w")
        browser_query_row = ttk.Frame(browser_box)
        browser_query_row.pack(fill="x", pady=(5, 0))
        ttk.Label(browser_query_row, text="Termos para busca no Edge (opcional):").pack(side="left")
        self.browser_query_entry = ttk.Entry(
            browser_query_row, textvariable=self.browser_query_var, state="disabled")
        self.browser_query_entry.pack(side="left", fill="x", expand=True, padx=(8, 0))
        self.browser_research_var.trace_add(
            "write", lambda *_args: self._sync_browser_query_state())
        ttk.Label(browser_box,
                  text="Este campo só sugere termos ao Codex: não inicia pesquisa nem abre links. Para analisar uma URL específica, cole-a na descrição da tarefa. O Edge abre apenas se o Codex usar o navegador visual.",
                  style="Hint.TLabel", wraplength=840).pack(anchor="w", pady=(4, 0))
        attachments_box = ttk.LabelFrame(
            self.work_tab, text="Arquivos anexados à tarefa", padding=6)
        attachments_box.pack(fill="x", pady=(0, 8))
        attachment_list_holder = ttk.Frame(attachments_box)
        attachment_list_holder.pack(fill="x")
        self.attachment_list = tk.Listbox(
            attachment_list_holder, height=3, exportselection=False)
        add_vertical_scrollbar(attachment_list_holder, self.attachment_list)
        attachment_controls = ttk.Frame(attachments_box)
        attachment_controls.pack(fill="x", pady=(5, 0))
        self.add_attachment_button = ttk.Button(
            attachment_controls, text="Anexar arquivos...", command=self.add_attachments)
        self.add_attachment_button.pack(side="left")
        self.remove_attachment_button = ttk.Button(
            attachment_controls, text="Remover anexo", command=self.remove_attachment)
        self.remove_attachment_button.pack(side="left", padx=8)
        self.open_attachment_button = ttk.Button(
            attachment_controls, text="Abrir anexo", command=self.open_attachment)
        self.open_attachment_button.pack(side="left")
        self.skills_browser = ttk.Frame(self.work_tab)
        self.skills_browser.pack(fill='x')
        skills_header = ttk.Frame(self.skills_browser)
        skills_header.pack(fill="x")
        ttk.Label(skills_header, text="Conhecimentos especializados (skills):").pack(side="left")
        self.manual_skills_toggle = ttk.Checkbutton(
            skills_header, text="Usar seleção manual (desmarcado: Gate escolhe automaticamente)", variable=self.manual_skills_var)
        self.manual_skills_toggle.pack(side="left", padx=(8, 0))
        ttk.Label(self.skills_browser, text="Automático é recomendado: o Gate explica abaixo por que cada instrução especializada foi escolhida. Use a seleção manual apenas quando quiser substituir a recomendação.", style="Hint.TLabel", wraplength=860).pack(anchor="w", pady=(2, 4))
        skill_search_row = ttk.Frame(self.skills_browser)
        skill_search_row.pack(fill="x", pady=(0, 2))
        ttk.Label(skill_search_row, text="Pesquisar skill por nome:").pack(side="left")
        self.skill_search_entry = ttk.Entry(
            skill_search_row, textvariable=self.skill_search_var, width=34)
        self.skill_search_entry.pack(side="left", padx=(8, 0))
        self.clear_skill_search_button = ttk.Button(
            skill_search_row, text="Limpar busca", command=self.clear_skill_search)
        self.clear_skill_search_button.pack(side="left", padx=(8, 0))
        ttk.Label(skill_search_row, textvariable=self.skill_search_status,
                  style="Hint.TLabel").pack(side="left", padx=(10, 0))
        skill_list_holder = ttk.Frame(self.skills_browser)
        skill_list_holder.pack(fill="x", pady=(2, 8))
        self.skill_list = tk.Listbox(
            skill_list_holder, selectmode="multiple", height=5, exportselection=False)
        add_vertical_scrollbar(skill_list_holder, self.skill_list)
        self.skill_search_var.trace_add("write", self.on_skill_search_changed)
        active_box = ttk.LabelFrame(
            self.work_tab, text="Skills recomendadas para esta tarefa", padding=6)
        active_box.pack(fill="x", pady=(0, 8))
        self.active_skills_box = active_box
        ttk.Label(active_box, text="Selecione uma skill para conferir as instruções completas. A explicação após o travessão informa a relevância identificada.", style="Hint.TLabel", wraplength=820).pack(anchor="w", pady=(0, 4))
        active_skill_list_holder = ttk.Frame(active_box)
        active_skill_list_holder.pack(fill="x")
        self.active_skill_list = tk.Listbox(
            active_skill_list_holder, height=3, exportselection=False)
        add_vertical_scrollbar(active_skill_list_holder, self.active_skill_list)
        active_controls = ttk.Frame(active_box)
        active_controls.pack(fill="x", pady=(5, 0))
        self.open_active_skill_button = ttk.Button(
            active_controls, text="Abrir skill para conferir", command=self.open_active_skill)
        self.open_active_skill_button.pack(side="left")
        self.install_active_skill_button = ttk.Button(
            active_controls, text="Instalar skill", command=self.install_active_skill)
        self.install_active_skill_button.pack(side="left", padx=(8, 0))
        self.add_active_skill_button = ttk.Button(
            active_controls, text="Adicionar skill à tarefa",
            command=self.add_selected_skill_to_task)
        self.add_active_skill_button.pack(side="left", padx=(8, 0))
        self.remove_active_skill_button = ttk.Button(
            active_controls, text="Remover skill selecionada",
            command=self.remove_selected_skill_from_task)
        self.remove_active_skill_button.pack(side="left", padx=(8, 0))
        controls = ttk.LabelFrame(self, text="Ações principais", padding=8)
        self.action_bar = controls
        controls.pack(side='bottom', fill='x', padx=10, pady=(0, 8), before=self.main_notebook)
        for column in range(3):
            controls.columnconfigure(column, weight=1)
        self.refresh_button = ttk.Button(controls, text="Atualizar skills", command=self.refresh_skills)
        self.recommend_button = ttk.Button(controls, text="1. Analisar tarefa", command=self.recommend, style="Primary.TButton")
        self.run_button = ttk.Button(controls, text="2. Confirmar e executar", command=self.authorize_run, style="Primary.TButton")
        self.cancel_button = ttk.Button(controls, text="Cancelar execução", command=self.cancel_run, state='disabled')
        for column, widget in enumerate((self.recommend_button, self.run_button, self.cancel_button)):
            widget.grid(row=0, column=column, sticky='ew', padx=3, pady=3)
        self.schedule_button = ttk.Button(controls, text="Agendar tarefa...", command=self.schedule_current_task)
        self.continue_pending_button = ttk.Button(controls, text="Responder pergunta pendente", command=self.show_continuation_window, state='disabled')
        self.schedule_button.grid(row=1, column=0, sticky='ew', padx=3, pady=3)
        self.continue_pending_button.grid(row=1, column=1, sticky='ew', padx=3, pady=3)
        ttk.Label(controls, text='Ctrl+Enter / Ctrl+Shift+Enter', style='Hint.TLabel').grid(row=1, column=2, padx=3)
        self.bind("<Control-Return>", self.analyze_from_shortcut, add="+")
        self.bind("<Control-Shift-Return>", self.execute_from_shortcut, add="+")

        decision = ttk.LabelFrame(
            self.work_tab, text="Resumo antes de executar", padding=6)
        decision.pack(fill="x", pady=(0, 8))
        self.decision_box = decision
        cards = ttk.Frame(decision)
        self.decision_cards = []
        cards.pack(fill="x", pady=(0, 8))
        for index, (title, variable) in enumerate((
            ("MODELO SELECIONADO", self.decision_model_card_var),
            ("NÍVEL", self.decision_effort_card_var),
            ("RISCO", self.decision_risk_card_var),
            ("SKILLS RELEVANTES", self.decision_skills_card_var),
        )):
            card = ttk.LabelFrame(cards, padding=(10, 6), style="Card.TLabelframe")
            self.decision_cards.append(card)
            card.grid(row=index // 2, column=index % 2, sticky="nsew", padx=3, pady=3)
            cards.columnconfigure(index % 2, weight=1)
            ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
            ttk.Label(card, textvariable=variable, style="CardValue.TLabel").pack(anchor="w", pady=(2, 0))
        self.decision_controls_line = ttk.Frame(decision)
        self.decision_controls_line.pack(fill="x")
        ttk.Label(self.decision_controls_line, text="Política:").pack(side="left")
        self.policy_box = ttk.Combobox(self.decision_controls_line, textvariable=self.policy_var, values=list(
            gate.POLICIES), state="readonly", width=13)
        self.policy_box.pack(side="left", padx=(4, 16))
        ttk.Label(self.decision_controls_line, text="Modelo:").pack(side="left")
        self.model_box = ttk.Combobox(self.decision_controls_line, textvariable=self.model_var, values=[
                                      model_label(name) for name in gate.PRIMARY_MODELS], state="readonly", width=12)
        self.model_box.pack(side="left", padx=(4, 16))
        self.model_box.bind("<<ComboboxSelected>>", self.on_model_selection_changed)
        ttk.Label(self.decision_controls_line, text="Modelo legado:").pack(side="left")
        self.legacy_model_var = tk.StringVar(value="Selecionar...")
        self.legacy_model_box = ttk.Combobox(self.decision_controls_line,
            textvariable=self.legacy_model_var,
            values=["Selecionar..."] + [model_label(key) for key in gate.LEGACY_MODELS],
            state="readonly", width=15)
        self.legacy_model_box.pack(side="left", padx=(4, 16))
        self.legacy_model_box.bind("<<ComboboxSelected>>", self.on_legacy_model_selection_changed)
        ttk.Label(self.decision_controls_line, text="Nível:").pack(side="left")
        self.effort_box = ttk.Combobox(self.decision_controls_line, textvariable=self.effort_var, values=[gate.EFFORT_LABELS[k] for k in gate.supported_efforts("sol")], state="readonly", width=12)
        self.effort_box.pack(side="left", padx=(4, 0))
        self.effort_box.bind('<<ComboboxSelected>>', self.sync_decision_settings)
        self.policy_box.bind('<<ComboboxSelected>>', self.sync_decision_settings)
        self.decision_text = tk.StringVar(
            value="Analise a tarefa para ver justificativa, risco e controles.")
        ttk.Label(decision, textvariable=self.decision_text,
                  wraplength=860, justify="left").pack(anchor="w", pady=(6, 0))
        ttk.Label(decision, textvariable=self.decision_checklist_var,
                  style="Hint.TLabel", wraplength=860, justify="left").pack(anchor="w", pady=(6, 0))
        usage_box = ttk.LabelFrame(decision, text="Consumo e custo estimado", padding=6)
        usage_box.pack(fill="x", pady=(8, 0))
        ttk.Label(usage_box, textvariable=self.consumption_var,
                  style="Hint.TLabel", wraplength=850, justify="left").pack(anchor="w")

        # Keep the complete preparation flow together near the task editor.
        # The skill library and execution monitoring remain below this block.
        decision.pack_forget()
        decision.pack(fill="x", pady=(0, 8), after=attachments_box)
        self.library_box.pack_forget()
        self.library_box.pack(fill="x", pady=(0, 8), after=decision)

        self.status = tk.StringVar(value="Nenhuma tarefa analisada.")
        ttk.Label(self.work_tab, textvariable=self.status,
                  wraplength=860, justify="left").pack(anchor="w", pady=(0, 6))
        ttk.Label(self.work_tab, text="Acompanhamento simples:").pack(anchor="w")
        ttk.Label(self.work_tab, textvariable=self.simple_progress_var, font=("Segoe UI", 10, "bold"), wraplength=860).pack(anchor="w", pady=(2, 5))
        execution_area = ttk.Frame(self.work_tab)
        execution_area.pack(fill="both", expand=True, pady=(2, 8))

        # UI Upgrade: Caixa de texto modernizada com melhor tipografia e margens
        self.log_holder = ttk.LabelFrame(execution_area, text="Detalhes técnicos da execução", padding=2)
        self.log_holder.pack(side="left", fill="both", expand=True)
        self.log = tk.Text(
            self.log_holder, height=9, wrap="word", state="disabled",
            font=("Segoe UI", 11), padx=10, pady=10, bg="#f5f5f5", relief="flat"
        )
        add_vertical_scrollbar(self.log_holder, self.log)

        progress_box = ttk.LabelFrame(
            execution_area, text="Progresso", padding=8, width=225)
        progress_box.pack(side="left", fill="y", padx=(8, 0))
        progress_box.pack_propagate(False)
        self.phase_var = tk.StringVar(value="Aguardando autorização")
        self.elapsed_var = tk.StringVar(value="Tempo decorrido: 00:00")
        self.remaining_var = tk.StringVar(
            value="Tempo restante: ainda não estimado")
        ttk.Label(progress_box, textvariable=self.phase_var,
                  wraplength=190, justify="left").pack(anchor="w")
        self.progress_bar = ttk.Progressbar(
            progress_box, mode="determinate", maximum=100, value=0)
        self.progress_bar.pack(fill="x", pady=(10, 8))
        ttk.Label(progress_box, textvariable=self.elapsed_var,
                  wraplength=190).pack(anchor="w")
        ttk.Label(progress_box, textvariable=self.remaining_var,
                  wraplength=190, justify="left").pack(anchor="w", pady=(5, 0))

        # Novo botão: Leitura em tela cheia do texto filtrado
        self.botao_leitura = ttk.Button(
            progress_box, text="Modo Leitura (Tela Cheia)", command=self.abrir_leitor_focado)
        self.botao_leitura.pack(fill="x", pady=(15, 0))

        deliveries = ttk.LabelFrame(
            self.work_tab, text="Resultados e arquivos criados", padding=6)
        deliveries.pack(fill="x")
        artifact_content = ttk.Frame(deliveries)
        artifact_content.pack(fill="x")
        artifact_list_holder = ttk.Frame(artifact_content)
        artifact_list_holder.pack(side="left", fill="both", expand=True)
        self.artifact_list = tk.Listbox(
            artifact_list_holder, height=4, exportselection=False)
        add_vertical_scrollbar(artifact_list_holder, self.artifact_list)
        self.artifact_list.bind("<<ListboxSelect>>", self.show_artifact_preview)
        artifact_preview = ttk.LabelFrame(artifact_content, text="Prévia", padding=6, width=245)
        artifact_preview.pack(side="left", fill="y", padx=(8, 0))
        artifact_preview.pack_propagate(False)
        self.artifact_thumbnail = ttk.Label(
            artifact_preview, text="Selecione um arquivo", anchor="center",
            justify="center", wraplength=215)
        self.artifact_thumbnail.pack(fill="x", pady=(0, 6))
        self.artifact_preview_var = tk.StringVar(
            value="Selecione um resultado para ver tipo, tamanho e data.")
        ttk.Label(artifact_preview, textvariable=self.artifact_preview_var,
                  style="Hint.TLabel", justify="left", wraplength=215).pack(anchor="w")
        bottom = ttk.Frame(deliveries)
        bottom.pack(fill="x", pady=(6, 0))
        ttk.Button(bottom, text="Abrir arquivo",
                   command=self.open_selected_artifact).pack(side="left")
        ttk.Button(bottom, text="Atualizar lista",
                   command=self.refresh_artifacts).pack(side="left", padx=8)
        self.record_quality_button = ttk.Button(
            bottom, text="Registrar resultado", command=self.record_outcome)
        self.record_quality_button.pack(side="left", padx=8)
        self.quality_box = ttk.Combobox(bottom, textvariable=self.quality_var, values=[
                                        "Não avaliado", "Aprovado", "Precisou de ajustes", "Falhou"], state="readonly", width=20)
        self.quality_box.pack(side="left")
        ttk.Label(self.history_tab, text="Tarefas anteriores:").pack(
            anchor="w", pady=(0, 4))
        search_bar = ttk.LabelFrame(
            self.history_tab, text="Buscar tarefa", padding=8)
        search_bar.pack(fill="x", pady=(0, 6))
        ttk.Label(search_bar, text="Palavra ou assunto:").pack(side="left")
        self.history_search_entry = ttk.Entry(
            search_bar, textvariable=self.record_filter_vars["task"])
        self.history_search_entry.pack(
            side="left", fill="x", expand=True, padx=(8, 6))
        self.history_search_entry.bind(
            "<KeyRelease>", self.schedule_history_search)
        self.history_search_entry.bind(
            "<Return>", lambda _event: self.load_history())
        ttk.Button(search_bar, text="Buscar", command=lambda: self.load_history(force=False)).pack(
            side="left")
        ttk.Button(search_bar, text="Limpar busca",
                   command=self.clear_history_search).pack(side="left", padx=(6, 0))
        ttk.Label(search_bar, textvariable=self.record_filter_status,
                  style="Hint.TLabel").pack(side="right", padx=(10, 0))
        self.bind("<Control-f>", self.focus_history_search, add="+")

        filters = ttk.LabelFrame(self.history_tab, text="Outros filtros", padding=6)
        filters.pack(fill="x", pady=(0, 6))
        filter_fields = (("Data", "date", 14), ("Modelo", "model", 14),
                         ("Status", "status", 14), ("Skill", "skill", 18))
        for index, (label, key, width) in enumerate(filter_fields):
            column = (index % 2) * 2
            filter_row = index // 2
            ttk.Label(filters, text=label + ":").grid(
                row=filter_row, column=column, sticky="w",
                padx=(0 if index == 0 else 8, 3), pady=2)
            ttk.Entry(filters, textvariable=self.record_filter_vars[key], width=width).grid(
                row=filter_row, column=column + 1, sticky="ew", pady=2)
            filters.columnconfigure(column + 1, weight=1)
        ttk.Button(filters, text="Aplicar filtros", command=self.load_history).grid(
            row=2, column=0, sticky="w", padx=(10, 0), pady=2)
        ttk.Button(filters, text="Limpar filtros", command=self.clear_record_filters).grid(
            row=2, column=2, sticky="w", padx=(8, 0), pady=2)
        columns = ("quando", "resultado", "qualidade", "modelo", "tarefa")
        history_body = ttk.Panedwindow(self.history_tab, orient="vertical")
        history_body.pack(fill="both", expand=True)
        history_holder = ttk.Frame(history_body)
        history_body.add(history_holder, weight=1)
        self.history = ttk.Treeview(
            history_holder, columns=columns, show="headings", height=1)
        for name, width in (("quando", 135), ("resultado", 100), ("qualidade", 130), ("modelo", 115), ("tarefa", 390)):
            self.history.heading(name, text=name.capitalize())
            self.history.column(name, width=width, minwidth=width, stretch=False, anchor="w")
        add_vertical_scrollbar(history_holder, self.history)
        self.history.bind("<<TreeviewSelect>>", self.show_selected_record)
        self.history_controls = ttk.Frame(history_holder)
        self.history_controls.pack(side="bottom", fill="x", pady=8, before=self.history)
        self.history_controls.columnconfigure(0, weight=1)
        self.history_actions_canvas = tk.Canvas(
            self.history_controls, height=42, highlightthickness=0,
            borderwidth=0, bg=UI_COLORS["surface"])
        self.history_actions_canvas.grid(row=0, column=0, sticky="ew")
        self.history_actions_scrollbar = ttk.Scrollbar(
            self.history_controls, orient="horizontal",
            command=self.history_actions_canvas.xview)
        self.history_actions_canvas.configure(
            xscrollcommand=self.history_actions_scrollbar.set)
        history_actions = ttk.Frame(self.history_actions_canvas)
        self.history_actions_frame = history_actions
        self.history_actions_canvas.create_window(
            (0, 0), window=history_actions, anchor="nw")
        history_actions.bind("<Configure>", self._update_history_action_scroll)
        self.history_actions_canvas.bind(
            "<Configure>", self._update_history_action_scroll)
        ttk.Button(history_actions, text="Atualizar registros",
                   command=self.load_history).pack(side="left", padx=(0, 8))
        self.continue_record_button = ttk.Button(
            history_actions, text="Continuar conversa",
            command=self.continue_selected_record_conversation, state="disabled")
        self.continue_record_button.pack(side="left", padx=(0, 8))
        ttk.Button(history_actions, text="Qualificar registro",
                   command=self.qualify_selected_record).pack(side="left", padx=(0, 12))
        ttk.Separator(history_actions, orient="vertical").pack(
            side="left", fill="y", padx=(0, 12), pady=4)

        list_button = ttk.Menubutton(history_actions, text="Lista ▾")
        self.history_list_menu = tk.Menu(list_button, tearoff=False)
        self.history_list_menu.add_command(
            label=self.tr("Registros sem avaliação"),
            command=self.toggle_unqualified_records)
        self.history_list_menu.add_command(
            label=self.tr("Gerar relatório dos registros"),
            command=self.generate_records_report)
        list_button.configure(menu=self.history_list_menu)
        list_button.pack(side="left", padx=(0, 8))

        record_button = ttk.Menubutton(history_actions, text="Abrir / exportar ▾")
        record_menu = tk.Menu(record_button, tearoff=False)
        record_menu.add_command(
            label=self.tr("Abrir registro em texto"),
            command=self.open_selected_record)
        record_menu.add_command(
            label=self.tr("Exportar registro TXT/PDF"),
            command=self.export_selected_record)
        record_menu.add_command(
            label=self.tr("Abrir pasta registro"),
            command=self.open_records_folder)
        record_button.configure(menu=record_menu)
        record_button.pack(side="left", padx=(0, 8))

        package_button = ttk.Menubutton(history_actions, text="Pacotes .gate ▾")
        package_menu = tk.Menu(package_button, tearoff=False)
        package_menu.add_command(
            label=self.tr("Exportar tarefa como pacote..."),
            command=self.export_selected_task_package)
        package_menu.add_command(
            label=self.tr("Importar pacote .gate..."),
            command=self.import_task_package)
        package_button.configure(menu=package_menu)
        package_button.pack(side="left")
        detail_box = ttk.LabelFrame(
            history_body, text="Detalhes do registro selecionado", padding=6)
        history_body.add(detail_box, weight=1)
        detail_scroll = ttk.Scrollbar(detail_box, orient="vertical")
        self.record_detail = tk.Text(
            detail_box, height=1, wrap="word", state="disabled", yscrollcommand=detail_scroll.set)
        detail_scroll.configure(command=self.record_detail.yview)
        detail_scroll.pack(side="right", fill="y")
        self.record_detail.pack(side="left", fill="both", expand=True)

        ttk.Label(self.files_tab, text="Arquivos de tarefas anteriores:").pack(
            anchor="w", pady=(0, 4))
        ttk.Label(
            self.files_tab, textvariable=self.files_context_var, style="Hint.TLabel",
            wraplength=840).pack(anchor="w", pady=(0, 8))
        files_controls = ttk.Frame(self.files_tab)
        files_controls.pack(anchor="w", pady=(0, 8))
        ttk.Button(files_controls, text="Selecionar tarefa anterior...",
                   command=self.show_history_tab).pack(side="left")
        ttk.Button(files_controls, text="Abrir pasta da tarefa",
                   command=self.open_selected_record_task_folder).pack(side="left", padx=8)
        ttk.Button(files_controls, text="Abrir arquivo selecionado",
                   command=self.open_selected_record_artifact).pack(side="left")
        previous_artifacts = ttk.LabelFrame(
            self.files_tab, text="Arquivos gerados ou alterados", padding=6)
        previous_artifacts.pack(fill="both", expand=True)
        artifact_holder = ttk.Frame(previous_artifacts)
        artifact_holder.pack(fill="both", expand=True)
        self.record_artifact_list = tk.Listbox(
            artifact_holder, height=14, exportselection=False)
        add_vertical_scrollbar(artifact_holder, self.record_artifact_list)

        self._build_usage_tab()

        ttk.Label(self.manual_tab, text="Manual do Codex Model Gate").pack(
            anchor="w", pady=(0, 4))
        ttk.Label(
            self.manual_tab,
            text="Consulte este guia sempre que quiser entender o fluxo do programa.",
            style="Hint.TLabel").pack(anchor="w", pady=(0, 8))
        manual_holder = ttk.Frame(self.manual_tab)
        manual_holder.pack(fill="both", expand=True)
        manual_scroll = ttk.Scrollbar(manual_holder, orient="vertical")
        self.manual_text = tk.Text(
            manual_holder, wrap="word", state="normal", padx=18, pady=14,
            font=("Segoe UI", 10), yscrollcommand=manual_scroll.set)
        manual_scroll.configure(command=self.manual_text.yview)
        manual_scroll.pack(side="right", fill="y")
        self.manual_text.pack(side="left", fill="both", expand=True)
        self.manual_text.tag_configure("heading1", font=("Segoe UI", 16, "bold"), spacing1=5, spacing3=10)
        self.manual_text.tag_configure("heading2", font=("Segoe UI", 12, "bold"), spacing1=10, spacing3=5)
        self.manual_text.tag_configure("bold", font=("Segoe UI", 10, "bold"))
        self.manual_text.tag_configure("italic", font=("Segoe UI", 10, "italic"))
        self.manual_text.tag_configure("code", font=("Cascadia Mono", 9), background="#eef1f5")
        self.manual_text.tag_configure("quote", foreground="#4c5f73", lmargin1=18, lmargin2=18)
        self.manual_text.tag_configure("symbol", font=("Cambria Math", 10))
        self.insert_markdown_for_reading(self.manual_text, USER_MANUAL)
        self.manual_text.configure(state="disabled")
        self.apply_native_palette()

    def _build_usage_tab(self):
        ttk.Label(self.usage_tab, text="Consumo de tokens e custos",
                  font=("Segoe UI", 13, "bold")).pack(anchor="w", pady=(2, 4))
        self.usage_estimate_notice = ttk.Label(self.usage_tab,
                  text="ESTIMATIVA — Não é uma cobrança da sua conta. Usa tokens registrados e tarifas/câmbio salvos em cada turno. Registros antigos usam referências atuais; recalcular é opcional.",
                  style="Hint.TLabel", wraplength=950, justify="left")
        self.usage_estimate_notice.pack(anchor="w", fill="x", pady=(0, 10))
        controls = ttk.LabelFrame(self.usage_tab, text="Período e moeda", padding=8)
        controls.pack(fill="x", pady=(0, 10))
        ttk.Label(controls, text="Período:").pack(side="left")
        self.usage_period_box = ttk.Combobox(
            controls, textvariable=self.usage_period_var,
            values=("Hoje", "Últimos 7 dias", "Este mês", "Este ano", "Todo o período", "Personalizado"),
            state="readonly", width=18)
        self.usage_period_box.pack(side="left", padx=(6, 16))
        self.usage_period_box.bind("<<ComboboxSelected>>", self.on_usage_period_changed)
        ttk.Label(controls, text="Moeda:").pack(side="left")
        self.usage_currency_box = ttk.Combobox(
            controls, textvariable=self.usage_currency_var,
            values=("Automática", "USD", "BRL", "EUR"), state="readonly", width=14)
        self.usage_currency_box.pack(side="left", padx=(6, 16))
        self.usage_currency_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh_usage_dashboard())
        ttk.Label(controls, text="Modelo:").pack(side="left")
        self.usage_model_box = ttk.Combobox(controls, textvariable=self.usage_model_var,
            values=("Todos os modelos", "Luna", "Terra", "Sol", "Astra"),
            state="readonly", width=16)
        self.usage_model_box.pack(side="left", padx=(6, 16))
        self.usage_model_box.bind("<<ComboboxSelected>>", lambda _event: self.refresh_usage_dashboard())
        ttk.Button(controls, text="Atualizar", command=self.refresh_usage_dashboard).pack(side="left")
        ttk.Button(controls, text="Exportar CSV...", command=self.export_usage_csv).pack(side="left", padx=(8, 0))
        ttk.Checkbutton(self.usage_tab, text='Recalcular com tarifas e câmbio atuais',
            variable=self.recalculate_costs_var, command=self.refresh_usage_dashboard).pack(anchor='w', pady=(0,8))
        self.usage_custom_range = ttk.Frame(self.usage_tab)
        ttk.Label(self.usage_custom_range, text="De (DD/MM/AAAA):").pack(side="left")
        self.usage_start_entry = ttk.Entry(self.usage_custom_range, width=14)
        self.usage_start_entry.pack(side="left", padx=(6, 14))
        ttk.Label(self.usage_custom_range, text="Até (DD/MM/AAAA):").pack(side="left")
        self.usage_end_entry = ttk.Entry(self.usage_custom_range, width=14)
        self.usage_end_entry.pack(side="left", padx=6)
        for entry in (self.usage_start_entry, self.usage_end_entry):
            entry.bind("<Return>", lambda _event: self.refresh_usage_dashboard())
        self.usage_totals_box = ttk.LabelFrame(self.usage_tab, text="Totais do período", padding=10)
        totals = self.usage_totals_box
        totals.pack(fill="x", pady=(0, 10))
        ttk.Label(totals, textvariable=self.usage_summary_var,
                  font=("Segoe UI", 11, "bold"), wraplength=950, justify="left").pack(anchor="w")
        ttk.Label(totals, textvariable=self.usage_range_var,
                  style="Hint.TLabel").pack(anchor="w", pady=(5, 0))
        ttk.Label(totals, textvariable=self.usage_records_var,
                  style="Hint.TLabel").pack(anchor="w", pady=(3, 0))
        self.usage_excluded_label = ttk.Label(totals, textvariable=self.usage_excluded_var,
                  style="Hint.TLabel", wraplength=950, justify="left")
        self.usage_excluded_label.pack(anchor="w", pady=(3, 0))
        breakdown = ttk.LabelFrame(self.usage_tab, text="Por intervalo", padding=6)
        breakdown.pack(fill="both", expand=True)
        holder = ttk.Frame(breakdown)
        holder.pack(fill="both", expand=True)
        columns = ("periodo", "modelo", "tarefas", "entrada", "cache", "saida", "raciocinio", "custo")
        self.usage_table = ttk.Treeview(holder, columns=columns, show="headings", height=12)
        titles = {"periodo": "Período", "modelo": "Modelo", "tarefas": "Tarefas", "entrada": "Entrada",
                  "cache": "Cache", "saida": "Saída", "raciocinio": "Raciocínio", "custo": "Custo estimado"}
        widths = {"periodo": 150, "modelo": 105, "tarefas": 80, "entrada": 115, "cache": 115,
                  "saida": 110, "raciocinio": 115, "custo": 145}
        for column in columns:
            self.usage_table.heading(column, text=titles[column], anchor="center")
            self.usage_table.column(column, width=widths[column], minwidth=widths[column], stretch=False, anchor="center")
        add_vertical_scrollbar(holder, self.usage_table)


    def export_usage_csv(self):
        """Export the visible usage breakdown to a spreadsheet-friendly CSV."""
        import csv
        destination = filedialog.asksaveasfilename(
            title=self.tr("Exportar consumo"), defaultextension=".csv",
            filetypes=(("CSV", "*.csv"),))
        if not destination:
            return
        try:
            with open(destination, "w", newline="", encoding="utf-8-sig") as stream:
                writer = csv.writer(stream, delimiter=";")
                writer.writerow([self.usage_table.heading(col, "text") for col in self.usage_table["columns"]])
                for item in self.usage_table.get_children():
                    writer.writerow(self.usage_table.item(item, "values"))
            messagebox.showinfo("Consumo", "Resumo exportado com sucesso.")
        except OSError as exc:
            messagebox.showerror("Consumo", str(exc))

    def refresh_usage_dashboard(self):
        if not hasattr(self, "usage_table"):
            return
        for item in self.usage_table.get_children():
            self.usage_table.delete(item)
        records = self.record_cache
        if records is None:
            records = []
            self.record_cache = records
        period_value = self.usage_period_var.get()
        canonical = next((label for label in ("Hoje", "Últimos 7 dias", "Este mês", "Este ano", "Todo o período", "Personalizado")
                          if self.tr(label) == period_value), period_value)
        now = datetime.now().astimezone()
        today = now.date()
        custom_start = custom_end = None
        if canonical == "Hoje":
            start, end = today, today
        elif canonical == "Últimos 7 dias":
            start, end = today - timedelta(days=6), today
        elif canonical == "Este mês":
            start, end = today.replace(day=1), today
        elif canonical == "Este ano":
            start, end = today.replace(month=1, day=1), today
        elif canonical == "Personalizado":
            try:
                custom_start = self._parse_usage_date(self.usage_start_entry.get())
                custom_end = self._parse_usage_date(self.usage_end_entry.get())
                if custom_start > custom_end:
                    raise ValueError("A data inicial deve ser anterior à data final.")
            except ValueError:
                self.usage_summary_var.set(self.tr("Informe um intervalo válido no formato DD/MM/AAAA."))
                self.usage_range_var.set("")
                self.usage_records_var.set("")
                return
            start, end = custom_start, custom_end
        else:
            start, end = date.min, today

        currency_label = self.usage_currency_var.get()
        currency = currency_label if currency_label in {"USD", "BRL", "EUR"} else (
            {"pt-BR": "BRL", "es": "EUR"}.get(self.language, "USD"))
        model_value = self.usage_model_var.get()
        model_key = next((key for key in gate.MODELS
                          if self.tr(model_label(key)) == model_value), None)
        if model_value in {self.tr("Todos os modelos"), "Todos os modelos"}:
            model_key = None
        symbols = {"USD": "US$", "BRL": "R$", "EUR": "€"}
        aggregate = {key: 0 for key in ("input", "cached_input", "output", "reasoning")}
        total_cost, counted, unknown = 0.0, 0, 0
        groups = {}
        period_records = eligible = 0
        earliest_day = None
        for record in usage_records(records):
            raw_date = str(record.get("finished_at") or "")
            try:
                finished = datetime.fromisoformat(raw_date.replace("Z", "+00:00")).astimezone()
            except (ValueError, TypeError, OSError):
                continue
            day = finished.date()
            if day < start or day > end:
                continue
            record_model = str(record.get("model_key") or "").lower()
            if model_key and record_model != model_key:
                continue
            period_records += 1
            earliest_day = day if earliest_day is None else min(earliest_day, day)
            usage = record.get("token_usage")
            if not isinstance(usage, dict) or not record_model or record_model not in gate.MODELS:
                unknown += 1
                continue
            cost = gate.estimate_token_cost(str(record.get("model_key") or ""), usage, currency, None if self.recalculate_costs_var.get() else record.get("pricing"), None if self.recalculate_costs_var.get() else record.get("exchange_rates"))
            if cost is None:
                unknown += 1
                continue
            eligible += 1
            counted += 1
            total_cost += cost
            for key in aggregate:
                aggregate[key] += max(0, int(usage.get(key, 0) or 0))
            if canonical == "Hoje":
                group_key = finished.strftime("%H:00")
            elif canonical in {"Últimos 7 dias", "Este mês", "Personalizado"}:
                group_key = day.isoformat()
            elif canonical in {"Este ano", "Todo o período"}:
                group_key = day.strftime("%Y-%m")
            else:
                group_key = day.isoformat()
            current = groups.setdefault((group_key, self.tr(model_label(record_model))), {**{key: 0 for key in aggregate}, "tasks": 0, "cost": 0.0})
            current["tasks"] += 1
            for key in aggregate:
                current[key] += max(0, int(usage.get(key, 0) or 0))
            current["cost"] += cost
        for (label, model_name), values in sorted(groups.items(), reverse=True):
            displayed_period = self._format_usage_month(label) if canonical in {
                "Este ano", "Todo o período"} else (
                label if canonical == "Hoje" else self._format_usage_date(date.fromisoformat(label)))
            self.usage_table.insert("", "end", values=(
                displayed_period, model_name, self._format_integer(values["tasks"]),
                self._format_integer(values["input"]),
                self._format_integer(values["cached_input"]),
                self._format_integer(values["output"]),
                self._format_integer(values["reasoning"]),
                f'{symbols[currency]} {self._format_estimated_cost(values["cost"])}'))
        self.usage_summary_var.set(
            f'{self.tr("Custo total estimado")}: {symbols[currency]} {self._format_estimated_cost(total_cost)}'
            f'   •   {self.tr("Tarefas com uso informado")}: {self._format_integer(counted)}')
        displayed_start = earliest_day if canonical == "Todo o período" else start
        displayed_range = (f'{self._format_usage_date(displayed_start)} — '
                           f'{self._format_usage_date(end)}') if displayed_start else "—"
        self.usage_range_var.set(
            f'{self.tr("Período")}: {displayed_range}')
        self.usage_records_var.set(
            f'{self.tr("Tokens")}: {self.tr("entrada")} {self._format_integer(aggregate["input"])}  •  '
            f'{self.tr("cache")} {self._format_integer(aggregate["cached_input"])}  •  '
            f'{self.tr("saída")} {self._format_integer(aggregate["output"])}  •  '
            f'{self.tr("raciocínio")} {self._format_integer(aggregate["reasoning"])}' +
            (f'  •  {self.tr("Sem dados para estimar o custo")}: {self._format_integer(unknown)}' if unknown else ""))
        excluded = max(0, period_records - eligible)
        self.usage_excluded_var.set(
            f'{self.tr("Registros no período")}: {self._format_integer(period_records)}  •  '
            f'{self.tr("Incluídos nos totais")}: {self._format_integer(eligible)}  •  '
            f'{self.tr("Excluídos por falta de dados de tokens ou modelo")}: {self._format_integer(excluded)}')
        self.usage_period_box.configure(values=[self.tr(value) for value in
            ("Hoje", "Últimos 7 dias", "Este mês", "Este ano", "Todo o período", "Personalizado")])
        self.usage_currency_box.configure(values=[self.tr(value) for value in
            ("Automática", "USD", "BRL", "EUR")])
        self.usage_model_box.configure(values=[self.tr("Todos os modelos")] + [
            self.tr(model_label(key)) for key in gate.MODELS])
        if self.usage_model_var.get() in {"Todos os modelos", "All models", "Todos los modelos"}:
            self.usage_model_var.set(self.tr("Todos os modelos"))

    def _usage_period_key(self):
        return next((label for label in ("Hoje", "Últimos 7 dias", "Este mês", "Este ano", "Todo o período", "Personalizado")
                     if self.tr(label) == self.usage_period_var.get()), self.usage_period_var.get())

    def on_usage_period_changed(self, _event=None):
        if self._usage_period_key() == "Personalizado":
            self.usage_custom_range.pack(fill="x", pady=(0, 8))
        else:
            self.usage_custom_range.pack_forget()
        self.refresh_usage_dashboard()

    def apply_native_palette(self):
        """Apply the same visual tokens to classic Tk text and list controls."""
        colors = UI_COLORS

        def visit(widget):
            if isinstance(widget, tk.Canvas):
                widget.configure(bg=colors["surface"])
            elif isinstance(widget, tk.Text):
                widget.configure(
                    bg=colors["surface"], fg=colors["text"],
                    insertbackground=colors["primary_dark"],
                    selectbackground=colors["selection"], selectforeground=colors["text"],
                    highlightthickness=1, highlightbackground=colors["border"],
                    highlightcolor=colors["primary"])
            elif isinstance(widget, tk.Listbox):
                widget.configure(
                    bg=colors["surface"], fg=colors["text"],
                    selectbackground=colors["primary"], selectforeground="#FFFFFF",
                    highlightthickness=1, highlightbackground=colors["border"],
                    highlightcolor=colors["primary"], relief="flat")
            for child in widget.winfo_children():
                visit(child)

        visit(self)

    def tr(self, text: str) -> str:
        return gate_i18n.translate(text, self.language)

    def install_localized_dialogs(self):
        """Translate all Tk dialogs, including messages created after startup."""
        for name, original in _MESSAGEBOX_FUNCTIONS.items():
            def localized(title, message, *args, _original=original, **kwargs):
                kwargs.setdefault("parent", self)
                return _original(self.tr(str(title)), self.tr(str(message)), *args, **kwargs)
            setattr(messagebox, name, localized)

        def localized_askstring(title, prompt, *args, **kwargs):
            kwargs.setdefault("parent", self)
            return _SIMPLEDIALOG_ASKSTRING(
                self.tr(str(title)), self.tr(str(prompt)), *args, **kwargs)
        simpledialog.askstring = localized_askstring

        for name, original in _FILEDIALOG_FUNCTIONS.items():
            def localized_file_dialog(*args, _original=original, **kwargs):
                if "title" in kwargs:
                    kwargs["title"] = self.tr(str(kwargs["title"]))
                if "filetypes" in kwargs:
                    kwargs["filetypes"] = [
                        (self.tr(str(label)), pattern)
                        for label, pattern in kwargs["filetypes"]
                    ]
                return _original(*args, **kwargs)
            setattr(filedialog, name, localized_file_dialog)

    def localize_interface(self):
        """Translate static widget text without coupling language packs to layout code."""
        self.title(self.tr("Codex Model Gate — Decisão Confiável de IA") +
                   f" v{APP_VERSION}")
        for widget in self.winfo_children():
            self._localize_widget(widget)
        for index, source in enumerate(
                ("Tarefa", "Resposta", "Tarefas anteriores", "Arquivos", "Consumo", "Manual")):
            self.main_notebook.tab(index, text=self.tr(source))
        heading_sources = {
            "quando": "Data", "resultado": "Status", "qualidade": "Resultado",
            "modelo": "Modelo", "tarefa": "Tarefa",
        }
        for column, source in heading_sources.items():
            self.history.heading(column, text=self.tr(source))
        usage_heading_sources = {
            "periodo": "Período", "modelo": "Modelo", "tarefas": "Tarefas",
            "entrada": "Entrada", "cache": "Cache", "saida": "Saída",
            "raciocinio": "Raciocínio", "custo": "Custo estimado",
        }
        for column, source in usage_heading_sources.items():
            self.usage_table.heading(column, text=self.tr(source))
        self.quality_box.configure(values=[self.tr(value) for value in (
            "Não avaliado", "Aprovado", "Precisou de ajustes", "Falhou")])
        self.policy_box.configure(values=[self.tr(value) for value in gate.POLICIES])
        self.policy_var.set(self.tr(self.policy_var.get()))
        self.effort_box.configure(values=[
            self.tr(gate.EFFORT_LABELS[k]) for k in gate.supported_efforts(model_key(self.model_var.get()) or "sol")])
        for variable in (
                self.files_context_var, self.record_filter_status,
                self.decision_model_card_var, self.simple_progress_var,
                self.skill_library_status, self.status, self.phase_var,
                self.elapsed_var, self.remaining_var, self.decision_text,
                self.decision_checklist_var, self.artifact_preview_var,
                self.cli_status_var, self.portable_storage_var,
                self.skill_search_status, self.decision_effort_card_var,
                self.decision_risk_card_var, self.decision_skills_card_var,
                self.usage_summary_var, self.usage_records_var, self.usage_range_var):
            variable.set(self.tr(variable.get()))
            self._keep_variable_localized(variable)
        template_sources = list(TASK_TEMPLATES)
        self.template_box.configure(values=[self.tr(value) for value in template_sources])
        self.template_var.set(self.tr(self.template_var.get()))
        self.manual_text.configure(state="normal")
        self.manual_text.delete("1.0", tk.END)
        self.insert_markdown_for_reading(
            self.manual_text, gate_i18n.manual(USER_MANUAL, self.language))
        self.manual_text.configure(state="disabled")
        self.usage_period_box.configure(values=[self.tr(value) for value in
            ("Hoje", "Últimos 7 dias", "Este mês", "Este ano", "Todo o período", "Personalizado")])
        self.usage_period_var.set(self.tr(self.usage_period_var.get()))
        if self._usage_period_key() == "Personalizado":
            self.usage_custom_range.pack(fill="x", pady=(0, 8))
        self.usage_currency_box.configure(values=[self.tr(value) for value in
            ("Automática", "USD", "BRL", "EUR")])
        self.usage_model_box.configure(values=[self.tr("Todos os modelos")] + [
            self.tr(key.capitalize()) for key in gate.MODELS])
        self.usage_excluded_label.configure(text=self.usage_excluded_var.get())
        self.usage_totals_box.configure(text=self.tr("Totais do período"))
        if self.usage_model_var.get() in {"Todos os modelos", "All models", "Todos los modelos"}:
            self.usage_model_var.set(self.tr("Todos os modelos"))
        else:
            usage_key = next((key for key in (*gate.PRIMARY_MODELS, *gate.LEGACY_MODELS)
                              if self.tr(key.capitalize()) == self.usage_model_var.get()), None)
            if usage_key:
                self.usage_model_var.set(self.tr(usage_key.capitalize()))
        self.usage_totals_box.configure(text=self.tr("Totais do período"))
        self.usage_excluded_label.configure(text=self.usage_excluded_var.get())
        self.usage_currency_var.set(self.tr(self.usage_currency_var.get()))
        if self.record_cache is not None:
            self.refresh_usage_dashboard()

    def _keep_variable_localized(self, variable: tk.StringVar):
        changing = False

        def translate_value(*_args):
            nonlocal changing
            if changing:
                return
            current = variable.get()
            translated = self.tr(current)
            if translated != current:
                changing = True
                try:
                    variable.set(translated)
                finally:
                    changing = False
        variable.trace_add("write", translate_value)

    def _localize_widget(self, widget):
        try:
            text = widget.cget("text")
        except (tk.TclError, AttributeError):
            text = ""
        if isinstance(text, str) and text:
            translated = self.tr(text)
            if translated != text:
                try:
                    widget.configure(text=translated)
                except tk.TclError:
                    pass
        for child in widget.winfo_children():
            self._localize_widget(child)

    def change_language(self, _event=None):
        if self.running or self.selecting_skills or self.busy_operation:
            self.language_var.set(gate_i18n.LANGUAGES[self.language])
            return messagebox.showinfo('Atividade em andamento', 'Aguarde a atividade terminar antes de alterar o idioma.')
        self.save_draft()
        selected = self.language_var.get()
        language = next(
            (code for code, name in gate_i18n.LANGUAGES.items() if name == selected),
            self.language)
        if language == self.language:
            return
        gate.save_app_settings({"language": language})
        prompts = {
            "pt-BR": ("Idioma alterado", "O novo idioma será aplicado agora. O programa será reiniciado."),
            "en": ("Language changed", "The new language will now be applied. The application will restart."),
            "es": ("Idioma cambiado", "El nuevo idioma se aplicará ahora. La aplicación se reiniciará."),
        }
        title, message = prompts[language]
        messagebox.showinfo(title, message)
        try:
            self.launch_fresh_instance()
        except OSError as exc:
            messagebox.showwarning(
                title,
                f"{message}\n\nNão foi possível reiniciar automaticamente: {exc}\n"
                "Feche e abra o programa para aplicar a escolha.")
            return
        self.destroy()

    @staticmethod
    def launch_fresh_instance():
        """Restart a source or PyInstaller build without reusing its _MEI directory."""
        environment = dict(os.environ)
        environment["PYINSTALLER_RESET_ENVIRONMENT"] = "1"
        if getattr(sys, "frozen", False):
            command = [sys.executable, *sys.argv[1:]]
        else:
            command = [sys.executable, *sys.argv]
        return subprocess.Popen(command, env=environment, close_fds=True)

    @staticmethod
    def _set_pack_visibility(widget, visible, options):
        if hasattr(widget, '_flow_hidden'):
            widget._flow_hidden = not visible
            widget.master._flow_refresh()
        elif visible and not widget.winfo_manager():
            widget.pack(**options)
        elif not visible and widget.winfo_manager():
            widget.pack_forget()


    def apply_ui_mode(self):
        advanced = bool(self.ui_mode_var.get())
        self._set_pack_visibility(self.decision_controls_line, advanced, {'fill': 'x'})
        self._set_pack_visibility(self.log_holder, advanced, {'side':'left', 'fill':'both', 'expand':True})
        self._set_pack_visibility(self.library_box, advanced, {'fill':'x', 'pady':(0,8), 'after':self.decision_box})
        self._set_pack_visibility(self.skills_browser, advanced, {'fill':'x', 'before':self.active_skills_box})
        # CLI recovery actions stay visible in simple mode.
        self._set_pack_visibility(self.cli_controls, advanced, {'anchor':'w', 'pady':(6,0)})
        for widget in (self.open_gate_data_button, self.backup_button, self.restore_backup_button):
            self._set_pack_visibility(widget, advanced, {'side':'left', 'padx':(8,0)})


    def apply_task_template(self, _event=None):
        selected_template = self.template_var.get()
        template = next(
            (source for source in TASK_TEMPLATES if self.tr(source) == selected_template),
            selected_template)
        content = self.tr(TASK_TEMPLATES.get(template, ""))
        if not content:
            return
        current = self.task.get("1.0", tk.END).strip()
        if current and not messagebox.askyesno(
                "Usar modelo de tarefa",
                "Substituir o texto atual pelo modelo escolhido?"):
            self.template_var.set(self.tr("Escolha um modelo..."))
            return
        self.task.delete("1.0", tk.END)
        self.task.insert("1.0", content)
        self.task.focus_set()
        self.status.set(
            "Modelo inserido. Troque os trechos entre colchetes antes de analisar a tarefa.")

    def analyze_from_shortcut(self, _event=None):
        if not self.running and not self.selecting_skills:
            self.recommend()
        return "break"

    def execute_from_shortcut(self, _event=None):
        if not self.running and not self.selecting_skills:
            self.authorize_run()
        return "break"

    def show_manual_tab(self):
        self.main_notebook.select(self.manual_tab)

    def show_onboarding_if_needed(self):
        settings = gate.load_app_settings()
        if settings.get("onboarding_completed"):
            return
        welcome = tk.Toplevel(self)
        welcome.title("Boas-vindas ao Codex Model Gate")
        welcome.transient(self)
        welcome.resizable(False, False)
        welcome.grab_set()
        holder = ttk.Frame(welcome, padding=18)
        holder.pack(fill="both", expand=True)
        ttk.Label(holder, text="Comece em poucos passos",
                  font=("Segoe UI", 14, "bold")).pack(anchor="w")
        ttk.Label(
            holder,
            text=("1. Descreva o resultado que você quer.\n\n"
                  "2. Clique em Analisar tarefa e confira a recomendação.\n\n"
                  "3. Confirme a execução somente depois de revisar skills, anexos e destino.\n\n"
                  "4. Abra os resultados e registre sua avaliação."),
            justify="left", wraplength=440).pack(anchor="w", pady=(10, 16))

        def finish():
            gate.save_app_settings({"onboarding_completed": True})
            welcome.destroy()

        ttk.Button(holder, text="Entendi, começar", command=finish).pack(anchor="e")
        welcome.protocol("WM_DELETE_WINDOW", finish)
        self.wait_window(welcome)

    def show_response(self, output, select=True):
        """Expose the final answer independently from the advanced technical log."""
        self.last_response_text = str(output or "").strip()
        self.response_text.configure(state="normal")
        self.response_text.delete("1.0", tk.END)
        if self.last_response_text:
            self.insert_markdown_for_reading(
                self.response_text, self.last_response_text)
        else:
            self.response_text.insert(
                tk.END, "O Codex não retornou uma resposta textual. Confira os arquivos criados.")
        self.response_text.configure(state="disabled")
        self.response_text.see("1.0")
        if select:
            self.main_notebook.select(self.response_tab)

    def abrir_leitor_focado(self):
        # Cria uma nova janela independente
        leitor = tk.Toplevel(self)
        leitor.title("Resposta Final da Tarefa")
        leitor.state("zoomed")
        leitor.configure(bg="#f4f4f4")

        try:
            # A resposta final fica separada do log técnico. O log permanece
            # como contingência para registros iniciados em versões antigas.
            texto_bruto = (self.last_response_text or
                           self.log.get("1.0", tk.END).strip())

            # Aplica o filtro para extrair apenas a resposta textual
            resposta_limpa = texto_bruto

            # 1. Pula os registros de internet e terminal buscando a última fala do modelo
            if "\ncodex\n" in texto_bruto:
                resposta_limpa = texto_bruto.split("\ncodex\n")[-1]
            elif texto_bruto.startswith("codex\n"):
                resposta_limpa = texto_bruto.split("codex\n")[-1]

            # 2. Corta o rodapé que contabiliza os tokens usados
            if "\ntokens used" in resposta_limpa:
                resposta_limpa = resposta_limpa.split("\ntokens used")[0]

            resposta_limpa = resposta_limpa.strip()

            # Fallback de segurança: se a filtragem falhar, mostra o original
            if not resposta_limpa:
                resposta_limpa = texto_bruto

        except Exception:
            resposta_limpa = "Erro ao processar o log."

        # Constrói a área de leitura limpa. O conteúdo vindo do Codex costuma
        # estar em Markdown; ele é mostrado com sua formatação, não com marcas.
        area = ttk.Frame(leitor, padding=20)
        area.pack(fill="both", expand=True)
        scroll = ttk.Scrollbar(area, orient="vertical")
        texto_leitor = tk.Text(
            area,
            wrap="word",
            font=("Segoe UI", 12),
            padx=32,
            pady=28,
            bg="#ffffff",
            fg="#222222",
            relief="flat",
            yscrollcommand=scroll.set,
        )
        scroll.configure(command=texto_leitor.yview)
        texto_leitor.tag_configure("heading1", font=("Segoe UI", 18, "bold"), spacing1=10, spacing3=8)
        texto_leitor.tag_configure("heading2", font=("Segoe UI", 15, "bold"), spacing1=8, spacing3=6)
        texto_leitor.tag_configure("bold", font=("Segoe UI", 12, "bold"))
        texto_leitor.tag_configure("italic", font=("Segoe UI", 12, "italic"))
        texto_leitor.tag_configure("code", font=("Cascadia Mono", 11), background="#eef1f5")
        texto_leitor.tag_configure("quote", foreground="#4c5f73", lmargin1=18, lmargin2=18)
        # Cambria Math is bundled with Windows and covers mathematical,
        # chemical and biological Unicode notation that may not exist in a
        # normal text font.
        texto_leitor.tag_configure("symbol", font=("Cambria Math", 12))
        self.insert_markdown_for_reading(texto_leitor, resposta_limpa)
        texto_leitor.config(state="disabled")  # Trava a edição do texto
        scroll.pack(side="right", fill="y")
        texto_leitor.pack(side="left", fill="both", expand=True)

    @staticmethod
    def insert_markdown_for_reading(widget: tk.Text, markdown: str):
        """Render Markdown as comfortable reading text, including tables."""
        in_code_block = False
        lines = markdown.splitlines()
        index = 0
        while index < len(lines):
            raw_line = lines[index]
            line = raw_line.rstrip()
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                index += 1
                continue
            if in_code_block:
                GateApp.insert_markdown_inline(widget, line + "\n", "code")
                index += 1
                continue
            if (index + 1 < len(lines) and GateApp.is_markdown_table_row(line)
                    and GateApp.is_markdown_table_separator(lines[index + 1])):
                headers = GateApp.parse_markdown_table_row(line)
                index += 2
                rows = []
                while index < len(lines) and GateApp.is_markdown_table_row(lines[index]):
                    rows.append(GateApp.parse_markdown_table_row(lines[index]))
                    index += 1
                GateApp.insert_readable_table(widget, headers, rows)
                continue
            heading = re.match(r"^(#{1,2})\s+(.+)$", line)
            if heading:
                GateApp.insert_markdown_inline(
                    widget, heading.group(2) + "\n", "heading" + str(len(heading.group(1))))
                index += 1
                continue
            quote = re.match(r"^\s*>\s?(.*)$", line)
            if quote:
                GateApp.insert_markdown_inline(widget, quote.group(1) + "\n", "quote")
                index += 1
                continue
            bullet = re.match(r"^(\s*)[-*+]\s+(.+)$", line)
            if bullet:
                widget.insert(tk.END, bullet.group(1) + "• ")
                GateApp.insert_markdown_inline(widget, bullet.group(2) + "\n")
                index += 1
                continue
            numbered = re.match(r"^(\s*)(\d+[.)])\s+(.+)$", line)
            if numbered:
                widget.insert(tk.END, numbered.group(1) + numbered.group(2) + " ")
                GateApp.insert_markdown_inline(widget, numbered.group(3) + "\n")
                index += 1
                continue
            GateApp.insert_markdown_inline(widget, line + "\n")
            index += 1

    @staticmethod
    def is_markdown_table_row(line: str) -> bool:
        return line.count("|") >= 2

    @staticmethod
    def is_markdown_table_separator(line: str) -> bool:
        cells = GateApp.parse_markdown_table_row(line)
        return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)

    @staticmethod
    def parse_markdown_table_row(line: str) -> list[str]:
        return [cell.strip() for cell in line.strip().strip("|").split("|")]

    @staticmethod
    def insert_readable_table(widget: tk.Text, headers: list[str], rows: list[list[str]]):
        """Present Markdown tables as labelled cards instead of literal pipes."""
        for row_number, row in enumerate(rows, start=1):
            if row_number > 1:
                widget.insert(tk.END, "\n")
            for header, value in zip(headers, row):
                GateApp.insert_markdown_inline(widget, header + ": ", "bold")
                GateApp.insert_markdown_inline(widget, value + "\n")
        if rows:
            widget.insert(tk.END, "\n")

    @staticmethod
    def insert_markdown_inline(widget: tk.Text, text: str, base_tag: str | None = None):
        text = GateApp.clean_reading_text(text)
        pattern = re.compile(
            r"(?P<markdown_link>\[(?P<link_label>[^\]\n]+)\]"
            r"\((?P<link_url>https?://[^\s)]+)\))"
            r"|(?P<bare_url>https?://[^\s<>\"']+)"
            r"|(?P<bold>\*\*.+?\*\*|__.+?__)"
            r"|(?P<code>`[^`]+`)"
            r"|(?P<italic>\*[^*\n]+\*|(?<!\w)_[^_\n]+_)",
            re.IGNORECASE,
        )

        def insert_piece(piece: str, tag: str | None = None):
            if tag:
                widget.insert(tk.END, piece, tag)
            else:
                # Preserve ordinary prose in Segoe UI while giving formulas a
                # Windows math font with broad Unicode coverage.
                symbol_pattern = r"[₀-₉⁰-⁹⁺⁻⁼⁽⁾ⁿᵃᵇᶜᵈᵉᶠᵍʰⁱʲᵏˡᵐᵒᵖʳˢᵗᵘᵛʷˣʸᶻα-ωΑ-Ω∑∏√∞≈≠≤≥±×÷→←↔•·]"
                position = 0
                for symbol in re.finditer(symbol_pattern, piece):
                    if symbol.start() > position:
                        widget.insert(tk.END, piece[position:symbol.start()])
                    widget.insert(tk.END, symbol.group(0), "symbol")
                    position = symbol.end()
                if position < len(piece):
                    widget.insert(tk.END, piece[position:])

        position = 0
        for match in pattern.finditer(text):
            if match.start() > position:
                insert_piece(text[position:match.start()], base_tag)
            token = match.group(0)
            if match.lastgroup == "markdown_link":
                GateApp.insert_web_link(
                    widget, match.group("link_label"), match.group("link_url"), base_tag)
            elif match.lastgroup == "bare_url":
                url, punctuation = GateApp.trim_web_url_punctuation(token)
                if GateApp.is_safe_web_url(url):
                    GateApp.insert_web_link(widget, url, url, base_tag)
                else:
                    insert_piece(url, base_tag)
                if punctuation:
                    insert_piece(punctuation, base_tag)
            elif match.lastgroup == "bold":
                widget.insert(tk.END, token[2:-2], "bold")
            elif match.lastgroup == "code":
                widget.insert(tk.END, token[1:-1], "code")
            else:
                widget.insert(tk.END, token[1:-1], "italic")
            position = match.end()
        if position < len(text):
            insert_piece(text[position:], base_tag)

    @staticmethod
    def trim_web_url_punctuation(url: str) -> tuple[str, str]:
        """Separate sentence punctuation without breaking balanced URL brackets."""
        punctuation = ""
        while url and url[-1] in ".,;:!?":
            punctuation = url[-1] + punctuation
            url = url[:-1]
        for closing, opening in ((")", "("), ("]", "["), ("}", "{")):
            while url.endswith(closing) and url.count(closing) > url.count(opening):
                punctuation = closing + punctuation
                url = url[:-1]
        return url, punctuation

    @staticmethod
    def is_safe_web_url(url: str) -> bool:
        """Accept only complete HTTP(S) links suitable for the system browser."""
        if not url or any(ord(character) < 32 for character in url):
            return False
        try:
            parsed = urlparse(url)
            _ = parsed.port  # Reject malformed ports instead of passing them onward.
        except ValueError:
            return False
        return (
            parsed.scheme.lower() in {"http", "https"}
            and bool(parsed.hostname)
            and parsed.username is None
            and parsed.password is None
        )

    @staticmethod
    def insert_web_link(
            widget: tk.Text, label: str, url: str, base_tag: str | None = None):
        """Insert one accessible-looking hyperlink and bind it to the default browser."""
        if not GateApp.is_safe_web_url(url):
            widget.insert(tk.END, label, base_tag) if base_tag else widget.insert(tk.END, label)
            return
        counter = int(getattr(widget, "_gate_link_counter", 0)) + 1
        setattr(widget, "_gate_link_counter", counter)
        event_tag = f"gate_web_link_{counter}"
        tags = tuple(tag for tag in (base_tag, "web_link", event_tag) if tag)
        widget.tag_configure("web_link", foreground="#0563C1", underline=True)
        widget.insert(tk.END, label, tags)
        widget.tag_bind(
            event_tag, "<Button-1>",
            lambda _event, target=url: GateApp.open_web_link(target))
        widget.tag_bind(
            event_tag, "<Enter>",
            lambda _event, target=widget: target.configure(cursor="hand2"))
        widget.tag_bind(
            event_tag, "<Leave>",
            lambda _event, target=widget: target.configure(cursor="xterm"))

    @staticmethod
    def open_web_link(url: str):
        if not GateApp.is_safe_web_url(url):
            messagebox.showerror("Link inválido", "Este endereço não pode ser aberto com segurança.")
            return
        try:
            opened = webbrowser.open_new_tab(url)
        except (OSError, webbrowser.Error):
            opened = False
        if not opened:
            messagebox.showerror(
                "Não foi possível abrir o link",
                "Confira se existe um navegador padrão configurado no Windows.")

    @staticmethod
    def clean_reading_text(text: str) -> str:
        """Keep symbols intact and normalize common typed/LaTex notation."""
        # Dashes used as an aside are displayed as conventional Portuguese
        # punctuation. Hyphens inside terms, such as "local-alvo", remain.
        text = re.sub(r"\s+[—–]\s+", ", ", text)
        replacements = {
            r"\alpha": "α", r"\beta": "β", r"\gamma": "γ",
            r"\delta": "δ", r"\Delta": "Δ", r"\mu": "μ",
            r"\pi": "π", r"\sigma": "σ", r"\omega": "ω",
            r"\Omega": "Ω", r"\times": "×", r"\div": "÷",
            r"\pm": "±", r"\leq": "≤", r"\geq": "≥",
            r"\neq": "≠", r"\approx": "≈", r"\infty": "∞",
            r"\rightarrow": "→", r"\leftarrow": "←",
            r"\leftrightarrow": "↔", r"\sqrt": "√",
            r"\cdot": "·", r"\bullet": "•",
        }
        for source, replacement in replacements.items():
            text = text.replace(source, replacement)
        # Remove simple LaTex wrappers, then convert formula exponents and
        # indices to Unicode. This keeps H₂O₂, O₂•⁻, Ca²⁺, x² and ¹O₂ as
        # formulas, rather than replacing them with prose.
        text = re.sub(r"\\(?:mathrm|text|ce)\{([^{}]+)\}", r"\1", text)
        superscript = str.maketrans("0123456789+-=()n", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿ")
        subscript = str.maketrans("0123456789+-=()aehijklmnoprstuvx", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₐₑₕᵢⱼₖₗₘₙₒₚᵣₛₜᵤᵥₓ")
        text = re.sub(r"\^\{([^{}]+)\}", lambda match: match.group(1).replace(" ", "").translate(superscript), text)
        text = re.sub(r"(?<=\w)\^([0-9+\-=()n])", lambda match: match.group(1).translate(superscript), text)
        text = re.sub(r"_\{([^{}]+)\}", lambda match: match.group(1).translate(subscript), text)
        text = re.sub(r"(?<=\w)_([0-9+\-=()aehijklmnoprstuvx])", lambda match: match.group(1).translate(subscript), text)
        return text

    def _update_work_scrollregion(self, _event=None):
        self.work_canvas.configure(scrollregion=self.work_canvas.bbox("all"))

    def _resize_work_content(self, event):
        from gate_widgets import adapt_wraplength
        adapt_wraplength(self.work_tab, event.width)
        self.work_canvas.itemconfigure(
            self.work_canvas_window, width=event.width)

    def _widget_is_in_work_tab(self, widget):
        while widget is not None:
            if widget == self.work_tab:
                return True
            widget = getattr(widget, "master", None)
        return False

    def _on_main_mousewheel(self, event):
        if not self._widget_is_in_work_tab(event.widget):
            return None
        # Text and list controls need the wheel for their own content. Moving
        # over the surrounding form scrolls the complete task page.
        if isinstance(event.widget, (tk.Text, tk.Listbox, ttk.Treeview, ttk.Combobox)):
            return None
        delta = -1 if event.delta > 0 else 1
        self.work_canvas.yview_scroll(delta * 3, "units")
        return "break"

    def _on_page_scroll(self, event):
        if not self._widget_is_in_work_tab(event.widget):
            return None
        self.work_canvas.yview_scroll(-1 if event.keysym ==
                                      "Prior" else 1, "pages")
        return "break"

    def history_path(self): return gate.app_data_dir() / "history.json"

    def read_history(self):
        # The readable permanent records are the single source of truth.
        return [{**record, 'output': record.get('execution_output', '')} for record in (self.record_cache or [])]


    def add_history(self, status, output, validation=None):
        # Permanent Markdown records are authoritative; no second JSON history.
        if not self.run_id:
            self.run_id = str(self.pending.get('id') or uuid.uuid4().hex)

        # The permanent record is written immediately afterwards; refresh once then.

    def _record_matches_filters(self, entry):
        filters = {key: variable.get() for key, variable in self.record_filter_vars.items()}
        date_filter = filters.pop("date", "").strip().casefold()
        if not gate.execution_record_matches(entry, filters):
            return False
        if not date_filter:
            return True
        stored_date = str(entry.get("finished_at") or "")
        displayed_date = self._format_record_datetime(stored_date)
        return date_filter in displayed_date.casefold() or date_filter in stored_date.casefold()

    def schedule_history_search(self, _event=None):
        """Debounce live search so large histories do not make typing sluggish."""
        if self.history_search_after_id:
            self.after_cancel(self.history_search_after_id)
        self.history_search_after_id = self.after(250, lambda: self.load_history(force=False))

    def focus_history_search(self, _event=None):
        self.main_notebook.select(self.history_tab)
        self.history_search_entry.focus_set()
        self.history_search_entry.selection_range(0, tk.END)
        return "break"

    def clear_history_search(self):
        self.record_filter_vars["task"].set("")
        self.load_history()
        self.history_search_entry.focus_set()

    def clear_record_filters(self):
        for variable in self.record_filter_vars.values():
            variable.set("")
        self.load_history()

    def load_history(self, force=True):
        if self.history.selection():
            current = self.record_items.get(self.history.selection()[0], {})
            self._selected_record_id = current.get('id')
        if not force and self.record_cache is not None:
            self.render_history(self.record_cache)
            return
        self._history_request += 1
        request = self._history_request
        def present(records):
            if request == self._history_request:
                self.render_history(records)
                from gate_records import REPOSITORY
                if REPOSITORY.issues:
                    self.record_filter_status.set(self.record_filter_status.get() + ' — ' + '; '.join(REPOSITORY.issues[:3]))
        self.start_job('Carregar registros', gate.read_execution_records, present)

    def render_history(self, records):
        self.history_search_after_id = None
        for item in self.history.get_children():
            self.history.delete(item)
        self.record_items = {}
        self.record_artifact_items = []
        self.record_artifact_list.delete(0, tk.END)
        self.files_context_var.set(
            "Selecione uma tarefa na aba “Tarefas anteriores” para ver seus arquivos.")
        if hasattr(self, "continue_record_button"):
            self.continue_record_button.configure(state="disabled")
        previous = getattr(self, "_selected_record_id", None)
        self.record_cache = records
        filtered_records = [
            entry for entry in records if self._record_matches_filters(entry)]
        if self.show_only_unqualified:
            filtered_records = [entry for entry in filtered_records if entry.get(
                "quality", "Não avaliado") == "Não avaliado"]
        for index, entry in enumerate(filtered_records):
            item_id = f"record-{index}"
            self.record_items[item_id] = entry
            self.history.insert("", "end", iid=item_id, values=(self._format_record_datetime(entry.get("finished_at", "")), entry.get(
                "status", ""), entry.get("quality", "Não avaliado"), entry.get("model", ""), entry.get("task", "")))
        shown = len(filtered_records)
        self.record_filter_status.set(
            f"{self._format_integer(shown)} {self.tr('de')} {self._format_integer(len(records))} "
            f"{self.tr('registro exibido' if shown == 1 else 'registros exibidos')}")
        pending_count = sum(1 for entry in records if entry.get(
            "quality", "Não avaliado") == "Não avaliado")
        self.history_list_menu.entryconfigure(
            0, label=self.tr("Mostrar todos os registros" if self.show_only_unqualified
                             else f"Registros sem avaliação ({pending_count})"))
        self.record_detail.configure(state="normal")
        self.record_detail.delete("1.0", tk.END)
        if not self.record_items:
            self.record_detail.insert(
                tk.END, self.tr("Nenhum registro corresponde aos filtros atuais." if records else "Nenhum registro persistente encontrado ainda. Os próximos resultados executados pelo Gate serão salvos aqui, mesmo após fechar o programa."))
        self.record_detail.configure(state="disabled")
        self.refresh_usage_dashboard()
        if previous:
            for iid, record in self.record_items.items():
                if record.get('id') == previous:
                    self.history.selection_set(iid); self.history.see(iid)
                    self.show_selected_record()
                    break



    def _update_history_action_scroll(self, _event=None):
        """Keep history actions on one row and expose overflow horizontally."""
        if not self.history_actions_canvas.winfo_exists():
            return
        content = self.history_actions_frame
        required_width = content.winfo_reqwidth()
        required_height = content.winfo_reqheight()
        self.history_actions_canvas.configure(
            scrollregion=(0, 0, required_width, required_height))
        if int(self.history_actions_canvas.cget("height")) != required_height:
            self.history_actions_canvas.configure(height=required_height)
        if required_width > self.history_actions_canvas.winfo_width() + 2:
            self.history_actions_scrollbar.grid(
                row=1, column=0, sticky="ew", pady=(3, 0))
        else:
            self.history_actions_scrollbar.grid_remove()
            self.history_actions_canvas.xview_moveto(0)

    def _sync_browser_query_state(self):
        """Only accept Edge search terms when the visual browser is enabled."""
        self.browser_query_entry.configure(
            state="normal" if (self.browser_research_var.get() and not self.running and
                               not self.browser_research_toggle.instate(["disabled"]))
            else "disabled")

    def update_consumption_display(self):
        usage = self.current_token_usage
        if not usage:
            self.consumption_var.set(
                "Consumo desta tarefa: indisponível. Esta versão do Codex CLI não enviou tokens de uso no retorno.")
            return
        currency = {"pt-BR": "BRL", "es": "EUR"}.get(self.language, "USD")
        model = str(self.pending.get("model") or "") if self.pending else ""
        cost = gate.estimate_token_cost(model, usage, currency)
        symbols = {"BRL": "R$", "EUR": "€", "USD": "US$"}
        text = (f"{self.tr('Consumo desta tarefa')} — "
                f"{self.tr('entrada')}: {self._format_integer(usage.get('input', 0))}; "
                f"{self.tr('cache')}: {self._format_integer(usage.get('cached_input', 0))}; "
                f"{self.tr('saída')}: {self._format_integer(usage.get('output', 0))}; "
                f"{self.tr('raciocínio')}: {self._format_integer(usage.get('reasoning', 0))}. ")
        if cost is None:
            text += self.tr("Custo estimado indisponível: modelo ou uso não identificado.")
        else:
            text += f"{self.tr('Custo estimado')}: {symbols[currency]} {self._format_estimated_cost(cost)}."
        self.consumption_var.set(text)

    def _format_estimated_cost(self, amount):
        """Format estimated costs to two decimal places in the active locale."""
        formatted = f"{amount:,.2f}"
        if self.language in {"pt-BR", "es"}:
            return formatted.replace(",", "\0").replace(".", ",").replace("\0", ".")
        return formatted

    def _format_integer(self, value):
        formatted = f"{int(value):,}"
        return formatted.replace(",", ".") if self.language in {"pt-BR", "es"} else formatted

    def _format_storage_size(self, size):
        formatted = gate.format_storage_size(size)
        return formatted.replace(".", ",") if self.language in {"pt-BR", "es"} else formatted

    def _format_usage_date(self, value):
        return value.strftime("%d/%m/%Y") if self.language in {"pt-BR", "es"} else value.isoformat()

    def _format_usage_month(self, value):
        year, month = value.split("-")
        return f"{month}/{year}" if self.language in {"pt-BR", "es"} else value

    def _parse_usage_date(self, value):
        value = value.strip()
        if self.language in {"pt-BR", "es"}:
            return datetime.strptime(value, "%d/%m/%Y").date()
        return date.fromisoformat(value)

    def _format_record_datetime(self, value):
        try:
            when = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
            if when.tzinfo:
                when = when.astimezone()
            return when.strftime("%d/%m/%Y %H:%M:%S") if self.language in {
                "pt-BR", "es"} else when.strftime("%Y-%m-%d %H:%M:%S")
        except (TypeError, ValueError, OSError):
            return str(value or "")

    def on_model_selection_changed(self, _event=None):
        selected = model_key(self.model_var.get())
        if selected not in gate.MODELS:
            return
        levels = gate.supported_efforts(selected) or gate.supported_efforts("sol")
        self.effort_box.configure(values=[self.tr(gate.EFFORT_LABELS[k]) for k in levels])
        if gate_i18n.source_text(self.effort_var.get(), self.language) not in [gate.EFFORT_LABELS[k] for k in levels]:
            self.effort_var.set(self.tr(gate.EFFORT_LABELS['medium' if 'medium' in levels else levels[0]]))
        self.sync_decision_settings()
        self.update_consumption_display()


    def on_legacy_model_selection_changed(self, _event=None):
        selected = model_key(self.legacy_model_var.get())
        if selected in gate.MODELS:
            self.model_var.set(model_label(selected))
            self.on_model_selection_changed()


    def selected_record(self):
        selection = self.history.selection()
        return self.record_items.get(selection[0]) if selection else None

    def selected_record_content(self, record):
        try:
            return Path(record["record_file"]).read_text(encoding="utf-8")
        except (OSError, KeyError) as exc:
            return f"Não foi possível abrir o registro selecionado: {exc}"

    def show_selected_record(self, _event=None):
        record = self.selected_record()
        if not record:
            self.continue_record_button.configure(state="disabled")
            return
        content = self.selected_record_content(record)
        self.record_detail.configure(state="normal")
        self.record_detail.delete("1.0", tk.END)
        self.record_detail.insert(tk.END, content)
        self.record_detail.see("1.0")
        self.record_detail.configure(state="disabled")
        self.show_selected_record_artifacts(record)
        self.continue_record_button.configure(
            state="normal" if self.record_can_continue(record) else "disabled")

    def record_can_continue(self, record):
        """Return whether a stored record has enough safe state to resume."""
        if gate.cli_rejected_model(str(record.get("execution_output") or "")):
            return False
        try:
            session_id = str(record.get("session_id") or "").strip()
            workspace = Path(str(record.get("project_folder") or "")).expanduser().resolve()
            model, effort = gate.record_model_settings(record)
            if not session_id and (record.get('imported_from_package') or record.get('restored_from_backup')):
                gate.build_codex_exec_command(gate.MODELS[model], effort)
            else:
                gate.build_codex_resume_command(session_id, gate.MODELS[model], effort)
        except (OSError, ValueError, KeyError):
            return False
        return (workspace.is_dir() and
                (not gate.is_portable_mode() or gate._path_is_within(
                    workspace, gate.projects_dir())))

    def continue_selected_record_conversation(self):
        """Open a new conversational turn in a completed Codex task."""
        if self.running or self.selecting_skills or self.busy_operation:
            return messagebox.showinfo(
                "Continuar conversa", "Aguarde a atividade atual terminar.")
        if self.pending_question:
            self.show_continuation_window()
            return messagebox.showinfo(
                "Continuação pendente",
                "Responda primeiro à pergunta que já está pendente.")
        record = self.selected_record()
        if not record:
            return messagebox.showinfo(
                "Continuar conversa", "Selecione uma tarefa anterior.")
        if gate.cli_rejected_model(str(record.get("execution_output") or "")):
            return messagebox.showinfo(
                "Falha anterior do Codex CLI",
                "Esta tarefa terminou antes de receber uma resposta. Atualize o Codex CLI e analise a pergunta novamente.")
        new_session = bool(record.get("imported_from_package") or record.get("restored_from_backup")) and not record.get("session_id")
        if not str(record.get("session_id") or "").strip() and not new_session:
            return messagebox.showinfo(
                "Conversa indisponível",
                "Este registro foi criado antes de o Gate preservar sessões concluídas. "
                "As próximas tarefas poderão ser retomadas por este botão.")
        try:
            workspace = Path(str(record.get("project_folder") or "")).expanduser().resolve()
            if not workspace.is_dir():
                raise OSError("A pasta desta tarefa não está mais disponível.")
            if gate.is_portable_mode() and not gate._path_is_within(
                    workspace, gate.projects_dir()):
                raise OSError("A tarefa está fora do pendrive e não pode ser retomada nesta edição.")
            model, effort = gate.record_model_settings(record)
            if new_session:
                gate.build_codex_exec_command(gate.MODELS[model], effort)
            else:
                gate.build_codex_resume_command(str(record['session_id']), gate.MODELS[model], effort)
            record_path = Path(str(record.get("record_file") or "")).resolve()
            if not record_path.is_file():
                raise OSError("O registro desta tarefa não está mais disponível.")
        except (OSError, ValueError, KeyError) as exc:
            return messagebox.showerror("Continuar conversa", str(exc))

        conversation = gate.normalize_conversation_turns(
            record.get("conversation"))
        output = str(record.get("execution_output") or "").strip()
        if not conversation:
            conversation = [{
                "role": "user", "text": str(record.get("task") or "Tarefa anterior"),
                "at": str(record.get("started_at") or ""),
            }]
            if output:
                conversation.append({
                    "role": "assistant", "text": output,
                    "at": str(record.get("finished_at") or ""),
                })
        context = next((turn["text"] for turn in reversed(conversation)
                        if turn.get("role") == "assistant"), output)
        self.run_id = str(record.get("id") or uuid.uuid4().hex)
        self.record_note_path = record_path
        self.conversation_record_path = record_path
        self.conversation_turns = conversation
        self.sent_continuation_message = ""
        self.current_followup_request = ""
        self.continuation_mode = "conversation"
        self.current_session_id = str(record.get("session_id") or "").strip() or None
        self.pending_question = context or "A tarefa foi concluída. Escreva como deseja continuar."
        self.last_continuation_answer = ""
        self.pending = {
            "new_session": new_session,
            "id": self.run_id,
            "task": str(record.get("task") or "Tarefa anterior"),
            "project_folder": str(workspace),
            "model": model,
            "effort": effort,
            "policy": str(record.get("policy_key") or "equilibrada"),
            "skills": list(record.get("skills") or []),
            "skill_fingerprints": list(record.get("skill_fingerprints") or []),
            "staged_attachments": list(record.get("attachments") or []),
            "existing_artifacts": list(record.get("artifacts") or []),
            "existing_duration": float(record.get("duration_seconds") or 0),
            "turn_metrics": list(record.get("turn_metrics") or (
                [{"duration_seconds": record.get("duration_seconds"),
                  "token_usage": record.get("token_usage"), "legacy": True}]
                if record.get("token_usage") else [])),
            "original_started_at": str(record.get("started_at") or ""),
            "quality": str(record.get("quality") or "Não avaliado"),
            "browser_research": bool(record.get("browser_research")),
            "browser_query": str(record.get("browser_query") or ""),
            "live_web_search": bool(record.get("live_web_search")) or
                bool(record.get("browser_research")) or
                gate.needs_live_web_search(str(record.get("task") or ""), [
                    {"name": name} for name in record.get("skills", [])]),
        }
        self.cwd = workspace
        self.projects_root = workspace.parent
        self.path_var.set(str(self.projects_root))
        self.task.delete("1.0", tk.END)
        self.task.insert("1.0", self.pending["task"])
        self.status.set("Tarefa importada: será criada uma nova sessão com o histórico e os arquivos restaurados." if new_session else "Tarefa reaberta para conversa na mesma sessão.")
        self.simple_progress_var.set(
            "Escreva um ajuste, uma revisão ou o próximo passo para esta tarefa.")
        self.show_continuation_window()

    def show_selected_record_artifacts(self, record):
        """List the persisted outputs for one prior task without opening them."""
        self.record_artifact_items = []
        self.record_artifact_list.delete(0, tk.END)
        task = " ".join(str(record.get("task", "")).split()) or "Tarefa sem descrição"
        when = self._format_record_datetime(record.get("finished_at", "")).strip()
        self.files_context_var.set(
            f"Tarefa selecionada: {task}" + (f"\nRegistro: {when}" if when else ""))
        for value in record.get("artifacts", []):
            if not isinstance(value, str) or not value.strip():
                continue
            path = Path(value).expanduser()
            self.record_artifact_items.append(path)
            suffix = "" if path.is_file() else " — arquivo não localizado"
            self.record_artifact_list.insert(tk.END, path.name + suffix)
        if not self.record_artifact_items:
            self.record_artifact_list.insert(
                tk.END, "Nenhum arquivo registrado para esta tarefa.")

    def show_history_tab(self):
        self.main_notebook.select(self.history_tab)

    def open_selected_record_task_folder(self):
        record = self.selected_record()
        if not record:
            return messagebox.showinfo(
                "Tarefas anteriores", "Selecione uma tarefa para abrir sua pasta.")
        try:
            folder = Path(str(record.get("project_folder", ""))).expanduser()
            if not folder.is_dir():
                raise OSError("A pasta desta tarefa não está mais disponível.")
            os.startfile(folder)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Pasta da tarefa", str(exc))

    def open_selected_record_artifact(self):
        selection = self.record_artifact_list.curselection()
        if not self.record_artifact_items or not selection:
            return messagebox.showinfo(
                "Arquivos anteriores", "Selecione um arquivo da tarefa para abri-lo.")
        path = self.record_artifact_items[selection[0]]
        try:
            if not path.is_file():
                raise OSError("O arquivo registrado não está mais disponível.")
            os.startfile(path)
        except OSError as exc:
            messagebox.showerror("Arquivo da tarefa", str(exc))

    def open_selected_record(self):
        record = self.selected_record()
        if not record:
            return messagebox.showinfo("Registros", "Selecione um registro para abri-lo.")
        try:
            subprocess.Popen(["notepad.exe", record["record_file"]])
        except (OSError, KeyError) as exc:
            messagebox.showerror(
                "Registros", f"Não foi possível abrir o registro: {exc}")

    def toggle_unqualified_records(self):
        self.show_only_unqualified = not self.show_only_unqualified
        self.load_history()

    def qualify_selected_record(self):
        record = self.selected_record()
        if not record:
            return messagebox.showinfo(
                "Qualificar registro", "Selecione um registro para avaliar o resultado.")
        dialog = tk.Toplevel(self)
        dialog.title("Qualificar resultado")
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        ttk.Label(dialog, text="Como você avalia o resultado desta tarefa?", padding=(16, 14, 16, 6)).pack(
            anchor="w")
        quality = tk.StringVar(value=record.get("quality", "Não avaliado"))
        selector = ttk.Combobox(
            dialog, textvariable=quality, state="readonly", width=28,
            values=["Aprovado", "Precisou de ajustes", "Falhou"])
        selector.pack(fill="x", padx=16, pady=(0, 12))
        if quality.get() == "Não avaliado":
            quality.set("Aprovado")
        choice: list[str] = []

        def save():
            choice.append(quality.get())
            dialog.destroy()

        controls = ttk.Frame(dialog, padding=(16, 0, 16, 14))
        controls.pack(fill="x")
        ttk.Button(controls, text="Salvar avaliação", command=save).pack(side="left")
        ttk.Button(controls, text="Cancelar", command=dialog.destroy).pack(side="right")
        self.wait_window(dialog)
        if not choice:
            return
        record_path = Path(record.get("record_file", ""))
        if not record_path.is_file():
            return messagebox.showerror(
                "Qualificar registro", "Não foi possível localizar o arquivo de registro selecionado.")
        self.start_job('Qualificar registro',lambda: gate.update_execution_record(record_path,
            quality=choice[0],evaluated_at=datetime.now().isoformat(timespec='seconds')),
            lambda _: self.load_history(),exclusive=True)

    @staticmethod
    def _write_record_pdf(destination, content):
        """Create a Unicode-safe, readable PDF export from one Markdown record."""
        try:
            from reportlab.lib.pagesizes import A4
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            from reportlab.pdfgen import canvas
        except ImportError as exc:
            raise RuntimeError(
                "A exportação para PDF requer reportlab. Execute Instalar_Validacao_Documentos.bat e tente novamente.") from exc
        font_candidates = [
            Path(os.environ.get("WINDIR", r"C:\\Windows")) /
            "Fonts" / "segoeui.ttf",
            Path(os.environ.get("WINDIR", r"C:\\Windows")) /
            "Fonts" / "arial.ttf",
            Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        ]
        font_path = next(
            (path for path in font_candidates if path.is_file()), None)
        if not font_path:
            raise RuntimeError(
                "Não foi encontrada uma fonte Unicode compatível para gerar o PDF. Instale Segoe UI, Arial ou DejaVu Sans.")
        font_name = "CodexGateUnicode"
        if font_name not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(font_name, str(font_path)))
        page_width, page_height = A4
        margin, footer, size, leading = 42, 28, 9.5, 13
        available_width = page_width - margin * 2
        document = canvas.Canvas(str(destination), pagesize=A4)
        document.setTitle("Registro - Codex Model Gate")

        def wrap_line(value, text_size):
            if not value:
                return [""]
            pieces, current = [], ""
            for word in value.split(" "):
                proposed = word if not current else current + " " + word
                if pdfmetrics.stringWidth(proposed, font_name, text_size) <= available_width:
                    current = proposed
                    continue
                if current:
                    pieces.append(current)
                current = word
                while pdfmetrics.stringWidth(current, font_name, text_size) > available_width:
                    cut = max(1, len(current) - 1)
                    while cut > 1 and pdfmetrics.stringWidth(current[:cut], font_name, text_size) > available_width:
                        cut -= 1
                    pieces.append(current[:cut])
                    current = current[cut:]
            if current or not pieces:
                pieces.append(current)
            return pieces

        page_number, y = 1, page_height - margin
        document.setFont(font_name, size)
        for source_line in content.splitlines():
            value = source_line.replace("**", "").replace("`", "")
            if value.startswith("## "):
                value, line_size = value[3:], 12
            elif value.startswith("# "):
                value, line_size = value[2:], 14
            else:
                line_size = size
            line_leading = max(leading, line_size + 4)
            for line in wrap_line(value, line_size):
                if y - line_leading < margin + footer:
                    document.setFont(font_name, 8)
                    document.drawRightString(
                        page_width - margin, margin / 2, f"Página {page_number}")
                    document.showPage()
                    page_number += 1
                    y = page_height - margin
                document.setFont(font_name, line_size)
                document.drawString(margin, y, line)
                y -= line_leading
        document.setFont(font_name, 8)
        document.drawRightString(
            page_width - margin, margin / 2, f"Página {page_number}")
        document.save()

    def export_selected_record(self):
        if self.running or self.busy_operation:
            return
        record = self.selected_record()
        if not record:
            return messagebox.showinfo('Exportar registro','Selecione um registro.')
        destination = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Texto','*.txt'),('PDF','*.pdf')])
        if not destination:
            return
        path = Path(destination)
        def export():
            content = Path(record['record_file']).read_text(encoding='utf-8')
            if path.suffix.lower() == '.pdf':
                from gate_storage import atomic_archive
                with atomic_archive(path) as temporary:
                    self._write_record_pdf(temporary, content)
            else:
                atomic_write_text(path, content)
            return path
        self.start_job('Exportar registro',export,lambda path:self.status.set(f'Registro exportado: {path}'),exclusive=True)


    def export_selected_task_package(self):
        if self.running or self.busy_operation:
            return
        record = self.selected_record()
        if not record:
            return messagebox.showinfo('Exportar tarefa', 'Selecione uma tarefa anterior.')
        destination = filedialog.asksaveasfilename(title='Exportar tarefa', defaultextension='.gate',
            filetypes=[('Pacote Codex Model Gate','*.gate')])
        if destination:
            self.start_job('Exportar tarefa', lambda: gate.export_task_package(record, Path(destination)),
                lambda path: self.status.set(f'Pacote exportado com anexos e resultados: {path.name}'), exclusive=True)


    def import_task_package(self):
        if self.running or self.busy_operation:
            return
        source = filedialog.askopenfilename(title='Importar pacote',filetypes=[('Pacote Codex Model Gate','*.gate')])
        if not source:
            return
        root = gate.validate_projects_root(self.path_var.get())
        def present(record):
            self.load_history()
            self.task.delete('1.0', tk.END)
            self.task.insert('1.0', str(record.get('task') or ''))
            self.pending = None
            self.status.set('Pacote importado. Selecione o registro e use Continuar conversa para restaurar o contexto.')
        self.start_job('Importar pacote',lambda: gate.import_task_package(Path(source),root),present,exclusive=True)


    def record_outcome(self):
        if self.running or self.busy_operation:
            return
        if not self.record_note_path:
            return messagebox.showinfo('Resultado', 'Execute uma tarefa antes de registrar a avaliação.')
        path, quality = self.record_note_path, self.quality_var.get()
        def present(_):
            self.load_history()
            self.status.set(f'Resultado registrado: {quality}.')
        self.start_job('Registrar resultado', lambda: gate.update_execution_record(path,
            quality=quality, evaluated_at=datetime.now().isoformat(timespec='seconds')), present, exclusive=True)


    def refresh_codex_cli_status(self):
        self.cli_status_var.set('Verificando versão do Codex CLI...')
        def inspect():
            executable = gate.resolve_codex_executable()
            return executable, gate.codex_cli_version(executable)
        self.start_job('Codex CLI', inspect, self.apply_cli_status)

    @staticmethod
    def executable_signature(executable):
        try:
            info = Path(executable).stat()
            return info.st_size, info.st_mtime_ns
        except (OSError, TypeError):
            return None

    def apply_cli_status(self, result):
        if self.running:
            self._deferred_cli_status = result
            return
        self.cli_executable, self.cli_version = result
        self.cli_signature = self.executable_signature(self.cli_executable)
        if not self.cli_executable:
            self.cli_status_var.set('Codex CLI não encontrado. Use Download / atualização oficial para instalar e autenticar.')
            self.install_cli_button.configure(state='normal')
            return
        version = '.'.join(map(str, self.cli_version)) if self.cli_version else 'versão não identificada'
        warning = gate.cli_model_compatibility_message(self.cli_executable, 'sol', self.cli_version) if self.cli_version else None
        self.cli_status_var.set(warning or f'Codex CLI {version}. Sol 6.1 requer 0.159.1+. Acesso depende da conta e do workspace.')
        self.install_cli_button.configure(text=self.tr('Atualizar Codex CLI...'), state='normal')
        home = gate.app_data_dir() / 'codex-cli' if gate.is_portable_mode() else Path(os.environ.get('CODEX_HOME', str(Path.home()/'.codex')))
        catalog = local_catalog(home, self.cli_version)
        from gate_models import MODEL_EFFORTS, MODEL_IDS, BASE_MODEL_IDS, BASE_MODEL_EFFORTS
        MODEL_IDS.clear(); MODEL_IDS.update(BASE_MODEL_IDS)
        MODEL_EFFORTS.clear(); MODEL_EFFORTS.update(BASE_MODEL_EFFORTS)
        for item in catalog:
            key = next((k for k, v in gate.MODELS.items() if v == item['id']), item['id'])
            gate.MODELS[key] = item['id']; MODEL_IDS[key] = item['id']; MODEL_EFFORTS[key] = item['efforts']
        extra = [k for k in gate.MODELS if k not in gate.PRIMARY_MODELS]
        self.legacy_model_box.configure(values=[self.tr('Selecionar...')] + [model_label(k) for k in extra])
        self.on_model_selection_changed()


    def open_codex_install_guide(self):
        try:
            webbrowser.open(CODEX_INSTALL_GUIDE_URL)
        except OSError as exc:
            messagebox.showerror(
                "Instruções do Codex CLI", f"Não foi possível abrir as instruções oficiais: {exc}")

    def install_codex_cli(self):
        self.open_codex_install_guide()


    def choose_dir(self):
        chosen = filedialog.askdirectory(initialdir=self.path_var.get())
        if chosen:
            selected = Path(chosen).expanduser().resolve()
            if gate.is_portable_mode() and not gate._path_is_within(
                    selected, gate.projects_dir()):
                return messagebox.showwarning(
                    "Projetos da versão portátil",
                    "Na versão portátil, os projetos precisam ficar em "
                    "CodexModelGate-Dados\\projetos no próprio pendrive.")
            self.path_var.set(str(selected))
            self.refresh_skills()

    def open_gate_data_folder(self):
        try:
            os.startfile(gate.app_data_dir())
        except OSError as exc:
            messagebox.showerror(
                "Dados do Gate", f"Não foi possível abrir a pasta de dados: {exc}")

    def backup_gate_data(self):
        if self.running or self.busy_operation:
            return
        destination = filedialog.asksaveasfilename(title='Salvar backup',defaultextension='.zip',
            initialfile=f"backup-codex-model-gate-{datetime.now():%Y%m%d-%H%M}.zip",
            filetypes=[('Arquivo ZIP','*.zip')])
        if destination:
            self.start_job('Criar backup',lambda: gate.create_data_backup(Path(destination)),
                lambda path: self.status.set(f'Backup concluído, incluindo pastas externas de tarefas: {path}'),exclusive=True)


    def restore_gate_data(self):
        if self.running or self.busy_operation:
            return
        source = filedialog.askopenfilename(title='Selecionar backup',filetypes=[('Arquivo ZIP','*.zip')])
        if source:
            self.start_job('Verificar backup',lambda: gate.inspect_data_backup(Path(source)),
                lambda preview: self.confirm_backup_restore(Path(source),preview),exclusive=True)

    def confirm_backup_restore(self, source, preview):
        counts = preview["counts"]
        preview_text = (
            f"Prévia do backup:\n"
            f"• {self._format_integer(preview['files'])} "
            f"{self.tr('arquivo' if preview['files'] == 1 else 'arquivos')}, "
            f"{self._format_storage_size(int(preview['bytes']))}\n"
            f"• Projetos: {counts['projetos']} | Skills: {counts['skills']}\n"
            f"• Registros: {counts['registro']} | Configurações: {counts['configuracoes']}\n\n")
        choice = messagebox.askyesnocancel(
            "Como restaurar o backup?",
            preview_text +
            "Sim: substituir arquivos atuais que tenham o mesmo nome.\n\n"
            "Não: manter os arquivos atuais e adicionar os restaurados com um nome diferente.\n\n"
            "Cancelar: não alterar nada.\n\n"
            "Os arquivos que não fazem parte do backup nunca são removidos.",
        )
        if choice is None:
            return
        def present(result):
            restored = int(result["restored"])
            overwritten = int(result["overwritten"])
            skipped = int(result["skipped"])
            saved_library = gate.saved_skill_library()
            self.skill_library_var.set(str(saved_library) if saved_library else "")
            self.refresh_skills()
            self.load_history()
            summary = f"{restored} arquivo(s) restaurado(s)"
            if overwritten:
                summary += f"; {overwritten} substituído(s)"
            if skipped:
                summary += f"; {skipped} configuração(ões) mantida(s)"
            self.status.set("Backup restaurado. " + summary + ".")
            messagebox.showinfo(
                "Backup restaurado",
                summary + "\n\nSe a restauração trouxe configurações de outro computador, feche e abra o Gate novamente para aplicá-las por completo.")
        self.start_job('Restaurar backup',lambda: gate.restore_data_backup(source,overwrite=choice),present,exclusive=True)


    def open_project_folder(self):
        folder = Path(self.path_var.get()).expanduser()
        if not folder.is_dir():
            return messagebox.showwarning("Pasta", "Escolha uma pasta de projeto válida.")
        os.startfile(folder)

    def choose_skill_library(self):
        initial = self.skill_library_var.get() or str(self.cwd)
        chosen = filedialog.askdirectory(initialdir=initial)
        if not chosen:
            return
        library = Path(chosen).expanduser().resolve()
        if gate.is_portable_mode() and not gate._path_is_within(
                library, gate.app_data_dir()):
            return messagebox.showwarning(
                "Skills da versão portátil",
                "Na versão portátil, vincule apenas uma biblioteca dentro de "
                "CodexModelGate-Dados no pendrive. Para trazer uma skill de "
                "outro local, use “Instalar skill” para copiá-la.")
        gate.save_skill_library(library)
        self.skill_library_var.set(str(library))
        self.refresh_skills()
        if not self.skills:
            messagebox.showwarning(
                "Biblioteca de skills", "A pasta foi vinculada, mas não encontrei subpastas com o arquivo SKILL.md.")

    def open_skill_library(self):
        value = self.skill_library_var.get().strip()
        library = Path(value).expanduser() if value else None
        if not library or not library.is_dir():
            return messagebox.showwarning("Biblioteca de skills", "Vincule uma pasta de skills válida primeiro.")
        os.startfile(library)

    def refresh_skills(self):
        if self.running:
            return
        try:
            root = gate.validate_projects_root(self.path_var.get())
            value = self.skill_library_var.get().strip()
            library = Path(value).expanduser() if value else None
            if gate.is_portable_mode() and library and not gate._path_is_within(library, gate.app_data_dir()):
                library = gate.managed_skills_dir()
                self.skill_library_var.set(str(library))
            self.projects_root = root
            if not self.pending or not self.pending.get("project_folder"):
                self.cwd = root
        except (ValueError, OSError) as exc:
            return messagebox.showwarning('Biblioteca', str(exc))
        def scan():
            root.mkdir(parents=True, exist_ok=True)
            return gate.refresh_skill_index(root, [library] if library and library.is_dir() else None)
        def present(result):
            self.skills, stats = result
            self.render_skill_list()
            self.skill_library_status.set(f"Memória pronta: {stats['total']} skills; {stats['updated']} atualizadas; {stats['reused']} reutilizadas.")
        self.start_job('Atualizar skills', scan, present, exclusive=True)


    def render_skill_list(self, selected_names=None):
        """Show the filtered catalog and keep Listbox indexes tied to its items."""
        self.filtered_skill_items = gate.filter_skills_by_name(
            self.skills, self.skill_search_var.get())
        self.skill_list.delete(0, tk.END)
        selected_names = set(selected_names or ())
        for index, skill in enumerate(self.filtered_skill_items):
            self.skill_list.insert(tk.END, skill["name"])
            if skill["name"] in selected_names:
                self.skill_list.selection_set(index)
        query = self.skill_search_var.get().strip()
        if query:
            self.skill_search_status.set(
                f"{len(self.filtered_skill_items)} de {len(self.skills)} skill(s)")
        else:
            self.skill_search_status.set(f"{len(self.skills)} skill(s) disponíveis")

    def on_skill_search_changed(self, *_):
        if hasattr(self, "skill_list"):
            self.render_skill_list()

    def clear_skill_search(self):
        self.skill_search_var.set("")

    def update_active_skills(self, skills, automatic):
        self.active_skill_items = list(skills)
        self.active_skill_list.delete(0, tk.END)
        if not skills:
            self.active_skill_list.insert(
                tk.END, "Nenhuma skill será utilizada nesta tarefa.")
            return
        for skill in skills:
            manually_added = skill.get("_added_to_task_manually", False)
            origin = ("adicionada por você" if manually_added else
                      "automática" if automatic else "manual")
            detail = skill.get("match_reasons") if automatic and not manually_added else None
            suffix = f" — {detail}" if detail else ""
            self.active_skill_list.insert(
                tk.END, f"{skill['name']} — seleção {origin}{suffix}")

    def sync_active_skills_to_pending_task(self):
        """Update only the in-memory selection for the task awaiting approval."""
        if not self.pending:
            return
        self.pending["selected_skills"] = list(self.active_skill_items)
        self.pending["skills"] = [skill["name"] for skill in self.active_skill_items]
        self.pending["skill_fingerprints"] = []
        self.decision_skills_card_var.set(
            str(len(self.active_skill_items)) if self.active_skill_items else "Nenhuma")
        names = ", ".join(self.pending["skills"]) or "nenhuma"
        self.status.set(f"Skills da tarefa atual: {names}.")

    def add_selected_skill_to_task(self):
        if self.running:
            return
        if not self.pending:
            return messagebox.showinfo(
                "Adicionar skill", "Analise a tarefa antes de adicionar uma skill.")
        selection = self.skill_list.curselection()
        if not selection:
            return messagebox.showinfo(
                "Adicionar skill", "Selecione uma ou mais skills na lista principal.")
        active_paths = {str(Path(skill["path"]).expanduser())
                        for skill in self.active_skill_items}
        additions = []
        for index in selection:
            skill = dict(self.filtered_skill_items[index])
            path = str(Path(skill["path"]).expanduser())
            if path in active_paths:
                continue
            skill["_added_to_task_manually"] = True
            additions.append(skill)
            active_paths.add(path)
        if not additions:
            return messagebox.showinfo(
                "Adicionar skill", "As skills selecionadas já fazem parte desta tarefa.")
        self.update_active_skills(self.active_skill_items + additions, False)
        self.sync_active_skills_to_pending_task()

    def remove_selected_skill_from_task(self):
        if self.running:
            return
        if not self.pending or not self.active_skill_items:
            return messagebox.showinfo(
                "Remover skill", "Não há uma skill adicionada à tarefa atual.")
        selection = self.active_skill_list.curselection()
        if not selection:
            return messagebox.showinfo(
                "Remover skill", "Selecione uma skill da tarefa para removê-la.")
        removed = self.active_skill_items[selection[0]]
        remaining = [skill for index, skill in enumerate(self.active_skill_items)
                     if index != selection[0]]
        self.update_active_skills(remaining, False)
        self.sync_active_skills_to_pending_task()
        self.status.set(
            f"A skill “{removed['name']}” foi removida apenas desta tarefa; "
            "ela continua disponível na biblioteca.")

    def open_active_skill(self):
        selection = self.active_skill_list.curselection()
        if not self.active_skill_items:
            return messagebox.showinfo("Skills", "Analise uma tarefa primeiro para ver as skills que serão usadas.")
        if not selection:
            return messagebox.showinfo("Skills", "Selecione uma skill da lista para conferir suas instruções.")
        skill = self.active_skill_items[selection[0]]
        try:
            subprocess.Popen(["notepad.exe", skill["path"]])
        except OSError as exc:
            messagebox.showerror("Não foi possível abrir a skill", str(exc))

    def refresh_portable_storage_status(self):
        if not gate.is_portable_mode():
            return
        def present(estimate):
            self.portable_storage_var.set('Espaço livre nesta unidade: ' + self._format_storage_size(estimate['free'])
                + '. Reserva mínima: ' + self._format_storage_size(estimate['required_free'])
                + '. O Gate usa ' + self._format_storage_size(estimate['app_size'] + estimate['data_size']) + '.')
        self.start_job('Armazenamento portátil',gate.portable_storage_estimate,present)


    def has_portable_capacity(self, additional_bytes=0, purpose="continuar"):
        """Block a portable write that cannot fit its conservative reserve."""
        if not gate.is_portable_mode():
            return True
        try:
            estimate = gate.portable_storage_estimate(additional_bytes, scan_sizes=False)
        except OSError as exc:
            messagebox.showerror("Armazenamento portátil",
                                 f"Não foi possível consultar o espaço do pendrive: {exc}")
            return False
        self.portable_storage_var.set(
            "Antes de " + purpose + ": espaço livre de " +
            self._format_storage_size(estimate["free"]) +
            "; arquivos adicionais previstos: " +
            self._format_storage_size(estimate["additional_size"]) +
            "; mínimo necessário: " +
            self._format_storage_size(estimate["required_free"]) +
            " (inclui reserva de " +
            self._format_storage_size(gate.PORTABLE_MIN_FREE_BYTES) + ").")
        if estimate["sufficient"]:
            return True
        messagebox.showerror(
            "Espaço insuficiente no pendrive",
            "Não é seguro " + purpose + " porque a unidade tem " +
            self._format_storage_size(estimate["free"]) + " livres e o Gate exige ao menos " +
            self._format_storage_size(estimate["required_free"]) +
            " livres, incluindo a reserva para os arquivos da tarefa. Libere espaço e tente novamente.")
        return False

    def install_active_skill(self):
        selection = self.active_skill_list.curselection()
        if not self.active_skill_items:
            return messagebox.showinfo("Skills", "Analise uma tarefa e selecione uma skill para instalá-la.")
        if not selection:
            return messagebox.showinfo("Skills", "Selecione uma skill para instalar.")
        skill = self.active_skill_items[selection[0]]
        source = Path(skill["path"])
        try:
            source_size = gate.directory_size(source.parent)
        except OSError:
            source_size = 0
        if not self.has_portable_capacity(source_size, "instalar esta skill"):
            return
        if not messagebox.askyesno(
                "Instalar skill",
                f"Copiar a skill “{skill['name']}” para a biblioteca local do Gate?\n\n"
                f"Tamanho previsto para a cópia: {self._format_storage_size(source_size)}.\n\n"
                "Uma versão já instalada não será substituída."):
            return
        try:
            installed = gate.install_skill(source)
            self.refresh_skills()
            location = "no pendrive" if gate.is_portable_mode() else "na biblioteca local"
            self.status.set(f"Skill instalada {location}: {installed}")
            self.refresh_portable_storage_status()
            messagebox.showinfo("Skill instalada", f"A skill foi instalada em:\n{installed}")
        except (OSError, ValueError) as exc:
            messagebox.showerror("Não foi possível instalar a skill", str(exc))

    def refresh_attachments(self):
        self.attachment_list.delete(0, tk.END)
        for path in self.attachments:
            self.attachment_list.insert(tk.END, str(path))
        self.update_action_buttons()

    def add_attachments(self):
        filetypes = [
            ("Documentos e imagens",
             "*.docx *.pdf *.png *.jpg *.jpeg *.webp *.gif *.bmp *.tif *.tiff"),
            ("Documentos Word", "*.docx"), ("Documentos PDF", "*.pdf"),
            ("Imagens", "*.png *.jpg *.jpeg *.webp *.gif *.bmp *.tif *.tiff"), ("Todos os arquivos", "*.*"),
        ]
        chosen = filedialog.askopenfilenames(
            title="Selecione arquivos para análise", filetypes=filetypes)
        known = {str(path).lower() for path in self.attachments}
        for value in chosen:
            path = Path(value).expanduser().resolve()
            if path.is_file() and str(path).lower() not in known:
                self.attachments.append(path)
                known.add(str(path).lower())
        self.refresh_attachments()

    def remove_attachment(self):
        selection = self.attachment_list.curselection()
        if not selection:
            return messagebox.showinfo("Anexos", "Selecione um arquivo da lista para remover.")
        del self.attachments[selection[0]]
        self.refresh_attachments()

    def open_attachment(self):
        selection = self.attachment_list.curselection()
        if not selection:
            return messagebox.showinfo("Anexos", "Selecione um arquivo da lista para abrir.")
        try:
            os.startfile(self.attachments[selection[0]])
        except OSError as exc:
            messagebox.showerror(
                "Anexos", f"Não foi possível abrir o arquivo: {exc}")

    def open_records_folder(self):
        try:
            os.startfile(gate.records_dir())
        except OSError as exc:
            messagebox.showerror(
                "Registro", f"Não foi possível abrir a pasta de registros: {exc}")

    def generate_records_report(self):
        try:
            report = gate.generate_records_report()
            subprocess.Popen(["notepad.exe", str(report)])
            self.status.set(f"Relatório gerado em: {report}")
        except OSError as exc:
            messagebox.showerror(
                "Relatório", f"Não foi possível gerar o relatório: {exc}")

    def restore_pending_continuation(self):
        """Restore a valid pending answer or conversational turn after restart."""
        state = gate.find_latest_pending_continuation(
            self.projects_root,
            allow_indexed_external=not gate.is_portable_mode())
        if not state:
            return
        try:
            workspace = Path(str(state["project_folder"])).expanduser().resolve()
            session_id = str(state["session_id"]).strip()
            question = str(state["question"]).strip()
        except (KeyError, OSError, ValueError):
            return
        if (not workspace.is_dir() or not session_id or not question or
                (gate.is_portable_mode() and not gate._path_is_within(
                    workspace, gate.projects_dir()))):
            return
        model = str(state.get("model", "terra")).lower()
        if model == "sol" and not state.get("model_id"):
            model = "sol6"
        effort = str(state.get("effort", "medium")).lower()
        self.projects_root = workspace.parent
        self.path_var.set(str(self.projects_root))
        self.cwd = workspace
        self.current_session_id = session_id
        self.pending_question = question
        self.continuation_mode = str(state.get("mode") or "question")
        if self.continuation_mode not in {"question", "conversation"}:
            self.continuation_mode = "question"
        self.last_continuation_answer = str(state.get("draft_answer") or "")
        saved_record = Path(str(state.get("record_file") or "")).expanduser()
        self.conversation_record_path = saved_record if saved_record.is_file() else None
        self.record_note_path = self.conversation_record_path
        self.conversation_turns = gate.normalize_conversation_turns(
            state.get("conversation"))
        self.current_followup_request = str(
            state.get("current_followup_request") or "")
        self.continuation_in_flight = False
        self.run_id = str(state.get("id") or uuid.uuid4().hex)
        self.pending = {
            "id": self.run_id,
            "task": str(state.get("task") or "Tarefa em continuação"),
            "project_folder": str(workspace),
            "model": model if model in gate.MODELS else "sol",
            "effort": effort if effort in gate.EFFORT_LABELS else "medium",
            "policy": str(state.get("policy") or "equilibrada"),
            "skills": list(state.get("skills") or []),
            "skill_fingerprints": list(state.get("skill_fingerprints") or []),
            "staged_attachments": list(state.get("staged_attachments") or []),
            "existing_artifacts": list(state.get("existing_artifacts") or []),
            "existing_duration": float(state.get("existing_duration") or 0),
            "turn_metrics": list(state.get("turn_metrics") or []),
            "original_started_at": str(state.get("original_started_at") or ""),
            "quality": str(state.get("quality") or "Não avaliado"),
            "browser_research": bool(state.get("browser_research")),
            "browser_query": str(state.get("browser_query") or ""),
            "live_web_search": bool(state.get("live_web_search")) or
                bool(state.get("browser_research")) or
                gate.needs_live_web_search(str(state.get("task") or ""), [
                    {"name": name} for name in state.get("skills", [])]),
        }
        self.task.delete("1.0", tk.END)
        self.task.insert("1.0", self.pending["task"])
        self.status.set(
            "Há uma conversa desta tarefa pronta para continuar."
            if self.continuation_mode == "conversation" else
            "Há uma resposta pendente do Codex para esta tarefa.")
        self.simple_progress_var.set(
            "A tarefa será retomada na mesma sessão quando você enviar sua resposta.")
        self.set_controls("normal")
        self.show_continuation_window()

    def pending_workspace(self):
        """Return the immutable workspace recorded for the pending task."""
        if not self.pending:
            raise ValueError("Não há uma tarefa pendente para continuar.")
        workspace = Path(
            str(self.pending.get("project_folder", ""))).expanduser().resolve()
        if not workspace.is_dir():
            raise OSError("A pasta da tarefa não está mais disponível.")
        if gate.is_portable_mode() and not gate._path_is_within(
                workspace, gate.projects_dir()):
            raise OSError(
                "A tarefa pendente está fora do pendrive e não pode ser retomada "
                "pela edição portátil.")
        return workspace

    def continuation_state(self, question):
        """Keep the minimal, serializable data needed after a restart."""
        workspace = self.pending_workspace()
        return {
            "id": self.pending.get("id", self.run_id or uuid.uuid4().hex),
            "session_id": self.current_session_id,
            "question": question,
            "mode": self.continuation_mode,
            "task": self.pending.get("task", ""),
            "project_folder": str(workspace),
            "model": self.pending.get("model", "terra"),
            "model_id": gate.MODELS.get(self.pending.get("model", ""), ""),
            "effort": self.pending.get("effort", "medium"),
            "policy": self.pending.get("policy", "equilibrada"),
            "skills": list(self.pending.get("skills", [])),
            "skill_fingerprints": list(self.pending.get("skill_fingerprints", [])),
            "staged_attachments": list(self.pending.get("staged_attachments", [])),
            "existing_artifacts": list(self.pending.get("existing_artifacts", [])),
            "existing_duration": float(self.pending.get("existing_duration") or 0),
            "turn_metrics": list(self.pending.get("turn_metrics") or []),
            "original_started_at": self.pending.get("original_started_at", ""),
            "quality": self.pending.get("quality", "Não avaliado"),
            "browser_research": bool(self.pending.get("browser_research")),
            "browser_query": str(self.pending.get("browser_query") or ""),
            "live_web_search": bool(self.pending.get("live_web_search")),
            "record_file": str(self.conversation_record_path or ""),
            "conversation": list(self.conversation_turns),
            "current_followup_request": self.current_followup_request,
        }

    def show_continuation_window(self):
        """Display a compact, self-contained continuation window once per question."""
        try:
            self.pending_workspace()
        except (OSError, ValueError):
            return
        if not self.pending_question or not (self.current_session_id or self.pending and self.pending.get("new_session")):
            return
        if self.continuation_window and self.continuation_window.winfo_exists():
            self.continuation_window.deiconify()
            self.continuation_window.lift()
            self.continuation_window.focus_force()
            return
        window = tk.Toplevel(self)
        self.continuation_window = window
        conversational = self.continuation_mode == "conversation"
        window.title(("Conversar nesta tarefa" if conversational else
                      "Continuar tarefa") + " — Codex Model Gate")
        window.geometry("760x570")
        window.minsize(540, 390)
        window.transient(self)
        window.protocol("WM_DELETE_WINDOW", self.close_continuation_window)

        content = ttk.Frame(window, padding=12)
        content.pack(fill="both", expand=True)
        ttk.Label(content, text=(
            "Peça um ajuste, uma revisão ou o próximo passo sem perder o contexto desta tarefa."
            if conversational else
            "O Codex precisa da sua resposta para continuar esta mesma tarefa."),
                  style="Hint.TLabel", wraplength=700).pack(anchor="w", pady=(0, 8))
        ttk.Label(content, text=("Última resposta do Codex:" if conversational else
                                 "Pergunta do Codex:")).pack(anchor="w")
        question_holder = ttk.Frame(content)
        question_holder.pack(fill="both", expand=True, pady=(3, 10))
        question_text = tk.Text(question_holder, height=10, wrap="word", state="normal",
                                font=("Segoe UI", 11), padx=10, pady=9,
                                background="#ffffff", relief="solid", borderwidth=1)
        question_text.tag_configure("heading1", font=("Segoe UI", 14, "bold"))
        question_text.tag_configure("heading2", font=("Segoe UI", 12, "bold"))
        question_text.tag_configure("bold", font=("Segoe UI", 11, "bold"))
        question_text.tag_configure("italic", font=("Segoe UI", 11, "italic"))
        question_text.tag_configure("code", font=("Cascadia Mono", 10), background="#eef1f5")
        question_text.tag_configure("quote", foreground="#4c5f73", lmargin1=14, lmargin2=14)
        question_text.tag_configure("symbol", font=("Cambria Math", 11))
        self.insert_markdown_for_reading(question_text, self.pending_question)
        question_text.configure(state="disabled")
        # The text is inserted only when a new question arrives. No timer or
        # log callback rewrites it, so a person keeps their scroll position.
        add_vertical_scrollbar(question_holder, question_text)

        ttk.Label(content, text=("Nova mensagem:" if conversational else
                                 "Sua resposta:")).pack(anchor="w")
        answer_holder = ttk.Frame(content)
        answer_holder.pack(fill="x", pady=(3, 10))
        self.continuation_answer = tk.Text(answer_holder, height=4, wrap="word",
                                           font=("Segoe UI", 11))
        if self.last_continuation_answer:
            self.continuation_answer.insert("1.0", self.last_continuation_answer)
        add_vertical_scrollbar(answer_holder, self.continuation_answer)

        controls = ttk.Frame(content)
        controls.pack(fill="x")
        ttk.Button(controls, text="Abrir arquivos da tarefa",
                   command=self.open_current_task_folder).pack(side="left")
        ttk.Button(controls, text="Enviar arquivo...",
                   command=self.add_continuation_attachments).pack(side="left", padx=(8, 0))
        ttk.Button(controls, text="Remover arquivo...",
                   command=self.remove_continuation_attachment).pack(side="left", padx=(8, 0))
        ttk.Button(controls, text=("Enviar e continuar conversa" if conversational else
                                   "Responder e continuar a mesma tarefa"),
                   command=self.continue_current_task).pack(side="right")

    def close_continuation_window(self):
        """Hide the UI without discarding its on-disk continuation state."""
        if self.continuation_window and self.continuation_window.winfo_exists():
            self.continuation_window.destroy()
        self.continuation_window = None
        self.continuation_answer = None

    def open_current_task_folder(self):
        try:
            os.startfile(self.pending_workspace())
        except (OSError, ValueError) as exc:
            messagebox.showerror("Arquivos da tarefa", str(exc))

    def add_continuation_attachments(self):
        if self.running or self.busy_operation:
            return
        if not self.pending or not (self.current_session_id or self.pending.get('new_session')):
            return messagebox.showinfo('Anexos','Abra uma tarefa antes de enviar um arquivo.')
        workspace=self.pending_workspace()
        chosen=filedialog.askopenfilenames(title='Enviar arquivos para a próxima mensagem',filetypes=[('Todos os arquivos','*.*')])
        paths=[Path(value).expanduser().resolve() for value in chosen]
        paths=[path for path in paths if path.is_file()]
        if not paths or not self.has_portable_capacity(sum(path.stat().st_size for path in paths),'copiar estes anexos'):
            return
        attachments=list(self.pending.get('staged_attachments',[]))
        recovery=self.continuation_state(self.pending_question) if self.current_session_id else None
        record_path=self.conversation_record_path
        def copy():
            new_items=gate.stage_continuation_attachments(workspace,paths)
            combined=attachments+new_items
            if recovery:
                recovery['staged_attachments']=combined
                gate.save_continuation_state(workspace,recovery)
            if record_path:
                gate.update_execution_record(record_path,attachments=combined)
            return combined,len(new_items)
        def present(result):
            self.pending['staged_attachments']=result[0]
            self.load_history()
            self.status.set(f'{result[1]} arquivo(s) preparado(s) para a próxima mensagem.')
            self.refresh_portable_storage_status()
        self.start_job('Copiar anexos',copy,present,exclusive=True)


    def remove_continuation_attachment(self):
        """Unlink one active context file while retaining its audit trail on disk."""
        if self.running:
            return messagebox.showinfo("Anexos", "Aguarde a atividade atual terminar.")
        if not self.pending or not (self.current_session_id or self.pending.get("new_session")):
            return messagebox.showinfo(
                "Anexos", "Abra ou continue uma tarefa com sessão disponível antes de remover um arquivo.")
        active = [(index, item) for index, item in enumerate(
            self.pending.get("staged_attachments", []))
            if isinstance(item, dict) and item.get("active", True)]
        if not active:
            return messagebox.showinfo("Anexos", "Não há arquivos ativos nesta conversa.")
        window = tk.Toplevel(self)
        window.title("Remover arquivo da conversa")
        window.geometry("640x300")
        window.transient(self)
        content = ttk.Frame(window, padding=12)
        content.pack(fill="both", expand=True)
        ttk.Label(content, text=("Escolha o arquivo que não deve mais ser usado nas próximas mensagens. "
                                 "A cópia e o histórico serão preservados."),
                  style="Hint.TLabel", wraplength=590).pack(anchor="w", pady=(0, 8))
        listing = tk.Listbox(content, height=9)
        listing.pack(fill="both", expand=True)
        for _, item in active:
            listing.insert(tk.END, str(item.get("staged") or item.get("original") or "Arquivo"))
        def detach():
            choice = listing.curselection()
            if not choice:
                return messagebox.showinfo("Anexos", "Selecione um arquivo para remover.", parent=window)
            index, item = active[choice[0]]
            item["active"] = False
            item["detached_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
            try:
                workspace = self.pending_workspace()
                if self.current_session_id:
                    gate.save_continuation_state(workspace, self.continuation_state(
                        self.pending_question or "A tarefa está pronta para continuar."))
                if self.conversation_record_path and self.conversation_record_path.is_file():
                    gate.update_execution_record(
                        self.conversation_record_path,
                        attachments=self.pending["staged_attachments"])
                    self.load_history()
            except (OSError, ValueError) as exc:
                item["active"] = True
                item.pop("detached_at", None)
                return messagebox.showerror("Anexos", str(exc), parent=window)
            window.destroy()
            self.status.set("Arquivo desanexado. Ele não será usado nas próximas mensagens da conversa.")
        controls = ttk.Frame(content)
        controls.pack(fill="x", pady=(10, 0))
        ttk.Button(controls, text="Cancelar", command=window.destroy).pack(side="left")
        ttk.Button(controls, text="Remover da conversa", command=detach).pack(side="right")

    def continue_current_task(self):
        if self.running or self.busy_operation:
            return
        if not self.pending or not (self.current_session_id or self.pending.get("new_session")):
            return messagebox.showerror(
                "Continuação", "Não há uma sessão válida para retomar.")
        answer = self.continuation_answer.get("1.0", tk.END).strip() if self.continuation_answer else ""
        if not answer:
            return messagebox.showwarning(
                "Nova mensagem" if self.continuation_mode == "conversation" else "Sua resposta",
                "Escreva uma mensagem antes de continuar.")
        if not self.has_portable_capacity(0, "retomar esta tarefa"):
            return
        try:
            workspace = self.pending_workspace()
            model = gate.MODELS[str(self.pending.get("model", "")).lower()]
            effort = str(self.pending.get("effort", "")).lower()
            executable = gate.resolve_codex_executable()
            if not executable:
                self.status.set("Codex CLI não encontrado; a conversa não foi iniciada.")
                self.phase_var.set("Codex CLI ausente")
                return messagebox.showerror(
                    "Codex CLI ausente",
                    "O executável do Codex não foi encontrado. Confira a seção Codex CLI na aba Tarefa.")
            if executable != self.cli_executable or self.executable_signature(executable) != self.cli_signature or not self.cli_version:
                self.refresh_codex_cli_status()
                return messagebox.showinfo('Codex CLI', 'Verificando a versão do CLI. Aguarde o resultado antes de executar.')
            compatibility_message = gate.cli_model_compatibility_message(
                executable, str(self.pending.get("model", "")).lower(), self.cli_version)
            if compatibility_message:
                self.status.set(compatibility_message)
                return messagebox.showwarning("Atualização do Codex CLI", compatibility_message)
            live_web_search = (bool(self.pending.get("live_web_search")) or
                               gate.needs_live_web_search(answer, []))
            if self.pending.get('new_session'):
                command = gate.build_codex_exec_command(model, effort,
                    workspace if self.pending.get('browser_research') else None,live_web_search,executable)
            else:
                command = gate.build_codex_resume_command(self.current_session_id, model, effort,
                    workspace if self.pending.get('browser_research') else None,
                    live_web_search=live_web_search,codex_executable=executable)
            if self.continuation_mode == "conversation":
                if not messagebox.askyesno(
                        "Confirmar continuidade",
                        f"Enviar esta mensagem com {self.pending['model'].capitalize()} — "
                        f"{gate.EFFORT_LABELS[effort]}?\n\n"
                        "O Codex continuará na mesma pasta e poderá criar ou alterar "
                        "arquivos da tarefa conforme o pedido."):
                    return
                prompt = gate.build_task_followup_prompt(
                    answer, self.pending.get("staged_attachments", []))
            else:
                prompt = gate.build_continuation_prompt(
                    answer, self.pending.get("staged_attachments", []))
            if self.pending.get('new_session'):
                context = json.dumps(self.conversation_turns, ensure_ascii=False)[-64000:]
                historical = ('HISTÓRICO IMPORTADO PARA CONTEXTO (não repita operações passadas):\n' + context
                    + '\nTarefa original: ' + self.pending['task'] + '\nNOVO PEDIDO DO USUÁRIO: ' + answer)
                prompt = gate.build_execution_prompt(historical, '', self.pending.get('staged_attachments', []))
            prompt += ("\nSe citar uma página, confira na fonte original que ela sustenta "
                       "diretamente a afirmação; não invente links ou seções.")
            # Preserve a draft before starting the process. If the process
            # cannot start or is interrupted, the person can explicitly retry
            # instead of silently losing or duplicating their response.
            self.last_continuation_answer = answer
            self.sent_continuation_message = answer
            if self.continuation_mode == "conversation":
                self.current_followup_request = answer
            state = self.continuation_state(self.pending_question)
            state["draft_answer"] = answer
            state["answer_sent_at"] = datetime.now().astimezone().isoformat(
                timespec="seconds")
            state["live_web_search"] = live_web_search
            if self.current_session_id:
                gate.save_continuation_state(workspace, state)
            self.pending["live_web_search"] = live_web_search
        except KeyError:
            return messagebox.showerror(
                "Continuação", "O modelo salvo para esta tarefa não é válido.")
        except (OSError, ValueError) as exc:
            return messagebox.showerror("Continuação", str(exc))
        # The root shown in the form may have changed while the question was
        # open.  Resume only in the workspace saved with this exact session.
        self.cwd = workspace
        self.projects_root = workspace.parent
        self.path_var.set(str(self.projects_root))
        self.before_files = {}
        self.artifacts = []
        self.clear_artifact_display()
        self.continuation_in_flight = True
        self.supervisor = ProcessSupervisor()
        self.cancel_requested = False
        self.execution_started_at = datetime.now().astimezone().isoformat(timespec="seconds")
        self.execution_started_monotonic = clock.monotonic()
        self.execution_duration_seconds = None
        self.running = True
        self.set_controls("disabled")
        self.status.set("Resposta enviada. O Codex está retomando a mesma sessão.")
        self.simple_progress_var.set("Continuando a tarefa no mesmo contexto e na mesma pasta.")
        self.phase_var.set("Retomando sessão do Codex")
        self.progress_bar.configure(mode="indeterminate")
        self.update_progress()
        self.close_continuation_window()
        self.append_log("\nResposta enviada para retomar a mesma tarefa.\n")
        def prepared(snapshot):
            self.before_files = snapshot
            threading.Thread(target=self.run_codex, args=(command, prompt), daemon=True).start()
        self.start_job('Preparação da tarefa',lambda: gate.snapshot_project_files(workspace),prepared,exclusive=True)

    def on_task_modified(self, _event=None):
        """Refresh the action cue after typing, pasting, or choosing a template."""
        if not self.task.edit_modified():
            return
        self.task.edit_modified(False)
        self.update_action_buttons()

    def update_action_buttons(self):
        """Show which step is ready and which step was already activated."""
        task_text = self.task.get("1.0", tk.END).strip()
        analyzed = bool(self.pending and self.pending.get("assessment") and
                        task_text == self.pending["task"] and
                        self.attachments == self.pending.get("attachments"))
        executed = analyzed and self.action_executed
        self.recommend_button.configure(
            style="ActivatedAction.TButton" if analyzed else
                  "Primary.TButton" if task_text else "WaitingAction.TButton",
            text=("✓ " if analyzed else "") + self.tr("1. Analisar tarefa"))
        self.run_button.configure(
            style="ActivatedAction.TButton" if executed else
                  "Primary.TButton" if analyzed else "WaitingAction.TButton",
            text=("✓ " if executed else "") + self.tr("2. Confirmar e executar"))

    def recommend(self):
        if self.running or self.busy_operation or self.selecting_skills:
            return
        try:
            self.projects_root = gate.validate_projects_root(self.path_var.get())
        except (ValueError, OSError) as exc:
            return messagebox.showwarning('Pasta de projetos', str(exc))
        if self.pending_question:
            self.show_continuation_window()
            return messagebox.showinfo(
                "Continuação pendente",
                "Responda ou conclua a pergunta pendente antes de iniciar outra tarefa.")
        task = self.task.get("1.0", tk.END).strip()
        if not task:
            return messagebox.showwarning("Tarefa", "Descreva a tarefa primeiro.")
        analysis_task = gate.attachment_context(task, self.attachments)
        automatic = not self.manual_skills_var.get()
        library = Path(self.skill_library_var.get()).expanduser(
        ) if self.skill_library_var.get().strip() else None
        roots = [library] if library and library.is_dir() else None
        selected = [self.filtered_skill_items[i]
                    for i in self.skill_list.curselection()] if not automatic else []
        if automatic:
            executable = gate.resolve_codex_executable()
            if not executable:
                return messagebox.showwarning('Seleção inteligente',
                    'Instale e autentique o Codex CLI ou escolha as skills manualmente.')
            attachments = list(self.attachments)
            projects_root = self.projects_root
            self.pending = None
            self.update_action_buttons()
            self.selecting_skills = True
            self.selection_supervisor = ProcessSupervisor()
            self.status.set('A IA está analisando a tarefa, os anexos e todas as competências da biblioteca.')
            self.simple_progress_var.set('Análise inteligente pelo CLI: esta etapa usa o modelo e consome tokens.')
            def analyze():
                catalog = gate.discover_skills(projects_root, roots)
                result = select_skills_with_ai(task, catalog, attachments, executable,
                    supervisor=self.selection_supervisor)
                return catalog, result
            def present(result):
                self.selecting_skills = False
                catalog, decision = result
                self.skills = catalog
                if task != self.task.get('1.0', tk.END).strip() or attachments != self.attachments:
                    raise ValueError('A tarefa ou os anexos mudaram. Analise novamente.')
                selected = gate.include_orchestrator_skill(
                    projects_root, decision['selected'], roots, catalog=catalog)
                source = 'Seleção inteligente por IA: tarefa, anexos e catálogo completo analisados.'
                if not decision['selected']:
                    source += ' A IA não identificou uma skill pertinente no catálogo.'
                if decision['attachment_findings']:
                    source += '\nAnexos: ' + decision['attachment_findings']
                if decision['limitations']:
                    source += '\nLimitações: ' + decision['limitations']
                self.apply_recommendation(task, analysis_task, selected, True, source)
                self.pending['skill_selection'] = {key: value for key, value in decision.items() if key != 'selected'}
                self.pending['live_web_search'] = decision['live_web_search'] or self.pending['live_web_search']
            self.start_job('Seleção inteligente', analyze, present, exclusive=True)
            return
        else:
            selected = gate.include_orchestrator_skill(
                self.projects_root, selected, roots, catalog=self.skills)
            selection_source = "Seleção manual confirmada pela orquestradora."
        self.apply_recommendation(task, analysis_task, selected, automatic, selection_source)

    def apply_recommendation(self, task, analysis_task, selected, automatic, selection_source):
        if automatic and selected:
            selected = gate.include_orchestrator_skill(
                self.projects_root, selected, catalog=self.skills)
        assessment = gate.assess_task(analysis_task, selected)
        model, effort, reason = gate.recommend(
            analysis_task, selected, assessment)
        policy = gate_i18n.source_text(self.policy_var.get(), self.language)
        controls = gate.decision_controls(assessment, policy)
        self.pending = {"recommended_model": model, "recommended_effort": effort, "id": uuid.uuid4().hex, "task": task, "attachments": list(self.attachments), "staged_attachments": [], "project_folder": "", "skills": [
            s["name"] for s in selected], "selected_skills": selected, "model": model, "effort": effort, "assessment": assessment, "policy": policy, "controls": controls,
            "live_web_search": gate.needs_live_web_search(analysis_task, selected)}
        self.action_executed = False
        self.update_action_buttons()
        self.model_var.set(model_label(model))
        self.effort_var.set(self.tr(gate.EFFORT_LABELS[effort]))
        self.decision_model_card_var.set(model_label(model))
        self.decision_effort_card_var.set(gate.EFFORT_LABELS[effort])
        self.decision_risk_card_var.set(gate.risk_level(assessment))
        self.decision_skills_card_var.set(str(sum(x["name"] != gate.ORCHESTRATOR_SKILL_NAME for x in selected)))
        if automatic:
            selected_names = {skill["name"] for skill in selected}
            self.render_skill_list(selected_names)
        self.on_model_selection_changed()
        self.update_active_skills(selected, automatic)
        names = ", ".join(self.pending["skills"]) or "nenhuma"
        attachment_names = ", ".join(
            path.name for path in self.attachments) or "nenhum"
        label = "escolhidas pela orquestradora" if automatic else "selecionadas manualmente"
        self.status.set(
            f"Recomendação: {model.capitalize()} — {gate.EFFORT_LABELS[effort]}\n{selection_source}\nSkills {label}: {names}\nAnexos: {attachment_names}\nMotivo: {reason}.\n{gate.assessment_summary(assessment)}\nAguardando autorização.")
        self.simple_progress_var.set(
            "Decisão pronta. Confira os cartões, as skills recomendadas e a pasta de destino; depois autorize a execução.")
        self.sync_decision_settings()
        destination = Path(self.path_var.get()).expanduser()
        self.decision_checklist_var.set(
            "Checklist antes de confirmar: 1) o resultado esperado está claro; "
            f"2) anexos conferidos ({len(self.attachments)}); "
            f"3) destino conferido ({destination.name or destination}); "
            f"4) skills revisadas ({len(selected)}).")

    def schedule_current_task(self):
        """Save a local schedule which always requires confirmation at runtime."""
        task = self.task.get("1.0", tk.END).strip()
        if not task:
            return messagebox.showwarning("Agendar tarefa", "Descreva a tarefa antes de agendá-la.")
        local_date_format = "%d/%m/%Y %H:%M" if self.language in {"pt-BR", "es"} else "%Y-%m-%d %H:%M"
        value = simpledialog.askstring(
            "Agendar tarefa", self.tr("Quando preparar esta tarefa?") + "\n" +
            self.tr("Use DD/MM/AAAA HH:MM (horário local)."))
        if value is None:
            return
        try:
            when = datetime.strptime(value.strip(), local_date_format).astimezone()
        except ValueError:
            return messagebox.showwarning(
                "Agendar tarefa", self.tr("Informe data e hora no formato DD/MM/AAAA HH:MM."))
        if when <= datetime.now().astimezone():
            return messagebox.showwarning("Agendar tarefa", "Escolha um horário futuro.")
        daily = messagebox.askyesno(
            "Repetir diariamente", "Deseja preparar esta mesma tarefa todos os dias nesse horário?")
        entries = gate.load_scheduled_tasks()
        entries.append({
            "id": uuid.uuid4().hex,
            "task": task,
            "project_root": self.path_var.get().strip(),
            "browser_research": bool(self.browser_research_var.get()),
            "browser_query": self.browser_query_var.get().strip(),
            "next_run": when.isoformat(timespec="minutes"),
            "recurrence": "daily" if daily else "once",
        })
        gate.save_scheduled_tasks(entries)
        self.status.set("Tarefa agendada. No horário, o Gate pedirá sua confirmação antes de analisar ou executar.")
        messagebox.showinfo(
            "Tarefa agendada", "O agendamento foi salvo localmente. O Codex não será executado sem sua confirmação no horário previsto.")

    def check_scheduled_tasks(self):
        """Offer due tasks only while the app is open; never run them silently."""
        try:
            if self.running or self.selecting_skills:
                return
            due = gate.due_scheduled_tasks()
            if not due:
                return
            entries = gate.load_scheduled_tasks()
            changed = False
            for entry in due:
                advanced = gate.advance_scheduled_task(entry)
                entries = [item for item in entries if item.get("id") != entry.get("id")]
                if advanced:
                    entries.append(advanced)
                changed = True
                if messagebox.askyesno(
                        "Tarefa agendada pronta",
                        "Chegou o horário desta tarefa:\n\n" + str(entry["task"]) +
                        "\n\nDeseja prepará-la agora? A análise será feita primeiro e a execução continuará exigindo confirmação."):
                    self.task.delete("1.0", tk.END)
                    self.task.insert("1.0", str(entry["task"]))
                    root = str(entry.get("project_root") or "").strip()
                    if root:
                        self.path_var.set(root)
                    self.browser_research_var.set(bool(entry.get("browser_research")))
                    self.browser_query_var.set(str(entry.get("browser_query") or ""))
                    self.pending = None
                    self.recommend()
                break
            if changed:
                gate.save_scheduled_tasks(entries)
        finally:
            self.after(60000, self.check_scheduled_tasks)

    def authorize_run(self):
        if self.running or self.busy_operation:
            return
        if self.pending_question:
            self.show_continuation_window()
            return
        if not self.pending:
            return messagebox.showwarning('Autorização', 'Analise uma tarefa antes de executar.')
        if self.task.get('1.0', tk.END).strip() != self.pending['task'] or self.attachments != self.pending['attachments']:
            return messagebox.showwarning('Análise desatualizada', 'A tarefa ou os anexos mudaram. Analise novamente.')
        signature = self.pending.get('skill_selection', {}).get('attachment_signature')
        if signature is not None:
            try:
                if signature != attachment_signature(self.attachments):
                    raise ValueError('O conteúdo de um anexo mudou. Analise novamente antes de executar.')
            except (ValueError, OSError) as exc:
                return messagebox.showwarning('Análise desatualizada', str(exc))
        try:
            root = gate.validate_projects_root(self.path_var.get())
            model = model_key(self.model_var.get())
            effort_label = gate_i18n.source_text(self.effort_var.get(), self.language)
            effort = next((k for k, v in gate.EFFORT_LABELS.items() if v == effort_label), '')
            gate.validate_model_effort(gate.MODELS[model], effort)
            policy = gate_i18n.source_text(self.policy_var.get(), self.language)
            if policy not in gate.POLICIES:
                raise ValueError('Escolha uma política válida.')
        except (ValueError, OSError, KeyError) as exc:
            return messagebox.showwarning('Decisão', str(exc))
        self.projects_root = root
        self.pending.update(model=model, effort=effort, policy=policy,
                            controls=gate.decision_controls(self.pending['assessment'], policy))
        executable = gate.resolve_codex_executable()
        if not executable:
            self.open_codex_install_guide()
            return messagebox.showwarning('Codex CLI', 'Instale e autentique o CLI; depois clique em Verificar novamente.')
        if not self.cli_version or executable != self.cli_executable or self.executable_signature(executable) != self.cli_signature:
            self.refresh_codex_cli_status()
            return messagebox.showinfo('Codex CLI', 'Verificando a versão do CLI. Aguarde o resultado antes de executar.')
        warning = gate.cli_model_compatibility_message(executable, model, self.cli_version)
        if warning:
            self.cli_status_var.set(warning)
            return messagebox.showwarning('Atualização do Codex CLI', warning)
        risk = int(self.pending['assessment']['risk'])
        if risk >= 3 or policy == 'rigorosa' and risk >= 1:
            if simpledialog.askstring('Confirmação reforçada', 'Digite EXECUTAR para confirmar que revisou escopo, arquivos e consequências:') != 'EXECUTAR':
                return
        if not self.has_portable_capacity(sum(p.stat().st_size for p in self.attachments if p.is_file()), 'iniciar esta tarefa'):
            return
        browser = bool(self.browser_research_var.get())
        live = bool(self.pending.get('live_web_search')) or browser
        config = AuthorizedTask(self.pending['id'], self.pending['task'], root, model, effort, policy,
                                tuple(self.attachments), browser, live, self.browser_query_var.get().strip())
        message = (f"Executar com {model_label(model)} — {gate.EFFORT_LABELS[effort]}?\n\n"
                   f"Destino: {root}\nPolítica: {gate.POLICIES[policy]}\n"
                   f"Anexos: {len(config.attachments)}\nSkills: {', '.join(self.pending['skills']) or 'nenhuma'}")
        if not messagebox.askyesno('Confirmar execução', message):
            return
        self.supervisor = ProcessSupervisor()
        self.cancel_requested = False
        self.running = True
        self.pending.update(browser_research=browser, live_web_search=live, browser_query=config.browser_query)
        self.phase_var.set('Preparando tarefa')
        self.simple_progress_var.set('Copiando anexos e preparando instruções...')
        self.execution_started_at = datetime.now().astimezone().isoformat(timespec='seconds')
        self.execution_started_monotonic = clock.monotonic()
        self.update_progress()
        skills = [dict(item) for item in self.pending['selected_skills']]
        self.start_job('Preparação da tarefa', lambda: prepare_task(config, skills, executable, self.supervisor.cancelled),
                       self.begin_prepared_task, exclusive=True)

    def begin_prepared_task(self, result):
        self.cwd, staged, fingerprints, instructions, command, self.before_files = result
        self.pending.update(project_folder=str(self.cwd), staged_attachments=staged, skill_fingerprints=fingerprints)
        self.artifacts = []
        self.clear_artifact_display()
        self.clear_log()
        self.show_response('', select=False)
        self.current_session_id = self.current_token_usage = self.pending_question = None
        self.conversation_record_path = None
        self.conversation_turns = []
        self.sent_continuation_message = self.current_followup_request = ''
        self.continuation_mode = 'question'
        self.run_id = self.pending['id']
        self.execution_duration_seconds = None
        self.record_note_path = None
        self.action_executed = True
        self.update_action_buttons()
        self.consumption_var.set('Consumo desta tarefa: aguardando retorno do Codex.')
        self.phase_var.set('Iniciando Codex')
        self.set_controls('disabled')
        self.estimated_total_seconds = gate.estimate_duration_seconds(
            f"{model_label(self.pending['model'])} — {gate.EFFORT_LABELS[self.pending['effort']]}", self.record_cache)
        threading.Thread(target=self.run_prepared_task, args=(command, instructions), daemon=True).start()


    def note_startup_step(self, step):
        """Keep a local startup trace if execution stalls before a response."""
        try:
            path = gate.gate_dir(self.cwd) / "startup-status.txt"
            with path.open("a", encoding="utf-8") as trace:
                trace.write(datetime.now().astimezone().isoformat(
                    timespec="seconds") + " | " + step + "\n")
        except OSError:
            pass

    def run_prepared_task(self, command, instructions):
        """Start Codex without a blocking browser preparation step."""
        try:
            self.note_startup_step("Preparando instrução para o Codex")
            self._run_prepared_task(command, instructions)
        except Exception as exc:
            self.note_startup_step(f"Falha na preparação: {type(exc).__name__}: {exc}")
            self.events.put(("done", 1, f"A preparação da tarefa falhou: {exc}", None, ""))

    def _run_prepared_task(self, command, instructions):
        if self.pending.get("browser_research"):
            self.events.put(("log", "Navegador visual do Gate disponível durante a tarefa.\n"))
        try:
            prompt = gate.build_execution_prompt(
                self.pending["task"], instructions,
                self.pending["staged_attachments"],
                browser_available=bool(self.pending.get("browser_research")),
                browser_query=str(self.pending.get("browser_query") or ""))
        except Exception as exc:
            self.events.put(("done", 1, f"Não foi possível preparar a tarefa: {exc}", None, ""))
            return
        if self.cancel_requested:
            self.events.put(("done", 1, "Execução cancelada pelo usuário.", None, ""))
            return
        self.note_startup_step("Abrindo processo do Codex")
        self.run_codex(command, prompt)

    def run_codex(self, command, prompt):
        try:
            self._run_codex(command, prompt)
        except Exception as exc:
            self.note_startup_step(f"Falha na execução: {type(exc).__name__}: {exc}")
            process = self.active_process
            if process and process.poll() is None:
                try:
                    self.supervisor.cancel()
                except OSError:
                    pass
            self.events.put(("done", 1, f"A execução do Codex falhou: {exc}", None, ""))

    def _run_codex(self, command, prompt):
        def started(process):
            self.active_process = process
            self.events.put(('phase', 'Codex iniciado', 'O Codex recebeu a tarefa.'))
        result, session, output, raw = self.supervisor.run(command, prompt, self.cwd,
                gate.codex_process_environment(), lambda text: self.events.put(('log', text)), started)
        self.events.put(('done', result, output, session, raw))


    def cancel_run(self):
        if self.selecting_skills:
            self.status.set('Cancelando a análise inteligente...')
            self.cancel_button.configure(state='disabled')
            self.start_job('Cancelamento da análise', self.selection_supervisor.cancel, lambda _: None)
            return
        if not self.running:
            return
        if not messagebox.askyesno('Cancelar execução', 'Encerrar a execução atual? Os arquivos parciais serão preservados.'):
            return
        self.cancel_requested = True
        self.supervisor.cancelled.set()
        self.phase_var.set('Cancelando execução')
        self.cancel_button.configure(state='disabled')
        self.start_job('Cancelamento', self.supervisor.cancel, lambda _: None)


    def poll_events(self):
        pending_logs = []
        processed = 0

        def flush_logs():
            if pending_logs:
                self.append_log("".join(pending_logs))
                pending_logs.clear()

        try:
            while processed < 250:
                event = self.events.get_nowait()
                processed += 1
                if event[0] == 'job_done':
                    flush_logs()
                    self.finish_job(event)
                elif event[0] == "log":
                    pending_logs.append(event[1])
                elif event[0] == "phase":
                    flush_logs()
                    if not self.cancel_requested:
                        self.phase_var.set(event[1])
                        self.simple_progress_var.set(event[2])
                elif event[0] == "done":
                    flush_logs()
                    self.finish_run(
                        event[1], event[2],
                        event[3] if len(event) > 3 else None,
                        event[4] if len(event) > 4 else "")
                elif event[0] == "selection_done":
                    flush_logs()
                    self.selecting_skills = False
                    self.set_controls("normal")
                    self.apply_recommendation(event[1], event[2], event[3], True, event[4])
        except queue.Empty:
            pass
        except Exception as exc:
            self.note_startup_step(f"Falha ao apresentar resultado: {type(exc).__name__}: {exc}")
            self.report_callback_exception(type(exc), exc, exc.__traceback__)
        finally:
            if pending_logs:
                flush_logs()
            try:
                if self.winfo_exists():
                    self.after(10 if processed >= 250 else 100, self.poll_events)
            except tk.TclError:
                pass

    def finish_run(self, returncode, output, session_id=None, raw_output=''):
        self.phase_var.set('Validando resultados' if not returncode else 'Preservando resultado parcial')
        self.simple_progress_var.set('Identificando arquivos e verificando a entrega...')
        self.show_response(output, select=True)
        task = self.current_followup_request or self.pending['task']
        cwd = self.cwd
        before = dict(self.before_files)
        names = list(self.pending.get('skills', []))
        def collect():
            after = gate.snapshot_project_files(cwd)
            artifacts = [cwd / name for name, meta in after.items() if before.get(name) != meta]
            installed, issues = [], []
            if not returncode:
                enough_space = (not gate.is_portable_mode() or gate.portable_storage_estimate(
                    gate.directory_size(cwd / 'skill-output'), scan_sizes=False)['sufficient'])
                if enough_space:
                    installed, issues = gate.import_generated_skills(task, cwd)
                else:
                    issues.append('Sem reserva de espaço para instalar skills. Os arquivos gerados foram preservados na pasta da tarefa.')
            artifacts.extend(installed)
            if not returncode:
                issues += gate.validate_download_outputs(task, artifacts)
                if gate.is_document_task(task):
                    documents = [p for p in artifacts if p.suffix.lower() in {'.pdf', '.docx'}]
                    if not documents:
                        issues.append('A tarefa pediu um documento, mas nenhum DOCX ou PDF criado ou alterado foi identificado.')
                    for path in documents:
                        issues += [f'{path.name}: {issue}' for issue in gate.validate_document_file(path,
                            gate.should_validate_abnt_citations(task, names), gate.should_validate_citation_reference_links(task, names))]
            return {'artifacts': artifacts, 'installed': installed, 'validation': issues}
        def present(data):
            self._completion_data = data
            self.present_finished_run(returncode, output, session_id, raw_output)
        self.start_job('Validação da tarefa', collect, present, exclusive=True)


    def save_execution_record(self, status, validation, output):
        try:
            artifacts = []
            for value in (list(self.pending.get("existing_artifacts", [])) +
                          [str(path) for path in self.artifacts]):
                text = str(value).strip()
                if text and text not in artifacts:
                    artifacts.append(text)
            conversation = gate.normalize_conversation_turns(
                self.conversation_turns)
            if not conversation:
                now = datetime.now().astimezone().isoformat(timespec="seconds")
                conversation = [
                    {"role": "user", "text": self.pending["task"],
                     "at": self.execution_started_at or now},
                    {"role": "assistant", "text": output, "at": now},
                ]
                self.conversation_turns = conversation
            duration = (float(self.pending.get("existing_duration") or 0) +
                        float(self.execution_duration_seconds or 0))
            turn_metrics = list(self.pending.get("turn_metrics") or [])
            turn_metrics.append({
                "started_at": self.execution_started_at or "",
                "duration_seconds": self.execution_duration_seconds,
                "token_usage": self.current_token_usage,
                "model_key": self.pending["model"],
                "pricing": dict(gate.TOKEN_PRICES_USD_PER_MILLION.get(self.pending["model"], {})),
                "exchange_rates": dict(gate.COST_CURRENCY_RATES),
            })
            aggregate_usage = None
            for metric in turn_metrics:
                usage = metric.get("token_usage") if isinstance(metric, dict) else None
                if isinstance(usage, dict):
                    if aggregate_usage is None:
                        aggregate_usage = {key: 0 for key in (
                            "input", "cached_input", "output", "reasoning")}
                    for key in aggregate_usage:
                        aggregate_usage[key] += max(0, int(usage.get(key, 0)))
            policy_key = str(self.pending.get("policy") or "equilibrada")
            payload = {
                "id": self.run_id or uuid.uuid4().hex,
                "started_at": self.pending.get("original_started_at") or self.execution_started_at or "",
                "duration_seconds": duration,
                "status": status,
                "quality": self.pending.get("quality", "Não avaliado"),
                "model": f"{model_label(self.pending['model'])} — {gate.EFFORT_LABELS[self.pending['effort']]}",
                "model_key": self.pending["model"],
                "model_id": gate.MODELS[self.pending["model"]],
                "effort": self.pending["effort"],
                "project_folder": self.pending.get("project_folder", ""),
                "policy": gate.POLICIES.get(policy_key, policy_key),
                "policy_key": policy_key if policy_key in gate.POLICIES else "equilibrada",
                "task": self.pending["task"],
                "skills": self.pending.get("skills", []),
                "skill_fingerprints": self.pending.get("skill_fingerprints", []),
                "skill_selection": self.pending.get("skill_selection", {}),
                "attachments": self.pending.get("staged_attachments", []),
                "artifacts": artifacts,
                "validation": validation,
                "execution_output": output,
                "browser_research": bool(self.pending.get("browser_research")),
                "browser_query": str(self.pending.get("browser_query") or ""),
                "live_web_search": bool(self.pending.get("live_web_search")),
                "session_id": self.current_session_id or "",
                "conversation": conversation,
                "continuation_count": max(
                    0, sum(1 for turn in conversation
                           if turn.get("role") == "user") - 1),
                "last_activity_at": datetime.now().astimezone().isoformat(
                    timespec="seconds"),
                "token_usage": aggregate_usage,
                "turn_metrics": turn_metrics,
            }
            previous = self.conversation_record_path
            recovery = self.continuation_state(self.pending_question) if status == 'Aguardando resposta' else None
            workspace = self.cwd
            def persist():
                if previous and previous.is_file():
                    gate.update_execution_record(previous, **payload)
                    path = previous
                else:
                    path = gate.write_execution_record(payload)
                if recovery:
                    recovery.update(record_file=str(path), existing_duration=duration, turn_metrics=turn_metrics)
                    gate.save_continuation_state(workspace, recovery)
                return path
            def present(path):
                self.record_note_path = self.conversation_record_path = path
                self.pending['existing_duration'] = duration
                self.pending['turn_metrics'] = turn_metrics
                self.load_history()
                self.status.set(f'Registro salvo: {path.name}.')
                self.phase_var.set(status)
                if status == 'Concluída' and self.auto_open_outputs_var.get():
                    candidates=[path for path in self.artifacts if path.suffix.lower() in {'.pdf','.png','.jpg','.jpeg'}]
                    for artifact in candidates[:3]:
                        try:
                            os.startfile(artifact)
                        except OSError as exc:
                            self.status.set(f'Registro salvo; não foi possível abrir {artifact.name}: {exc}')
                if recovery:
                    self.show_continuation_window()
            self.start_job('Salvar registro', persist, present, exclusive=True)
        except (OSError, ValueError) as exc:
            self.status.set(f"Registro não pôde ser salvo: {exc}")
            self.phase_var.set("Falha ao salvar registro")
            messagebox.showerror("Registro", str(exc))

    def validate_document_outputs(self):
        task = self.current_followup_request or self.pending["task"]
        download_issues = gate.validate_download_outputs(task, self.artifacts)
        if not gate.is_document_task(task):
            return download_issues
        document_outputs = [path for path in self.artifacts if path.suffix.lower() in {
            ".docx", ".pdf"}]
        if not document_outputs:
            return download_issues or ["A tarefa pediu um documento, mas nenhum DOCX ou PDF criado ou alterado foi identificado."]
        check_abnt = gate.should_validate_abnt_citations(
            task, self.pending.get("skills", []))
        check_links = gate.should_validate_citation_reference_links(
            task, self.pending.get("skills", []))
        document_issues = [f"{path.name}: {issue}" for path in document_outputs for issue in gate.validate_document_file(
            path, check_abnt, check_links)]
        return download_issues + document_issues

    def snapshot_files(self):
        if not self.cwd.is_dir():
            return {}
        return {str(path.relative_to(self.cwd)): (path.stat().st_size, path.stat().st_mtime_ns) for path in self.cwd.rglob("*") if path.is_file() and ".codex-model-gate" not in path.parts}

    def refresh_artifacts(self):
        after = self.snapshot_files()
        changed = sorted(path for path, meta in after.items()
                         if self.before_files.get(path) != meta)
        self.artifacts = [self.cwd / path for path in changed]
        self.clear_artifact_display()
        for path in self.artifacts:
            self.add_artifact_display(path)

    def clear_artifact_display(self):
        self.artifact_list.delete(0, tk.END)
        self.artifact_preview_image = None
        if hasattr(self, "artifact_thumbnail"):
            self.artifact_thumbnail.configure(image="", text="Selecione um arquivo")
            self.artifact_preview_var.set(
                "Selecione um resultado para ver tipo, tamanho e data.")

    @staticmethod
    def artifact_type_label(path):
        suffix = path.suffix.lower()
        labels = {
            ".pdf": "PDF", ".docx": "Documento Word", ".xlsx": "Planilha",
            ".pptx": "Apresentação", ".png": "Imagem", ".jpg": "Imagem",
            ".jpeg": "Imagem", ".webp": "Imagem", ".svg": "Imagem vetorial",
            ".txt": "Texto", ".md": "Texto", ".csv": "Dados", ".json": "Dados",
            ".zip": "Arquivo ZIP",
        }
        return labels.get(suffix, "Arquivo")

    def add_artifact_display(self, path, label=None):
        try:
            display_path = str(path.relative_to(self.cwd))
        except ValueError:
            display_path = path.name
        try:
            size = self._format_storage_size(path.stat().st_size)
        except OSError:
            size = "tamanho indisponível"
        kind = label or self.artifact_type_label(path)
        self.artifact_list.insert(tk.END, f"{kind}  ·  {size}  ·  {display_path}")

    def show_artifact_preview(self, _event=None):
        selection = self.artifact_list.curselection()
        if not selection or selection[0] >= len(self.artifacts):
            return
        path = self.artifacts[selection[0]]
        try:
            metadata = path.stat()
            details = (f"{self.artifact_type_label(path)}\n{self._format_storage_size(metadata.st_size)}\n"
                       f"{self.tr('Alterado em')} "
                       f"{self._format_record_datetime(datetime.fromtimestamp(metadata.st_mtime))}")
        except OSError:
            details = f"{self.artifact_type_label(path)}\nMetadados indisponíveis"
        self.artifact_preview_var.set(details)
        self.artifact_preview_image = None
        self.artifact_thumbnail.configure(image="", text=self.artifact_type_label(path))
        if Image and ImageTk and path.suffix.lower() in {".png", ".jpg", ".jpeg", ".webp", ".bmp"}:
            try:
                with Image.open(path) as source:
                    preview = source.copy()
                preview.thumbnail((205, 105))
                self.artifact_preview_image = ImageTk.PhotoImage(preview)
                self.artifact_thumbnail.configure(image=self.artifact_preview_image, text="")
            except (OSError, ValueError):
                pass

    def open_selected_artifact(self):
        selection = self.artifact_list.curselection()
        if not selection:
            return messagebox.showinfo("Arquivo", "Selecione um arquivo da lista.")
        path = self.artifacts[selection[0]]
        try:
            if path.suffix.lower() in {".md", ".txt", ".csv", ".json", ".py", ".html", ".css", ".js"}:
                subprocess.Popen(["notepad.exe", str(path)])
            else:
                os.startfile(path)
        except OSError as exc:
            messagebox.showerror("Não foi possível abrir o arquivo", str(exc))

    def append_log(self, line):
        lowered = line.lower()
        if "apply patch" in lowered or "patch:" in lowered:
            self.phase_var.set("Aplicando alterações")
            self.simple_progress_var.set("O Codex está aplicando alterações na pasta da tarefa.")
        elif "exec" in lowered:
            self.phase_var.set("Executando ferramenta")
            self.simple_progress_var.set("O Codex está executando uma etapa da tarefa.")
        elif "codex" in lowered:
            self.phase_var.set("Codex processando a tarefa")
            self.simple_progress_var.set("O Codex está analisando e produzindo o resultado.")
        self.log.configure(state="normal")
        self.log.insert(tk.END, line)
        self.log.see(tk.END)
        self.log.configure(state="disabled")

    def clear_log(self):
        self.log.configure(state="normal")
        self.log.delete("1.0", tk.END)
        self.log.configure(state="disabled")

    @staticmethod
    def format_duration(seconds):
        seconds = max(0, int(seconds))
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def update_progress(self):
        if not self.running or self.execution_started_monotonic is None:
            return
        elapsed = max(0, round(clock.monotonic() -
                      self.execution_started_monotonic))
        self.elapsed_var.set("Tempo decorrido: " +
                             self.format_duration(elapsed))
        if (self.active_process and not self.cancel_requested and
                elapsed >= 30 and elapsed % 30 == 0):
            self.simple_progress_var.set(
                "O Codex continua em execução há " + self.format_duration(elapsed) +
                ". Você pode cancelar se não quiser esperar.")
        if self.estimated_total_seconds and elapsed < self.estimated_total_seconds:
            remaining = max(0, self.estimated_total_seconds - elapsed)
            value = min(
                95, round(elapsed / self.estimated_total_seconds * 100))
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate", value=value)
            self.remaining_var.set("Tempo restante estimado: " + self.format_duration(
                remaining) + "\nBaseado em execuções anteriores semelhantes.")
        else:
            self.progress_bar.configure(mode="indeterminate")
            self.progress_bar.start(12)
            self.remaining_var.set(
                "Tempo restante: estimativa ultrapassada; o Codex ainda está em execução."
                if self.estimated_total_seconds else
                "Tempo restante: sem histórico suficiente para estimar.")
        self.after(1000, self.update_progress)

    def set_controls(self, state):
        def change_state(control, desired):
            try:
                control.configure(state="readonly" if desired == "normal" and isinstance(control, ttk.Combobox) else desired)
            except tk.TclError as exc:
                self.note_startup_step(
                    f"Aviso em controle da interface: {type(exc).__name__}: {exc}")

        for control in (self.cli_check_button, self.cli_release_button, self.choose_button, self.open_folder_button, self.open_gate_data_button, self.backup_button, self.restore_backup_button, self.choose_skill_library_button, self.open_skill_library_button, self.library_refresh_button, self.refresh_button, self.recommend_button, self.run_button, self.schedule_button, self.policy_box, self.model_box, self.legacy_model_box, self.effort_box, self.manual_skills_toggle, self.open_active_skill_button, self.install_active_skill_button, self.add_active_skill_button, self.remove_active_skill_button, self.skill_library_entry, self.skill_search_entry, self.clear_skill_search_button, self.add_attachment_button, self.remove_attachment_button, self.open_attachment_button, self.advanced_mode_toggle, self.template_box, self.browser_research_toggle, self.browser_query_entry):
            change_state(control, state)
        change_state(self.language_box, state)
        self._sync_browser_query_state()
        change_state(self.path_entry, state)
        change_state(self.task, state)
        change_state(self.skill_list, state)
        change_state(self.attachment_list, state)
        change_state(self.continue_pending_button,
            "normal" if state == "normal" and self.pending_question and
            (self.current_session_id or self.pending and self.pending.get("new_session")) else "disabled")
        change_state(self.cancel_button,
            "normal" if state == "disabled" and (self.running or self.selecting_skills) else "disabled")

    def present_finished_run(self, returncode, output, session_id=None, raw_output=""):
        self.note_startup_step(f"Processo encerrado com código {returncode}")
        self.running = False
        self.active_process = None
        if session_id:
            self.current_session_id = session_id
            self.pending["new_session"] = False
        rejected_model = gate.cli_rejected_model(raw_output or output) if returncode else None
        if rejected_model and raw_output:
            output = raw_output
        if rejected_model:
            self.current_session_id = None
        compatibility_message = gate.cli_model_compatibility_message(
            self.cli_executable, rejected_model, self.cli_version) if rejected_model else None
        rejected_message = self.tr(
            "O Codex CLI recusou {model}. Confira a versão do CLI, a autenticação e a disponibilidade do modelo nesse cliente. O Gate não altera o modelo autorizado automaticamente.")
        display_output = (self.tr(compatibility_message) or
                          rejected_message.format(model=rejected_model.capitalize())
                          if rejected_model else output)
        try:
            self.show_response(display_output, select=True)
            self.update_idletasks()
        except Exception as exc:
            self.note_startup_step(f"Aviso ao mostrar resposta: {type(exc).__name__}: {exc}")
        try:
            self.current_token_usage = gate.extract_codex_token_usage(raw_output)
            self.update_consumption_display()
            self.set_controls("normal")
        except Exception as exc:
            self.note_startup_step(f"Aviso ao restaurar interface: {type(exc).__name__}: {exc}")
        self.artifacts = self._completion_data['artifacts']
        self.clear_artifact_display()
        for path in self.artifacts:
            self.add_artifact_display(path)

        if self.execution_started_monotonic is not None:
            self.execution_duration_seconds = max(
                1, round(clock.monotonic() - self.execution_started_monotonic))
        try:
            self.progress_bar.stop()
            self.progress_bar.configure(mode="determinate", value=0 if returncode else 100)
        except tk.TclError as exc:
            self.note_startup_step(f"Aviso na barra de progresso: {exc}")
        self.elapsed_var.set(
            "Tempo decorrido: " + self.format_duration(self.execution_duration_seconds or 0))
        self.remaining_var.set("Tempo restante: finalizado")
        self.phase_var.set("Falhou" if returncode else "Salvando registro")
        if returncode:
            result_label = "Cancelada" if self.cancel_requested else "Falhou"
            self.status.set(
                f"Execução {result_label.lower()} (código {returncode}). Consulte o painel de andamento.")
            self.simple_progress_var.set(
                "Execução cancelada; os arquivos parciais foram preservados." if self.cancel_requested else "A execução falhou. Consulte os detalhes técnicos para entender o ocorrido.")
            self.add_history(result_label, output)
            self.save_execution_record(result_label, [], output)
            if self.continuation_in_flight and self.pending_question:
                self.continuation_in_flight = False
                self.status.set(
                    "A resposta foi enviada, mas o Codex não concluiu a retomada. "
                    "Revise e tente novamente quando estiver pronto.")
                self.simple_progress_var.set(
                    "A pergunta e sua resposta foram preservadas para uma nova tentativa explícita.")
                self.show_continuation_window()
            if self.cancel_requested:
                return messagebox.showinfo("Execução cancelada", "A execução foi encerrada. Os arquivos parciais permanecem na pasta da tarefa.")
            if rejected_model:
                self.status.set(display_output)
                self.simple_progress_var.set(display_output)
                return messagebox.showerror("Falha do Codex CLI", display_output)
            return messagebox.showerror("Falha na execução", output[-3000:] or "O Codex não retornou detalhes.")

        self.continuation_in_flight = False
        if self.sent_continuation_message:
            now = datetime.now().astimezone().isoformat(timespec="seconds")
            self.conversation_turns.extend([
                {"role": "user", "text": self.sent_continuation_message, "at": now},
                {"role": "assistant", "text": output, "at": now},
            ])
            self.conversation_turns = gate.normalize_conversation_turns(
                self.conversation_turns)
            self.sent_continuation_message = ""
        question = gate.extract_continuation_question(output)
        if question and self.current_session_id:
            self.pending_question = question
            self.continuation_mode = "question"
            self.last_continuation_answer = ""
            try:
                gate.save_continuation_state(self.cwd, self.continuation_state(question))
            except (OSError, ValueError) as exc:
                self.append_log(
                    f"Não foi possível salvar a continuação da tarefa: {exc}\n")
                self.pending_question = None
                self.last_continuation_answer = ""
                self.set_controls("normal")
                return messagebox.showerror(
                    "Continuação indisponível",
                    "O Codex fez uma pergunta, mas o estado da tarefa não pôde ser salvo. "
                    "A pergunta continua no log técnico.")
            self.status.set("O Codex aguarda sua resposta para continuar esta mesma tarefa.")
            self.simple_progress_var.set(
                "Resposta necessária. A continuação preservará a sessão e a pasta da tarefa.")
            self.phase_var.set("Aguardando sua resposta")
            self.add_history("Aguardando resposta", output)
            self.save_execution_record("Aguardando resposta", [], output)
            if not self.busy_operation:
                self.set_controls("normal")
                self.show_continuation_window()
            return
        if question and not self.current_session_id:
            self.append_log(
                "O Codex fez uma pergunta, mas esta versão do CLI não informou o identificador da sessão. "
                "A pergunta ficou registrada no log e a tarefa não foi retomada automaticamente.\n")
        self.pending_question = None
        self.last_continuation_answer = ""
        gate.clear_continuation_state(self.cwd)
        self.close_continuation_window()
        self.set_controls("normal")
        installed_skills = self._completion_data['installed']
        validation = self._completion_data['validation']
        if installed_skills:
            self.refresh_skills()
        if validation:
            self.phase_var.set("Revisão necessária")
            self.status.set(
                "Execução finalizada, mas há itens que precisam de revisão antes de considerar a tarefa concluída.")
            self.simple_progress_var.set("Resultado gerado, mas precisa de revisão antes de ser aprovado.")
            self.add_history("Revisão necessária", output, validation)
            self.save_execution_record(
                "Revisão necessária", validation, output)
            return messagebox.showwarning("Validação de documento", "\n".join(validation))
        self.phase_var.set("Salvando registro")
        self.status.set(
            "Execução concluída com sucesso. Confira os arquivos e registre a qualidade do resultado.")
        self.simple_progress_var.set("Concluído. Abra os arquivos gerados e registre sua avaliação do resultado.")
        self.add_history("Concluída", output)
        self.save_execution_record("Concluída", [], output)


    def start_job(self, label, work, complete, exclusive=False):
        self.pending_jobs += 1
        if exclusive:
            self.exclusive_jobs += 1
            self.busy_operation = True
            self.set_controls('disabled')
        def run():
            try:
                result = work()
                error = None
            except Exception as exc:
                result, error = None, exc
            self.events.put(('job_done', label, complete, result, error, exclusive))
        threading.Thread(target=run, daemon=True).start()

    def finish_job(self, event):
        _, label, callback, result, error, exclusive = event
        self.pending_jobs -= 1
        if exclusive:
            self.exclusive_jobs -= 1
            self.busy_operation = self.exclusive_jobs > 0
        if error:
            if label == 'Seleção inteligente':
                self.selecting_skills = False
                self.pending = None
                self.status.set(f'Análise não concluída: {error}. Pode tentar novamente ou usar a seleção manual.')
                self.simple_progress_var.set('A seleção inteligente não foi concluída.')
            if label == 'Consultar novas versões':
                self.cli_status_var.set('Consulta indisponível. Use Download / atualização oficial para conferir as versões.')
            if label == 'Salvar registro':
                self.phase_var.set('Falha ao salvar registro')
                self.status.set(f'Resultado disponível, mas o registro não foi salvo: {error}')
            if label in {'Preparação da tarefa', 'Validação da tarefa'}:
                self.running = False
                self.phase_var.set('Cancelada' if self.cancel_requested else 'Falhou')
                self.simple_progress_var.set(str(error))
            if not self.running and not self.busy_operation:
                self.set_controls('normal')
            messagebox.showerror(label, str(error))
            return
        try:
            callback(result)
        finally:
            if not self.running and not self.busy_operation:
                self.set_controls('normal')
                if hasattr(self, '_deferred_cli_status'):
                    result = self._deferred_cli_status
                    del self._deferred_cli_status
                    self.apply_cli_status(result)

    def check_cli_updates(self):
        self.cli_status_var.set('Consultando changelog oficial...')
        def present(latest):
            version = '.'.join(map(str, latest))
            installed = '.'.join(map(str, self.cli_version)) if self.cli_version else 'não identificada'
            message = f'CLI instalado: {installed}. Última versão estável no changelog: {version}.'
            if self.cli_version and latest > self.cli_version:
                message += ' Atualização disponível: use Download / atualização oficial.'
            self.cli_status_var.set(message)
        self.start_job('Consultar novas versões', latest_cli_release, present)

    def sync_decision_settings(self, _event=None):
        if not self.pending:
            return
        key = model_key(self.model_var.get())
        effort_label = gate_i18n.source_text(self.effort_var.get(), self.language)
        effort = next((k for k, v in gate.EFFORT_LABELS.items() if v == effort_label), None)
        policy = gate_i18n.source_text(self.policy_var.get(), self.language)
        if key not in gate.MODELS or not effort or policy not in gate.POLICIES:
            return
        self.pending.update(model=key, effort=effort, policy=policy)
        self.decision_model_card_var.set(model_label(key))
        self.decision_effort_card_var.set(self.tr(gate.EFFORT_LABELS[effort]))
        assessment = self.pending.get('assessment')
        if assessment:
            recommended = model_label(str(self.pending.get('recommended_model', self.pending['model'])))
            recommended_effort = self.pending.get('recommended_effort', self.pending['effort'])
            self.decision_text.set(f"Recomendado: {recommended} — {gate.EFFORT_LABELS[recommended_effort]}.\n"
                                   f"Selecionado: {model_label(key)} — {gate.EFFORT_LABELS[effort]}.\n"
                                   + gate.decision_summary(assessment, policy))

    def save_draft(self):
        gate.save_app_settings({'draft': {'task':self.task.get('1.0', tk.END).strip(),
            'attachments':[str(p) for p in self.attachments], 'root':self.path_var.get()}})

    def copy_response(self):
        self.clipboard_clear()
        self.clipboard_append(self.last_response_text)

    def export_response(self):
        destination = filedialog.asksaveasfilename(defaultextension='.md', filetypes=[('Markdown','*.md'),('Texto','*.txt')])
        if destination:
            atomic_write_text(Path(destination), self.last_response_text)

    def open_diagnostics(self):
        if self.pending and self.pending.get('project_folder'):
            folder = gate.gate_dir(Path(self.pending['project_folder']))
            os.startfile(folder)

    def on_close(self):
        if self.running or self.selecting_skills or self.busy_operation:
            return messagebox.showinfo("Atividade em andamento", "Aguarde a análise ou a execução terminar antes de fechar o Codex Model Gate.")
        self.save_draft()
        self.destroy()


if __name__ == "__main__":
    if "--mcp-browser-server" in sys.argv:
        from gate_browser_mcp import run_server
        run_server()
    else:
        GateApp().mainloop()
