@echo off
echo ========================================
echo   INSTALACAO DO PROJETO PIFLOOR
echo ========================================
echo.

echo [1/4] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado! Por favor, instale o Python 3.8 ou superior.
    pause
    exit /b 1
)
echo OK: Python encontrado

echo.
echo [2/4] Instalando dependencias do BACKEND...
cd backend
if not exist venv (
    echo Criando ambiente virtual...
    python -m venv venv
)
call venv\Scripts\activate.bat
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias do backend
    pause
    exit /b 1
)
call venv\Scripts\deactivate.bat
cd ..
echo OK: Backend configurado

echo.
echo [3/4] Verificando Node.js e pnpm...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Node.js nao encontrado! Por favor, instale o Node.js 18 ou superior.
    pause
    exit /b 1
)
echo OK: Node.js encontrado

pnpm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Instalando pnpm...
    npm install -g pnpm
)
echo OK: pnpm encontrado

echo.
echo [4/4] Instalando dependencias do FRONTEND...
cd frontend
pnpm install
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias do frontend
    pause
    exit /b 1
)
cd ..
echo OK: Frontend configurado

echo.
echo ========================================
echo   INSTALACAO CONCLUIDA COM SUCESSO!
echo ========================================
echo.
echo Para iniciar o projeto, execute: INICIAR.bat
echo.
pause

