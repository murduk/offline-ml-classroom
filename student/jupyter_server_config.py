# Serve notebooks and all JupyterLab assets from the local container.
c = get_config()  # noqa: F821
c.ServerApp.ip = "0.0.0.0"
c.ServerApp.port = 8888
c.ServerApp.open_browser = False
c.ServerApp.root_dir = "/home/student/work"
c.LabApp.check_for_updates_class = "jupyterlab.NeverCheckForUpdate"
# Authentication is managed by jupyterhub-singleuser. Do not disable it here.
