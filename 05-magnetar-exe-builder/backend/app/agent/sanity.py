import os
from .utils import run_cmd

def run_sanity_check(run_dir: str):
    main_py_path = os.path.join(run_dir, "src", "main.py")
    if not os.path.exists(main_py_path):
        return False, "src/main.py does not exist."
    
    rc, out, err = run_cmd("python -m py_compile src/main.py", cwd=run_dir, timeout=120)
    if rc != 0:
        return False, (err or out)[:1500]
    return True, "Sanity check passed (python -m py_compile src/main.py successful)."
