@echo off
REM Script de inicialização para Windows - TimeTracker

REM Detecta se deve usar py ou python
set PYTHON_CMD=py
where py >nul 2>nul
if errorlevel 1 (
    set PYTHON_CMD=python
    where python >nul 2>nul
    if errorlevel 1 (
        echo Python não encontrado! Instale o Python 3 e adicione ao PATH.
        pause
        exit /b 1
    )
)

REM Ativa o ambiente virtual ou cria se não existir
if not exist venv (
    echo Criando ambiente virtual Python...
    %PYTHON_CMD% -m venv venv
)

if not exist venv\Scripts\activate.bat (
    echo Falha ao criar o ambiente virtual! Verifique se o Python está instalado corretamente.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat

REM Instala dependências
if exist requirements.txt (
    echo Instalando dependências...
    pip install -r requirements.txt
)

REM Executa migrações
%PYTHON_CMD% manage.py migrate

REM Tenta iniciar o servidor na porta 8000, se falhar tenta 8080
set PORT=8000
start "TimeTracker" cmd /c "%PYTHON_CMD% manage.py runserver 8000"
ping 127.0.0.1 -n 5 > nul
REM Testa se a porta 8000 está respondendo
powershell -Command "try { (Invoke-WebRequest -UseBasicParsing http://127.0.0.1:8000).StatusCode } catch { exit 1 }"
if %ERRORLEVEL% neq 0 (
    echo Porta 8000 ocupada ou erro. Tentando na porta 8080...
    set PORT=8080
    start "TimeTracker" cmd /c "%PYTHON_CMD% manage.py runserver 8080"
    ping 127.0.0.1 -n 5 > nul
)

REM Abre o navegador na porta correta
start http://127.0.0.1:%PORT%
echo TimeTracker iniciado! O servidor está rodando em segundo plano.
pause
