@echo off
echo ========================================
echo   INSTALACAO DO PROJETO PIFLOOR
echo ========================================
echo.

REM ===================================
REM BACKEND
REM ===================================

echo ========================================
echo   BACKEND - Configuracao
echo ========================================
echo.

echo [1/6] Verificando Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado!
    echo Por favor, instale o Python 3.8 ou superior.
    echo Download: https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo OK: Python encontrado
echo.

echo [2/6] Navegando para pasta backend...
cd backend
if %errorlevel% neq 0 (
    echo ERRO: Pasta backend nao encontrada!
    pause
    exit /b 1
)
echo OK: Pasta backend encontrada
echo.

echo [3/6] Criando ambiente virtual Python...
if exist venv (
    echo Ambiente virtual ja existe, pulando criacao...
) else (
    python -m venv venv
    if %errorlevel% neq 0 (
        echo ERRO: Falha ao criar ambiente virtual
        pause
        exit /b 1
    )
    echo OK: Ambiente virtual criado
)
echo.

echo [4/6] Ativando ambiente virtual...
call venv\Scripts\activate.bat
if %errorlevel% neq 0 (
    echo ERRO: Falha ao ativar ambiente virtual
    pause
    exit /b 1
)
echo OK: Ambiente virtual ativado
echo.

echo [5/6] Atualizando pip...
python -m pip install --upgrade pip
echo OK: pip atualizado
echo.

echo [6/6] Instalando dependencias do backend...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias do backend
    pause
    exit /b 1
)
echo OK: Dependencias do backend instaladas
echo.

call venv\Scripts\deactivate.bat
cd ..

echo ========================================
echo   BACKEND - Configuracao Concluida!
echo ========================================
echo.

REM ===================================
REM FRONTEND
REM ===================================

echo ========================================
echo   FRONTEND - Configuracao
echo ========================================
echo.

echo [1/4] Verificando Node.js...
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Node.js nao encontrado!
    echo Por favor, instale o Node.js 18 ou superior.
    echo Download: https://nodejs.org/
    pause
    exit /b 1
)
node --version
echo OK: Node.js encontrado
echo.

echo [2/4] Navegando para pasta frontend...
cd frontend
if %errorlevel% neq 0 (
    echo ERRO: Pasta frontend nao encontrada!
    pause
    exit /b 1
)
echo OK: Pasta frontend encontrada
echo.

echo [3/4] Verificando gerenciador de pacotes...
pnpm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo pnpm nao encontrado, tentando instalar...
    npm install -g pnpm
    if %errorlevel% neq 0 (
        echo Aviso: Falha ao instalar pnpm, usando npm...
        set USE_NPM=1
    ) else (
        echo OK: pnpm instalado
        set USE_NPM=0
    )
) else (
    pnpm --version
    echo OK: pnpm encontrado
    set USE_NPM=0
)
echo.

echo [4/4] Instalando dependencias do frontend...
if %USE_NPM%==1 (
    echo Usando npm...
    npm install
    if %errorlevel% neq 0 (
        echo ERRO: Falha ao instalar dependencias do frontend
        pause
        exit /b 1
    )
) else (
    echo Usando pnpm...
    pnpm install
    if %errorlevel% neq 0 (
        echo ERRO: Falha ao instalar dependencias do frontend
        pause
        exit /b 1
    )
)
echo OK: Dependencias do frontend instaladas
echo.

cd ..

echo ========================================
echo   FRONTEND - Configuracao Concluida!
echo ========================================
echo.

REM ===================================
REM RESUMO FINAL
REM ===================================

echo ========================================
echo   INSTALACAO CONCLUIDA COM SUCESSO!
echo ========================================
echo.
echo Resumo da instalacao:
echo   [OK] Backend configurado (Python + venv + dependencias)
echo   [OK] Frontend configurado (Node.js + dependencias)
echo.
echo Proximos passos:
echo   1. Execute INICIAR.bat para iniciar o projeto
echo   2. Acesse http://localhost:5173 no navegador
echo.
echo Para rodar testes:
echo   cd backend
echo   venv\Scripts\activate
echo   pytest -q
echo.
pause
