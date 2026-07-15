#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"
WINEPREFIX="${WINEPREFIX:-$HOME/.wine-medic}"
PYTHON_VER="3.11.9"
PYTHON_URL="https://www.python.org/ftp/python/${PYTHON_VER}/python-${PYTHON_VER}-embed-amd64.zip"
VC_REDIST_URL="https://aka.ms/vs/17/release/vc_redist.x64.exe"

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  简易病例记录系统 - Ubuntu 交叉打包工具${NC}"
echo -e "${GREEN}============================================${NC}"

if ! command -v wine &>/dev/null; then
    echo -e "${YELLOW}[1/8] 安装 Wine 9.0...${NC}"
    apt-get update -qq && apt-get install -y -qq wine64 wine cabextract xvfb 2>&1 | tail -3
fi
echo -e "${GREEN}[1/8] Wine $(wine --version 2>/dev/null || echo '?') 已就绪${NC}"

echo -e "${YELLOW}[2/8] 初始化 Wine 环境...${NC}"
rm -rf "$WINEPREFIX"
export WINEPREFIX
WINEARCH=win64 WINEDLLOVERRIDES="mscoree,mshtml=" wine wineboot 2>/dev/null || true
wine reg add "HKEY_CURRENT_USER\\Software\\Wine" /v Version /d win10 /f 2>/dev/null || true

echo -e "${YELLOW}[3/8] 下载 Windows Python ${PYTHON_VER}...${NC}"
PYTHON_DIR="$WINEPREFIX/drive_c/Python311"
mkdir -p "$PYTHON_DIR"
TMP_ZIP="/tmp/python-embed-$$.zip"
wget -q "$PYTHON_URL" -O "$TMP_ZIP" 2>&1 || curl -kfsSL "$PYTHON_URL" -o "$TMP_ZIP"
unzip -o -q "$TMP_ZIP" -d "$PYTHON_DIR"
rm -f "$TMP_ZIP"

cat > "$PYTHON_DIR/python311._pth" << 'PYTHONPATH'
python311.zip
.
Lib
Lib/site-packages
import site
PYTHONPATH

echo -e "${YELLOW}[4/8] 安装 pip...${NC}"
wget -q "https://bootstrap.pypa.io/get-pip.py" -O /tmp/get-pip-$$.py 2>&1 || \
    curl -kfsSL "https://bootstrap.pypa.io/get-pip.py" -o /tmp/get-pip-$$.py
xvfb-run -a wine "C:/Python311/python.exe" /tmp/get-pip-$$.py --no-warn-script-location 2>&1 | grep -v "^$" | tail -3
rm -f /tmp/get-pip-$$.py

echo -e "${YELLOW}[5/8] 安装 VC++ Redist...${NC}"
wget -q "$VC_REDIST_URL" -O /tmp/vc_redist-$$.exe 2>&1 || \
    curl -kfsSL "$VC_REDIST_URL" -o /tmp/vc_redist-$$.exe

rm -rf /tmp/vcrt-$$ /tmp/ucrt-$$
mkdir -p /tmp/vcrt-$$ /tmp/ucrt-$$
cabextract -q -d /tmp/vcrt-$$ /tmp/vc_redist-$$.exe 2>/dev/null

for f in /tmp/vcrt-$$/a*; do
    cabextract -q -d /tmp/ucrt-$$ "$f" 2>/dev/null || true
done

WINE_SYS32="$WINEPREFIX/drive_c/windows/system32"
if [ -f /tmp/ucrt-$$/ucrtbase.dll ]; then
    cp /tmp/ucrt-$$/ucrtbase.dll "$WINE_SYS32/"
    cp /tmp/ucrt-$$/api-ms-win-crt-*.dll "$WINE_SYS32/" 2>/dev/null || true
    cp /tmp/ucrt-$$/api_ms_win_crt-*.dll "$WINE_SYS32/" 2>/dev/null || true
    cp /tmp/ucrt-$$/vcruntime140.dll "$WINE_SYS32/" 2>/dev/null || true
fi

cat > /tmp/dll-override-$$.reg << REGEOF
REGEDIT4

[HKEY_CURRENT_USER\\Software\\Wine\\DllOverrides]
"ucrtbase"="native,builtin"
"api-ms-win-crt-runtime-l1-1-0"="native,builtin"
"api-ms-win-crt-math-l1-1-0"="native,builtin"
"api-ms-win-crt-convert-l1-1-0"="native,builtin"
"api-ms-win-crt-stdio-l1-1-0"="native,builtin"
"api-ms-win-crt-string-l1-1-0"="native,builtin"
"api-ms-win-crt-heap-l1-1-0"="native,builtin"
"api-ms-win-crt-environment-l1-1-0"="native,builtin"
"api-ms-win-crt-filesystem-l1-1-0"="native,builtin"
"api-ms-win-crt-time-l1-1-0"="native,builtin"
"api-ms-win-crt-locale-l1-1-0"="native,builtin"
"api-ms-win-crt-process-l1-1-0"="native,builtin"
"api-ms-win-crt-utility-l1-1-0"="native,builtin"
"api-ms-win-crt-multibyte-l1-1-0"="native,builtin"
"vcruntime140"="native,builtin"
REGEOF
xvfb-run -a wine regedit /tmp/dll-override-$$.reg 2>/dev/null || true

rm -rf /tmp/vcrt-$$ /tmp/ucrt-$$ /tmp/vc_redist-$$.exe /tmp/dll-override-$$.reg

echo -e "${YELLOW}      验证 numpy 兼容性...${NC}"
xvfb-run -a wine "C:/Python311/python.exe" -c "import numpy; print('NumPy', numpy.__version__)" 2>/dev/null || {
    echo -e "${RED}[错误] numpy 导入失败，ucrtbase 修复可能不完整${NC}"
    exit 1
}
echo -e "${GREEN}      NumPy 兼容性 OK${NC}"

echo -e "${YELLOW}[6/8] 安装项目依赖...${NC}"
PROJECT_WIN="$WINEPREFIX/drive_c/project"
rm -rf "$PROJECT_WIN"
mkdir -p "$PROJECT_WIN"
cp "$PROJECT_DIR/main.py" "$PROJECT_DIR/utils.py" "$PROJECT_WIN/"
cp -r "$PROJECT_DIR/page" "$PROJECT_WIN/"

xvfb-run -a wine "C:/Python311/python.exe" -m pip install -q pyinstaller gradio pandas openpyxl xlsxwriter 2>&1 | tail -3

echo -e "${YELLOW}[7/8] 打补丁 (gradio PyInstaller 兼容)...${NC}"
GRADIO_META="$WINEPREFIX/drive_c/Python311/Lib/site-packages/gradio/component_meta.py"
python3 -c "
with open('$GRADIO_META', 'r') as f:
    content = f.read()
old = '''    source_code = source_file.read_text(encoding=\"utf-8\")'''
new = '''    try:
        source_code = source_file.read_text(encoding=\"utf-8\")
    except Exception:
        return'''
content = content.replace(old, new)
with open('$GRADIO_META', 'w') as f:
    f.write(content)
"

echo -e "${YELLOW}[8/8] PyInstaller 打包中 (约需 1-2 分钟)...${NC}"

cat > "$PROJECT_WIN/build_win.py" << 'PYEOF'
import subprocess, sys, shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
NAME = "\u7b80\u6613\u75c5\u4f8b\u8bb0\u5f55\u7cfb\u7edf"

HIDDEN_IMPORTS = [
    "gradio.blocks", "gradio.components", "gradio.layouts",
    "gradio.themes", "gradio.themes.utils", "gradio.routes",
    "gradio.events", "gradio.helpers", "gradio.context",
    "gradio.utils", "gradio.processing_utils", "gradio.networking",
    "uvicorn.logging", "uvicorn.loops.auto",
    "uvicorn.protocols.http.auto", "uvicorn.protocols.websockets.auto",
    "uvicorn.lifespan.on", "pandas.io.formats.style",
    "openpyxl.cell._writer", "jinja2.ext",
]

EXCLUDES = [
    "tkinter", "matplotlib", "scipy", "IPython", "jupyter",
    "notebook", "ipykernel", "streamlit", "torch", "torchvision",
    "torchaudio", "tensorflow", "tensorboard", "sympy", "numba",
    "pytest", "setuptools", "pip", "wheel", "pkg_resources",
    "sqlalchemy", "psycopg2", "MySQLdb",
]

def build():
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            shutil.rmtree(d)

    pyi_args = [
        sys.executable, "-m", "PyInstaller",
        "--clean", "--noconfirm", "--onefile",
        "--name", NAME,
        "--collect-data", "gradio",
        "--collect-submodules", "gradio",
        "--collect-data", "safehttpx",
        "--collect-data", "groovy",
        "--add-data", "C:/Python311/Lib/site-packages/safehttpx/version.txt;safehttpx",
        "--add-data", "C:/Python311/Lib/site-packages/groovy/version.txt;groovy",
    ]

    for mod in EXCLUDES:
        pyi_args.extend(["--exclude-module", mod])

    for imp in HIDDEN_IMPORTS:
        pyi_args.extend(["--hidden-import", imp])

    pyi_args.append(str(PROJECT_ROOT / "main.py"))

    result = subprocess.run(pyi_args, cwd=str(PROJECT_ROOT))
    if result.returncode != 0:
        sys.exit(result.returncode)

    candidate = DIST_DIR / f"{NAME}.exe"
    if not candidate.exists():
        sys.exit(1)

if __name__ == "__main__":
    build()
PYEOF

xvfb-run -a wine "C:/Python311/python.exe" "C:/project/build_win.py" 2>&1 | grep -E "complete|ERROR|PKG" || true

OUTPUT_DIR="$PROJECT_DIR/dist"
mkdir -p "$OUTPUT_DIR"
cp "$PROJECT_WIN/dist/简易病例记录系统.exe" "$OUTPUT_DIR/" 2>/dev/null

if [ -f "$OUTPUT_DIR/简易病例记录系统.exe" ]; then
    SIZE=$(du -sh "$OUTPUT_DIR/简易病例记录系统.exe" | cut -f1)
    echo ""
    echo -e "${GREEN}============================================${NC}"
    echo -e "${GREEN}  打包成功!${NC}"
    echo -e "${GREEN}  输出: dist/简易病例记录系统.exe (${SIZE})${NC}"
    echo -e "${GREEN}============================================${NC}"
    echo ""
    echo "部署: 将 dist/简易病例记录系统.exe 复制到 Windows 电脑"
    echo "      双击运行，浏览器访问 http://localhost:8501"
else
    echo -e "${RED}打包失败，请检查上方日志${NC}"
    exit 1
fi

rm -rf "$PROJECT_WIN/build" "$PROJECT_WIN/dist" "$PROJECT_WIN/build_win.py"
