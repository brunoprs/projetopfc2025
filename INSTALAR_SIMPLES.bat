@echo off
cls
echo.
echo ==========================================
echo  INSTALACAO PIFLOOR - VERSAO SIMPLIFICADA
echo ==========================================
echo.
echo Este script vai instalar todas as dependencias.
echo Aguarde, pode demorar alguns minutos...
echo.
pause

echo.
echo Instalando BACKEND...
cd backend
python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
call venv\Scripts\deactivate.bat
cd ..

echo.
echo Instalando FRONTEND...
cd frontend
call pnpm install
cd ..

echo.
echo ==========================================
echo  INSTALACAO CONCLUIDA!
echo ==========================================
echo.
echo Agora execute: INICIAR.bat
echo.
pause

