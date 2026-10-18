"""Execute every baked-in notebook with no external network (run via script)."""
from pathlib import Path
import importlib
import subprocess
import sys
import tempfile

import nbformat
from nbclient import NotebookClient
from start_student import seed_workspace


def main():
    # These are OS executables installed at image build time, not pip packages.
    for command in [["libreoffice", "--headless", "--version"],
                    ["ffmpeg", "-version"], ["ffprobe", "-version"]]:
        result = subprocess.run(command, check=True, capture_output=True, text=True, timeout=60)
        print(f"OK {command[0]}: {result.stdout.splitlines()[0]}", flush=True)
    for name in ["jupyterhub", "jupyterlab", "notebook", "ipykernel", "ipywidgets", "numpy",
                 "pandas", "scipy", "sklearn", "matplotlib", "seaborn", "statsmodels", "openpyxl", "PIL"]:
        module = importlib.import_module(name)
        print(f"OK {name}: {getattr(module, '__version__', 'installed')}", flush=True)
    subprocess.run([sys.executable, "-m", "pip", "check"], check=True)
    # A temporary workspace avoids touching any student's saved work.
    with tempfile.TemporaryDirectory(prefix="classroom-check-") as directory:
        workspace = Path(directory)
        seed_workspace(Path("/opt/classroom/courses"), workspace, Path("/opt/classroom/datasets"))
        notebooks = sorted(workspace.rglob("*.ipynb"))
        if not notebooks:
            raise RuntimeError("No course notebooks found in the image")
        for path in notebooks:
            print(f"Executing {path.relative_to(workspace)}", flush=True)
            nb = nbformat.read(path, as_version=4)
            nbformat.validate(nb)
            NotebookClient(nb, timeout=180, kernel_name="python3",
                           resources={"metadata": {"path": str(path.parent)}}).execute()
        print(f"PASS: {len(notebooks)} notebooks executed without external networking.", flush=True)


if __name__ == "__main__":
    main()
