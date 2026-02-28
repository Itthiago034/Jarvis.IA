@echo off
title Jarvis - Dev Mode
cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo ERRO: Ambiente virtual nao encontrado!
    pause
    exit
)

REM Limpa variavel de ambiente antiga para usar a do .env
set GOOGLE_API_KEY=

echo Ativando ambiente virtual...
call venv\Scripts\activate

echo ----------------------------
echo Iniciando Jarvis em modo DEV
echo ----------------------------

python agent.py dev

pause