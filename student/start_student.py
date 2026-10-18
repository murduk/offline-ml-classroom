"""Seed private course copies without replacing existing student work."""
import os
from pathlib import Path
import shutil
import sys


def seed_workspace(source: Path, workspace: Path, datasets: Path) -> int:
    workspace.mkdir(parents=True, exist_ok=True)
    added = 0
    for item in sorted(source.rglob("*")):
        target = workspace / item.relative_to(source)
        if item.is_dir():
            target.mkdir(parents=True, exist_ok=True)
        elif not target.exists() and not target.is_symlink():
            target.parent.mkdir(parents=True, exist_ok=True)
            # Exclusive creation preserves existing files even on a retry.
            with item.open("rb") as src, target.open("xb") as dst:
                shutil.copyfileobj(src, dst)
            added += 1
    link = workspace / "datasets"
    if not link.exists() and not link.is_symlink():
        link.symlink_to(datasets, target_is_directory=True)
    return added


if __name__ == "__main__":
    count = seed_workspace(
        Path("/opt/classroom/courses"),
        Path("/home/student/work"),
        Path("/opt/classroom/datasets"),
    )
    print(f"Classroom workspace ready; {count} new course files copied.", flush=True)
    command = sys.argv[1:] or ["jupyterhub-singleuser"]
    os.execvp(command[0], command)
