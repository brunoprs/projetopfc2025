@echo off
echo ========================================
echo   INICIANDO PROJETO PIFLOOR
echo ========================================
echo.

echo [1/2] Iniciando BACKEND (Flask)...
cd backend
start "PiFloor Backend" cmd /k "venv\Scripts\activate.bat && python run.py"
cd ..
echo OK: Backend iniciado em http://localhost:5000

timeout /t 3 /nobreak >nul

echo.
echo [2/2] Iniciando FRONTEND (React)...
cd frontend
start "PiFloor Frontend" cmd /k "pnpm dev"
cd ..
echo OK: Frontend iniciado em http://localhost:5173

echo.
echo ========================================
echo   PROJETO INICIADO COM SUCESSO!
echo ========================================
echo.
echo Backend: http://localhost:5000
echo Frontend: http://localhost:5173
echo.
echo Duas janelas foram abertas:
echo - Backend (servidor Flask)
echo - Frontend (servidor Vite)
echo.
echo Para parar os servidores, feche as janelas ou pressione Ctrl+C em cada uma.
echo.
echo Abrindo navegador em 5 segundos...
timeout /t 5 /nobreak >nul
start http://localhost:5173
echo.
pause

