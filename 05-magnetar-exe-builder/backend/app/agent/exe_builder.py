import os
import shutil
import sys
import zipfile
from .utils import run_cmd, ensure_dir

def build_executable_in_code(run_dir: str, log_fn=None):
    """
    Directly compiles src/main.py into a standalone executable using PyInstaller in-code.
    """
    def _log(msg: str):
        if log_fn:
            log_fn(msg)
        print(f"[ExeBuilder] {msg}")

    _log("Starting in-code PyInstaller build engine...")

    src_main = os.path.join(run_dir, "src", "main.py")
    if not os.path.exists(src_main):
        raise RuntimeError("src/main.py not found in run directory.")

    req_file = os.path.join(run_dir, "requirements.txt")
    if os.path.exists(req_file):
        _log("Checking requirements.txt for optional dependency installation...")
        with open(req_file, "r", encoding="utf-8") as f:
            reqs = [line.strip() for line in f if line.strip() and not line.startswith("#")]
        if reqs:
            _log(f"Installing requirements: {', '.join(reqs)}")
            rc, out, err = run_cmd(f"{sys.executable} -m pip install " + " ".join(reqs), cwd=run_dir, timeout=300)
            if rc != 0:
                _log(f"Warning: pip install returned non-zero code: {err[:300]}")

    release_dir = os.path.join(run_dir, "release")
    build_dir = os.path.join(run_dir, "build_tmp")
    ensure_dir(release_dir)
    ensure_dir(build_dir)

    # Detect platform
    is_windows = sys.platform.startswith("win")
    exe_filename = "app.exe" if is_windows else "app"

    # Command line for PyInstaller
    cmd = (
        f"{sys.executable} -m PyInstaller "
        f"--noconfirm --clean --onefile "
        f"--name app "
        f"--distpath \"{release_dir}\" "
        f"--workpath \"{build_dir}\" "
        f"src/main.py"
    )

    _log(f"Executing: {cmd}")
    rc, out, err = run_cmd(cmd, cwd=run_dir, timeout=600)

    if rc != 0:
        _log(f"PyInstaller build stdout: {out[-800:]}")
        _log(f"PyInstaller build stderr: {err[-800:]}")
        raise RuntimeError(f"PyInstaller build failed with exit code {rc}:\n" + (err or out)[-1000:])

    _log("PyInstaller compilation completed successfully!")

    target_exe = os.path.join(release_dir, exe_filename)
    if not os.path.exists(target_exe):
        # Search release directory for any built file
        found_files = os.listdir(release_dir)
        if found_files:
            target_exe = os.path.join(release_dir, found_files[0])
        else:
            raise RuntimeError("Build succeeded but output binary was not found in release directory.")

    _log(f"Executable staged at: {target_exe} ({os.path.getsize(target_exe)} bytes)")
    return target_exe
