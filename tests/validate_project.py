"""Source-level validation; run in a venv containing hub/student requirements and PyYAML."""
from pathlib import Path
from types import SimpleNamespace
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest

import nbformat
from nbclient import NotebookClient
import yaml
from traitlets.config.loader import PyFileConfigLoader
from jupyterhub.app import JupyterHub
from jupyterhub.auth import Authenticator
from jupyterhub.orm import new_session_factory
from dockerspawner import DockerSpawner
from nativeauthenticator import NativeAuthenticator

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("start_student", ROOT / "student/start_student.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ClassroomTests(unittest.TestCase):
    def test_compose_offline_policy(self):
        compose = yaml.safe_load((ROOT / "compose.yaml").read_text())
        for service in compose["services"].values():
            self.assertEqual(service["pull_policy"], "never")
        self.assertEqual(compose["services"]["student-image"]["profiles"], ["build"])
        self.assertEqual(compose["networks"]["classroom"]["name"], "offline-ml-network")

    def test_real_hub_config(self):
        config = PyFileConfigLoader("jupyterhub_config.py", str(ROOT / "hub")).load_config()
        for cls in [JupyterHub, DockerSpawner, NativeAuthenticator, Authenticator]:
            self.assertFalse(set(config.get(cls.__name__, {})) - set(cls.class_traits(config=True)))
        hub = JupyterHub(config=config)
        self.assertEqual(hub.authenticator_class, NativeAuthenticator)
        spawner = DockerSpawner(config=config, user=SimpleNamespace(name="student01"))
        self.assertEqual(spawner.pull_policy, "never")
        self.assertEqual(spawner.network_name, "offline-ml-network")
        self.assertEqual(spawner.mem_limit, 2 * 1024**3)
        self.assertEqual(spawner.cpu_limit, 1)
        self.assertEqual(spawner.volumes["offline-ml-work-{username}"], "/home/student/work")
        factory = new_session_factory("sqlite:///:memory:")
        auth = NativeAuthenticator(config=config, db=factory())
        self.assertFalse(auth.open_signup)
        self.assertFalse(auth.ask_email_on_signup)
        self.assertIn("instructor", auth.admin_users)

    def test_hub_versions_match(self):
        def version(path):
            return next(line for line in path.read_text().splitlines() if line.startswith("jupyterhub=="))
        self.assertEqual(version(ROOT / "hub/requirements.txt"), version(ROOT / "student/requirements.txt"))

    def test_seed_preserves_saved_work_and_adds_missing_files(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source, workspace, datasets = base / "source", base / "work", base / "data"
            (source / "class-1").mkdir(parents=True)
            datasets.mkdir()
            (source / "class-1/a.ipynb").write_text("original")
            self.assertEqual(module.seed_workspace(source, workspace, datasets), 1)
            saved = workspace / "class-1/a.ipynb"
            saved.write_text("student edit")
            (source / "class-1/a.ipynb").write_text("instructor revision")
            (source / "class-1/b.ipynb").write_text("new exercise")
            self.assertEqual(module.seed_workspace(source, workspace, datasets), 1)
            self.assertEqual(saved.read_text(), "student edit")
            self.assertEqual((workspace / "class-1/b.ipynb").read_text(), "new exercise")
            self.assertEqual((workspace / "datasets").resolve(), datasets.resolve())
            self.assertEqual(module.seed_workspace(source, workspace, datasets), 0)

    def test_notebooks_execute(self):
        with tempfile.TemporaryDirectory() as directory:
            workspace = Path(directory)
            module.seed_workspace(ROOT / "courses", workspace, ROOT / "datasets")
            notebooks = sorted(workspace.rglob("*.ipynb"))
            self.assertEqual(len(notebooks), 4)
            for path in notebooks:
                with self.subTest(notebook=path.name):
                    nb = nbformat.read(path, as_version=4)
                    nbformat.validate(nb)
                    if os.environ.get("CLASSROOM_VALIDATE_IN_PROCESS") == "1":
                        # Restricted validation hosts may block kernel sockets.
                        # The image's check_environment.py always uses real kernels.
                        previous = Path.cwd()
                        namespace = {"__name__": "__main__"}
                        try:
                            os.chdir(path.parent)
                            for cell in nb.cells:
                                if cell.cell_type == "code":
                                    exec(compile(cell.source, path.name, "exec"), namespace)
                        finally:
                            os.chdir(previous)
                    else:
                        NotebookClient(nb, timeout=120, kernel_name="python3",
                                       resources={"metadata": {"path": str(path.parent)}}).execute()

    def test_shell_syntax(self):
        for path in (ROOT / "scripts").glob("*.sh"):
            subprocess.run(["bash", "-n", str(path)], check=True)

    def test_python_and_json_syntax(self):
        for path in ROOT.rglob("*.py"):
            compile(path.read_text(), str(path), "exec")
        json.loads((ROOT / "student/overrides.json").read_text())


if __name__ == "__main__":
    unittest.main(verbosity=2)
