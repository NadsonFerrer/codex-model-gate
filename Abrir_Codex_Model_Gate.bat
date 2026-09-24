@echo off
setlocal
cd /d "%~dp0"
python codex_model_gate_gui.py
if errorlevel 1 (
  echo.
  echo Nao foi possivel abrir o Codex Model Gate. Verifique se o Python esta instalado.
  pause
)
