@echo off
setlocal

:: 设置当前目录为脚本所在目录
cd /d "%~dp0"

:: =========================================
:: 1. 启动后端服务 (Uvicorn)
:: =========================================
if not exist ".\agent_all" (
    echo [ERROR] Backend directory ".\agent_all" not found.
    pause
    exit /b
)
cd /d ".\agent_all"
start "Backend Server (Uvicorn)" cmd /k "uvicorn main:app --reload --log-level debug"
echo [OK] Backend server started.

:: 回到脚本根目录
cd /d "%~dp0"

:: =========================================
:: 2. 启动前端服务 (npm run dev)
:: =========================================
if not exist ".\frontend\ai_teaching" (
    echo [ERROR] Frontend directory ".\frontend\ai_teaching" not found.
    pause
    exit /b
)
cd /d ".\frontend\ai_teaching"
start "Frontend Server (npm)" cmd /k "npm run dev"
echo [OK] Frontend server started.

:: =========================================
:: 3. 检查 Ollama 是否安装
:: =========================================
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Ollama is not installed. Please download and install it:
    echo     https://ollama.com/download
    pause
    exit /b
) else (
    echo [OK] Ollama is installed.
)

:: =========================================
:: 4. 启动 Ollama 服务
:: =========================================
start "Ollama Service" cmd /k "ollama serve"
if errorlevel 1 (
    echo [ERROR] Failed to start Ollama service. Make sure the model is downloaded and Ollama is correctly installed.
    pause
    exit /b
) else (
    echo [OK] Ollama service started.
)

:: =========================================
:: 5. 等待服务启动
:: =========================================
timeout /t 3 /nobreak >nul

:: =========================================
:: 6. 打开浏览器访问前端 URL
:: =========================================
start http://localhost:5173
echo [OK] Browser opened at http://localhost:5173

pause
endlocal
