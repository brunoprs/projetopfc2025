@echo off
cls
echo.
echo ==========================================
echo  INICIANDO PIFLOOR
echo ==========================================
echo.

echo Iniciando Backend...
cd backend
start "Backend Flask" cmd /k "venv\Scripts\activate && python run.py"
cd ..

timeout /t 2 /nobreak >nul

echo Iniciando Frontend...
cd frontend
start "Frontend React" cmd /k "pnpm dev"
cd ..

echo.
echo ==========================================
echo  SERVIDORES INICIADOS!
echo ==========================================
echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Abrindo navegador...
timeout /t 3 /nobreak >nul
start http://localhost:5173

echo.
echo Feche esta janela quando terminar.
pause

