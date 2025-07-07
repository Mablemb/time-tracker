@echo off
REM Script de inicialização para Windows - TimeTracker

REM Ativa o ambiente virtual ou cria se não existir
if not exist venv (
    echo Criando ambiente virtual Python...
    python -m venv venv
)

call venv\Scripts\activate

REM Instala dependências
if exist requirements.txt (
    echo Instalando dependências...
    pip install -r requirements.txt
)

REM Executa migrações
python manage.py migrate

REM Inicia o servidor Django
start "TimeTracker" cmd /c "python manage.py runserver"

REM Aguarda alguns segundos e abre o navegador
ping 127.0.0.1 -n 5 > nul
start http://127.0.0.1:8000

echo TimeTracker iniciado! Feche esta janela para encerrar.
pause
