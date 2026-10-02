@echo off
setlocal
cd /d "%~dp0"
echo Instalando o componente de validacao de PDF...
python -m pip install --user -r requirements.txt
if errorlevel 1 (
  echo.
  echo A instalacao nao foi concluida. Verifique se o Python esta instalado e conectado a internet.
) else (
  echo.
  echo Validacao de documentos instalada com sucesso.
)
pause
