@echo off
setlocal
:: Define o caminho do projeto (ajustado para ser relativo ao local do script)
set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

title INICIALIZADOR FINANCEIRO - DELAY 5 MIN
echo ==========================================================
echo    SISTEMA FINANCEIRO - INICIALIZACAO AUTOMATICA
echo ==========================================================
echo.
echo [!] Aguardando 5 minutos (300s) para garantir conexao...
timeout /t 300 /nobreak

echo.
echo [1/3] Verificando e Iniciando API Backend...
taskkill /F /IM python.exe >nul 2>&1
start "API_BACKEND" /min cmd /c "python main_api.py"

echo [2/3] Verificando e Iniciando Tunel Ngrok...
taskkill /F /IM ngrok.exe >nul 2>&1
start "TUNEL_NGROK" /min cmd /c "ngrok.exe http 8000 --url=noncongruous-chiffonade-bernarda.ngrok-free.dev"

echo [3/3] Verificando e Iniciando Frontend (Vite)...
cd frontend
start "FRONTEND_VITE" /min cmd /c "npm run dev"

echo.
echo ==========================================================
echo    AMBIENTE INICIALIZADO COM SUCESSO!
echo ==========================================================
echo O sistema esta rodando em segundo plano.
timeout /t 10
exit
