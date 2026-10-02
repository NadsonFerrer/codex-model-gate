"""Typed task configuration and process supervision without GUI dependencies."""
from __future__ import annotations

import os
import subprocess
import threading
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class AuthorizedTask:
    identifier: str
    task: str
    projects_root: Path
    model: str
    effort: str
    policy: str
    attachments: tuple[Path, ...]
    browser: bool
    live_web: bool
    browser_query: str


def prepare_task(config: AuthorizedTask, skills, executable, cancelled):
    import codex_model_gate as g
    if cancelled.is_set():
        raise InterruptedError('Preparação cancelada.')
    workspace = g.execution_workspace(config.projects_root, config.identifier, config.task)
    g.remember_workspace(workspace)
    staged = g.stage_attachments(workspace, list(config.attachments), config.identifier, cancelled)
    fingerprints = g.skill_fingerprints(skills)
    instructions = g.selected_skill_instructions(skills)
    command = g.build_codex_exec_command(g.MODELS[config.model], config.effort,
                    workspace if config.browser else None, config.live_web, executable)
    if cancelled.is_set():
        raise InterruptedError('Preparação cancelada; arquivos parciais preservados.')
    return workspace, staged, fingerprints, instructions, command, g.snapshot_project_files(workspace)


class ProcessSupervisor:
    def __init__(self):
        self.cancelled = threading.Event()
        self.process = None
        self._job = None
        self._lock = threading.RLock()

    def _attach_job(self, process):
        if os.name != 'nt':
            return
        import ctypes
        from ctypes import wintypes as w
        class Basic(ctypes.Structure):
            _fields_ = [('ProcessTime', ctypes.c_int64), ('JobTime', ctypes.c_int64),
                        ('Flags', w.DWORD), ('MinWorkingSet', ctypes.c_size_t),
                        ('MaxWorkingSet', ctypes.c_size_t), ('ActiveLimit', w.DWORD),
                        ('Affinity', ctypes.c_size_t), ('Priority', w.DWORD), ('Scheduling', w.DWORD)]
        class IO(ctypes.Structure):
            _fields_ = [(name, ctypes.c_uint64) for name in ('ReadOps','WriteOps','OtherOps','ReadBytes','WriteBytes','OtherBytes')]
        class Limits(ctypes.Structure):
            _fields_ = [('Basic', Basic), ('IO', IO), ('ProcessMemory', ctypes.c_size_t),
                        ('JobMemory', ctypes.c_size_t), ('PeakProcess', ctypes.c_size_t), ('PeakJob', ctypes.c_size_t)]
        kernel = ctypes.WinDLL('kernel32', use_last_error=True)
        kernel.CreateJobObjectW.argtypes = [ctypes.c_void_p, w.LPCWSTR]
        kernel.CreateJobObjectW.restype = w.HANDLE
        kernel.SetInformationJobObject.argtypes = [w.HANDLE, ctypes.c_int, ctypes.c_void_p, w.DWORD]
        kernel.AssignProcessToJobObject.argtypes = [w.HANDLE, w.HANDLE]
        kernel.CloseHandle.argtypes = [w.HANDLE]
        handle = kernel.CreateJobObjectW(None, None)
        limits = Limits(); limits.Basic.Flags = 0x2000  # KILL_ON_JOB_CLOSE
        if handle and kernel.SetInformationJobObject(handle, 9, ctypes.byref(limits), ctypes.sizeof(limits)) and kernel.AssignProcessToJobObject(handle, w.HANDLE(int(process._handle))):
            self._job = (kernel, handle)
        elif handle:
            kernel.CloseHandle(handle)

    def cancel(self):
        self.cancelled.set()
        with self._lock:
            process = self.process
            if process and process.poll() is None:
                if self._job:
                    from ctypes import wintypes
                    kernel, handle = self._job
                    kernel.TerminateJobObject.argtypes = [wintypes.HANDLE, wintypes.UINT]
                    kernel.TerminateJobObject(handle, 1)
                elif os.name == 'nt':
                    subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                                   capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW, timeout=10)
                else:
                    import signal
                    try:
                        os.killpg(process.pid, signal.SIGTERM)
                    except ProcessLookupError:
                        pass

    def run(self, command, prompt, workspace, environment, on_log, on_started):
        import codex_model_gate as g
        if self.cancelled.is_set():
            return 1, None, 'Execução cancelada.', ''
        options = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {'start_new_session': True}
        process = subprocess.Popen(command, cwd=workspace, stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
                    encoding='utf-8', errors='replace', bufsize=1, env=environment, **options)
        with self._lock:
            self.process = process
            self._attach_job(process)
        stdout, stderr = [], []
        def reader(stream, collection):
            try:
                for line in stream:
                    collection.append(line)
                    display = g.codex_event_display_text(line)
                    if display:
                        on_log(display)
            finally:
                stream.close()
        readers = [threading.Thread(target=reader, args=(process.stdout, stdout), daemon=True),
                   threading.Thread(target=reader, args=(process.stderr, stderr), daemon=True)]
        for item in readers:
            item.start()
        try:
            on_started(process)
            if self.cancelled.is_set():
                self.cancel()
            try:
                process.stdin.write(prompt)
            except (OSError, BrokenPipeError):
                pass
            finally:
                process.stdin.close()
            result = process.wait()
        finally:
            with self._lock:
                if self._job:
                    kernel, handle = self._job
                    kernel.CloseHandle(handle); self._job = None
            if process.poll() is None:
                process.kill(); process.wait(timeout=5)
            for item in readers:
                item.join(timeout=5)
            self.process = None
        raw = ''.join(stdout)
        session, output = g.parse_codex_json_output(raw)
        diagnostics = ''.join(stderr)
        if result:
            output = output + ('\n' + diagnostics[-12000:] if diagnostics else '')
        if any(item.is_alive() for item in readers):
            result = result or 1
        return result, session, output or diagnostics, raw
