# Validation record

Checked before delivery:

- Installed the exact pinned Hub and student Python requirements into a fresh
  Python 3.12 virtual environment. `pip check` reported no broken requirements.
- Loaded the actual configuration using JupyterHub 5.3.0, DockerSpawner 14.0.0,
  and NativeAuthenticator 1.3.0. All configured trait names were recognized;
  image policy, network, volume, memory, CPU, and approval defaults were checked.
- Ran JupyterHub initialization with `--show-config`, a temporary cookie secret,
  and an in-memory database. Initialization completed successfully.
- Passed seven source-validation tests covering configuration, matching Hub
  versions, non-destructive workspace initialization, notebook code, Python/JSON
  syntax, and Bash syntax.
- Validated all four notebooks against the notebook schema and executed every
  code cell in order in a fresh namespace per notebook using the pinned packages.
  Example results: Iris test accuracy 0.895; regression MAE about USD 13,412 and
  R² 0.988; clustering silhouette 0.878. These are teaching examples, not targets
  for production models.
- Verified JupyterLab 4.4.6's actual settings schema accepts the disabled news
  and update settings, and its server resolves the NeverCheckForUpdate class.

Limitations:

- No Docker executable/engine was available in the generation environment.
  Docker image builds, Compose runtime, apt/npm installation, student spawning,
  browser interactions, and LAN access could not be exercised here.
- This environment blocks the sockets used by Jupyter kernels. The ordinary
  nbclient test was attempted but could not launch kernels for that reason;
  code cells were then executed directly. Direct execution does not verify
  kernel transport or browser rendering.
- Linux x86-64 Python dependencies were checked here. Build and test on the
  actual target laptop, especially for a different CPU architecture.

The project's online build script runs `scripts/check-offline.sh` automatically.
That check uses actual notebook kernels in a Docker container with `--network
none`, and fails if a notebook cannot execute. Complete that check and the
second-device/WAN-disconnected acceptance test in README.md before teaching.

Optional developer rerun in a prepared environment:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r hub/requirements.txt -r student/requirements.txt pyyaml
python -m ipykernel install --sys-prefix --name python3
python tests/validate_project.py
```

On a host that blocks kernel sockets, use
`CLASSROOM_VALIDATE_IN_PROCESS=1 MPLBACKEND=Agg python tests/validate_project.py`
for the explicitly limited direct-code check. The Docker offline acceptance
script always uses real kernels.
