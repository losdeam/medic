@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

cd /d "%~dp0..\.."

echo ========================================
echo   简易病例记录系统 - Windows 打包工具
echo ========================================
echo.

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 Python，请先安装 Python 3.10+
    pause
    exit /b 1
)

echo [*] Python:
python --version

if exist _build_venv\ (
    echo [*] Removing old build venv...
    rmdir /s /q _build_venv
)

echo [*] Creating clean virtual environment...
python -m venv _build_venv
if %errorlevel% neq 0 (
    echo [错误] 创建虚拟环境失败
    pause
    exit /b 1
)

echo [*] Installing dependencies...
_build_venv\Scripts\python.exe -m pip install --upgrade pip -q
_build_venv\Scripts\python.exe -m pip install pyinstaller gradio pandas openpyxl xlsxwriter numpy -q
if %errorlevel% neq 0 (
    echo [错误] 依赖安装失败
    pause
    exit /b 1
)

echo [*] Building...
_build_venv\Scripts\python.exe scripts\build\build.py
if %errorlevel% neq 0 (
    echo [错误] 打包失败
    pause
    exit /b 1
)

echo [*] Cleaning up build venv...
rmdir /s /q _build_venv

echo.
echo ========================================
echo   打包成功!
echo   输出文件: dist\简易病例记录系统.exe
echo ========================================
echo.
echo 部署说明:
echo   1. 将 dist\简易病例记录系统.exe 复制到目标 Windows 电脑
echo   2. 双击运行，在弹出的控制台窗口中等待启动完成
echo   3. 打开浏览器访问 http://localhost:8501
echo   4. 所有数据保存在同目录下的 medical_records.db 中
echo.
pause
