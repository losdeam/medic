#!/usr/bin/env python3
import subprocess
import sys
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
NAME = "简易病例记录系统"

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
    print(f"[*] Platform: {sys.platform}")
    print(f"[*] Cleaning previous builds...")
    for d in [DIST_DIR, BUILD_DIR]:
        if d.exists():
            shutil.rmtree(d)

    pyi_args = [
        sys.executable, "-m", "PyInstaller",
        "--clean", "--noconfirm", "--onefile",
        "--name", NAME,
        "--collect-data", "gradio",
        "--collect-binaries", "gradio",
    ]

    for mod in EXCLUDES:
        pyi_args.extend(["--exclude-module", mod])

    for imp in HIDDEN_IMPORTS:
        pyi_args.extend(["--hidden-import", imp])

    pyi_args.append(str(PROJECT_ROOT / "main.py"))

    print(f"[*] Running PyInstaller...")
    result = subprocess.run(pyi_args, cwd=str(PROJECT_ROOT))

    if result.returncode != 0:
        print("[!] Build failed!")
        sys.exit(result.returncode)

    exe = None
    if sys.platform == "win32":
        candidate = DIST_DIR / f"{NAME}.exe"
    else:
        candidate = DIST_DIR / NAME

    if candidate.exists():
        exe = candidate

    if exe:
        size_mb = exe.stat().st_size / (1024 * 1024)
        print(f"\n[OK] Build successful: {exe.name} ({size_mb:.1f} MB)")
        print(f"\nUsage:")
        print(f"  1. Copy '{exe.name}' to the target computer")
        print(f"  2. Run it, then open http://localhost:8501 in browser")
        print(f"  3. Data is stored in medical_records.db in the same directory")
    else:
        print("[!] Could not find output executable in dist/")
        for f in DIST_DIR.rglob("*"):
            print(f"   {f}")
        sys.exit(1)


if __name__ == "__main__":
    build()
