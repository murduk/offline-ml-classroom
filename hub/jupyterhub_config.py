import os
import re

import nativeauthenticator

c = get_config()  # noqa: F821 -- provided by JupyterHub

# Paths in "source" refer to the hosting laptop.
courses_dir = os.environ["COURSES_DIR"]

c.DockerSpawner.mounts = [
    {
        "type": "bind",
        "source": courses_dir,
        "target": target,
        "read_only": True,
    }
    for target in [
        "/opt/classroom/courses",
        "/home/student/work/materials",
    ]
]

admin = os.environ.get("ADMIN_USER", "instructor")
if not re.fullmatch(r"[a-z][a-z0-9-]{0,30}", admin):
    raise ValueError("ADMIN_USER must be lowercase, start with a letter, and use at most 31 letters/digits/hyphens")

c.JupyterHub.bind_url = "http://0.0.0.0:8000"
c.JupyterHub.hub_ip = "0.0.0.0"
c.JupyterHub.hub_port = 8081
c.JupyterHub.hub_connect_url = "http://hub:8081"
c.JupyterHub.db_url = "sqlite:////data/jupyterhub.sqlite"
c.JupyterHub.cookie_secret_file = "/data/jupyterhub_cookie_secret"
c.JupyterHub.cleanup_servers = True
c.JupyterHub.allow_named_servers = False
c.JupyterHub.shutdown_on_logout = False

# Local accounts only: no OAuth provider, email verification, CAPTCHA, or CDN.
c.JupyterHub.authenticator_class = "native"
c.Authenticator.allow_all = True
c.JupyterHub.template_paths = [os.path.join(os.path.dirname(nativeauthenticator.__file__), "templates")]
c.Authenticator.admin_users = {admin}
c.Authenticator.username_pattern = r"[a-z][a-z0-9-]{0,30}"
c.NativeAuthenticator.open_signup = os.environ.get("OPEN_SIGNUP", "false").lower() == "true"
c.NativeAuthenticator.minimum_password_length = 10
c.NativeAuthenticator.ask_email_on_signup = False
c.NativeAuthenticator.allowed_failed_logins = 5
c.NativeAuthenticator.seconds_before_next_try = 60

c.JupyterHub.spawner_class = "dockerspawner.DockerSpawner"
c.DockerSpawner.image = os.environ.get("STUDENT_IMAGE", "offline-ml-student:1.0")
c.DockerSpawner.pull_policy = "never"
c.DockerSpawner.network_name = os.environ.get("DOCKER_NETWORK_NAME", "offline-ml-network")
c.DockerSpawner.use_internal_ip = True
c.DockerSpawner.remove = True
c.DockerSpawner.prefix = "offline-ml-student"
c.DockerSpawner.notebook_dir = "/home/student/work"
c.DockerSpawner.volumes = {"offline-ml-work-{username}": "/home/student/work"}
c.DockerSpawner.mem_limit = os.environ.get("STUDENT_MEMORY_LIMIT", "2G")
c.DockerSpawner.cpu_limit = float(os.environ.get("STUDENT_CPU_LIMIT", "1"))
c.DockerSpawner.extra_host_config = {
    "cap_drop": ["ALL"],
    "security_opt": ["no-new-privileges:true"],
    "pids_limit": 256,
}
c.Spawner.default_url = "/lab"
c.Spawner.start_timeout = 120
c.Spawner.http_timeout = 120
c.Spawner.environment = {
    "PIP_NO_INDEX": "1",
    "PIP_DISABLE_PIP_VERSION_CHECK": "1",
    "OMP_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "NUMEXPR_NUM_THREADS": "1",
    "MPLBACKEND": "module://matplotlib_inline.backend_inline",
}
