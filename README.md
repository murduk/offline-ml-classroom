# Offline ML classroom with Docker

JupyterHub provides local logins and starts one private JupyterLab container per
student using DockerSpawner. Each student gets both classes, a persistent work
volume, a read-only dataset directory, and a CPU-based Python ML environment.
Students need only a browser on your Wi-Fi; computation runs on your host laptop.

**Internet is needed to build the images once. Serving the classroom needs no
internet, pip install, npm install, apt install, git clone, or image pulls.**
This download contains source/configuration, not prebuilt multi-gigabyte images.

## 1. Prepare while online

Install and start Docker Desktop (Mac/Windows) or Docker Engine plus the Compose
v2 plugin (Linux). Use Linux containers. On Windows, run the Bash scripts in WSL
with Docker integration enabled. Install and launch the Docker runtime while
online, including any first-run setup. Compose v2.20+ is recommended.

From this project directory:

```bash
cp .env.example .env
# Edit .env if desired: ADMIN_USER, memory/CPU limits, port, approval policy.
bash scripts/build-online.sh
```

The build installs all dependencies, packages Jupyter's web assets, copies your
courses/datasets into the student image, and runs every notebook in an isolated
test container with `--network none`. The test creates fresh copies and does not
touch student work. Kernel loopback communication still works.

Default packages: Python 3.12, JupyterLab, Notebook, NumPy, pandas, SciPy,
scikit-learn, Matplotlib, seaborn, statsmodels, ipywidgets, openpyxl, Pillow,
and notebook execution tools. pip itself is included. PyTorch/TensorFlow and
GPU acceleration are not configured in this starter.

Direct Python dependencies and the HTTP proxy version are pinned. Base image
tags, apt packages, and transitive dependencies can change between online builds.
For the exact same environment, distribute the saved built images rather than
rebuilding independently. The student image records `pip freeze` at
`/opt/classroom/installed-packages.txt`.

## 2. Add your two classes before the final build

| Local path | Purpose |
| --- | --- |
| `courses/class-1/` | First class's notebooks and supporting files |
| `courses/class-2/` | Second class's notebooks and supporting files |
| `datasets/` | Shared CSVs, images, pretrained models, and other resources |
| `student/requirements.txt` | All extra Python packages required by your course |
| `student/Dockerfile` | Extra operating-system dependencies if required |

Four small example notebooks are included: NumPy/pandas, classification,
regression, and clustering. They use bundled scikit-learn datasets or a local CSV.
Add as many notebooks as needed, then rerun `bash scripts/build-online.sh`.

From a notebook in `class-1` or `class-2`, load a shared file with:

```python
from pathlib import Path
import pandas as pd
data = pd.read_csv(Path("../datasets/housing-sample.csv"))
```

Each student sees editable copies of both course folders under their workspace.
`datasets` is a link to root-owned files baked into the image; students cannot
modify those originals. Copy a dataset into the workspace if an exercise needs
to edit it. Course originals also remain root-owned in `/opt/classroom/courses`.
New/missing course files are copied on each server start. Existing files are
never overwritten. For revised exercises, use a new filename or version folder;
otherwise an existing student's copy stays as they last saved it. Deleting a
seeded course file causes it to be restored at the next server start.

The classes are course folders, not separate access-controlled student cohorts.
If you need different dependencies, separate class enrollment, or different
permissions, that requires an additional configuration.

## 3. Start without internet

Disconnect the router's WAN/internet connection, but leave DHCP and Wi-Fi enabled.
Connect the hosting laptop to the router, preferably by Ethernet. Reserve a LAN
address for it, for example `192.168.1.10`.

```bash
bash scripts/start-offline.sh
docker compose ps
```

On the host, open `http://localhost:8000/hub/signup`. Register the username from
`ADMIN_USER` (default `instructor`) and choose your own password of at least ten
characters. The configured admin account is automatically authorized. Create
this account before inviting students to register. There is no default password.

Students join the same Wi-Fi and open:

```text
http://192.168.1.10:8000
```

Replace the IP with the hosting laptop's actual LAN IP. Students must not use
`localhost`; that refers to their own computer. Students register at `/hub/signup`.
The instructor logs in and approves their accounts at `/hub/authorize`. Approval
and login work offline. No email or external account is required. If you set
`OPEN_SIGNUP=true` in `.env`, registrations can log in without approval.

Configure router guest/client isolation so students can reach the host. Allow
the configured port through the laptop firewall. Keep the host awake and plugged
in. Devices may warn that Wi-Fi has no internet; they must stay connected anyway.
Allocate adequate memory/CPU to Docker Desktop or the Linux VM used by your
Docker runtime. The default per-student cap is 2 GB RAM and one CPU equivalent;
these caps do not reserve resources or guarantee capacity. Test your expected
number of concurrent learners with the actual exercises.

## 4. What enforces offline startup

| Setting | Behavior |
| --- | --- |
| Compose `pull_policy: never` | Uses only locally built/loaded images |
| Startup `--no-build --pull never` | Cannot trigger a build or registry pull |
| DockerSpawner `pull_policy = "never"` | New student sessions cannot pull an image |
| All installations in Dockerfile `RUN` steps | Nothing installs during startup |
| `PIP_NO_INDEX=1` in running containers | pip does not query package indexes by default |
| Local NativeAuthenticator | No internet authentication dependency |
| Bundled JupyterLab assets | Pages, scripts, styles, and standard math rendering served locally |
| Disabled JupyterLab news/update checks and extension manager | Avoids those external lookups |

This is offline-capable, not a container network firewall: student containers use
a normal Docker bridge so the Hub can reach them. If you reconnect the host to
internet, notebook code may access it. Docker's socket is available only to the
trusted Hub, not student containers. The Hub can control the Docker daemon.

Use dedicated classroom accounts and a trusted password-protected WLAN. This
starter uses local HTTP and a single shared hostname and is not an internet-facing
deployment hardened for hostile users. HTTPS and stronger isolation are separate
deployment steps if your teaching environment requires them.

## 5. Test before class

```bash
bash scripts/check-offline.sh
```

This executes the image's notebooks without external networking. Then, with the
WAN disconnected, test from a **fresh browser profile on a second device**:

1. Open login and signup pages; approve a new test account.
2. Start that student's server and check both class folders.
3. Execute all notebooks, including widgets, charts, and Markdown math.
4. Save an edit, stop the server from the Hub control panel, and start it again.
5. Check that the edit survives and a second account has its own private copy.

The Python execution check cannot detect browser-only remote resources in your
notebooks, such as remote images, map tiles, custom JavaScript/CDNs, or video.
Do not depend on runtime `pip install`, `fetch_openml`, `download=True`, public
CSV URLs, Hugging Face downloads, or online APIs. Bundle resources locally and
update notebook code to read local files before the final build.

## 6. Transfer the already-built environment to another laptop

While online, or any time after building:

```bash
bash scripts/export-images.sh classroom-images.tar
```

Transfer that archive plus this project folder and `.env` by USB. On the target
laptop with Docker already installed:

```bash
docker load -i classroom-images.tar
bash scripts/check-offline.sh
bash scripts/start-offline.sh
```

Images are built for your Docker host's CPU architecture. An Apple Silicon image
is not an Intel/AMD image: build/test on each required architecture while online.
Docker can emulate other architectures, but do not rely on that for classroom
capacity. Each laptop runs an independent Hub with its own IP, accounts, and
volumes. This setup does not balance sessions across laptops. Image exports
contain course materials and software, but **not existing accounts or student
work**; those are in Docker volumes.

## 7. Persistence, maintenance, and logs

| Docker volume | Data |
| --- | --- |
| `offline-ml-hub-data` | Local accounts, Hub state, and cookie secret |
| `offline-ml-work-<escaped-username>` | One student's notebooks, results, and saved files |

Only `/home/student/work` is persistent in student containers. Packages or files
manually added elsewhere in a running container disappear when it is replaced.
Back up volumes before deleting/resetting accounts, pruning volumes, or moving
to another laptop. Reusing an old username can expose the old workspace to the
new owner; handle account and volume lifecycle together. Do not run
`docker compose down -v` or volume-pruning commands on your classroom data.

Stop the Hub and its managed student servers gracefully, preserving volumes:

```bash
docker compose stop hub
```

Start again with `bash scripts/start-offline.sh`. For changes to `.env`, rerun the
start script to recreate the Hub. For changes to Dockerfiles, dependencies,
configurations, courses, or datasets, rebuild online, stop existing student
servers, and start the Hub again. Already-running student containers keep their
old image until stopped/recreated. DockerSpawner removes stopped student
containers, while their work volumes remain.

Diagnostics:

```bash
docker compose logs --tail=100 hub
docker ps --filter name=offline-ml-student
docker volume ls --filter name=offline-ml
```

For a specific running student container, substitute its actual name:

```bash
docker logs <student-container-name>
docker cp <student-container-name>:/home/student/work ./student-work-export
```

## Project files

| File | Purpose |
| --- | --- |
| `compose.yaml` | Runtime Hub, persistent data, network, and student image build target |
| `hub/Dockerfile` | Hub, local authenticator, DockerSpawner, and proxy |
| `hub/jupyterhub_config.py` | Accounts, networking, offline image policy, student limits |
| `student/Dockerfile` | Complete ML environment and bundled courses |
| `student/start_student.py` | Non-destructive initialization of private course copies |
| `scripts/build-online.sh` | Build both images and run isolated notebook checks |
| `scripts/start-offline.sh` | Fail-fast classroom startup without downloads |
| `scripts/check-offline.sh` | Package and notebook checks with no external networking |
| `scripts/export-images.sh` | Save both built images to a portable archive |

## Validation of this generated starter

See `VALIDATION.md` for checks completed before delivery and limitations. Run the
Docker build and offline acceptance steps above on the actual classroom laptop.

## Upstream references

- https://jupyterhub-dockerspawner.readthedocs.io/en/latest/
- https://jupyterhub-dockerspawner.readthedocs.io/en/latest/docker-image.html
- https://jupyterhub-dockerspawner.readthedocs.io/en/latest/api/index.html
- https://native-authenticator.readthedocs.io/en/latest/quickstart.html
- https://jupyterlab.readthedocs.io/en/4.4.x/user/announcements.html
- https://docs.docker.com/engine/storage/volumes/
