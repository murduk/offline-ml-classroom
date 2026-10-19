FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# System packages installed while building online.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        libgomp1 \
        fonts-dejavu-core \
        fonts-liberation \
        ca-certificates \
        libreoffice \
        ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN libreoffice --headless --version \
    && ffmpeg -version >/dev/null \
    && ffprobe -version >/dev/null

# Install CPU-only PyTorch before Docling/EasyOCR.
RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --retries 5 --timeout 120 \
        torch torchvision \
        --index-url https://download.pytorch.org/whl/cpu \
    && python -c "from importlib.metadata import version; print('\n'.join(f'{p}=={version(p)}' for p in ('torch', 'torchvision')))" \
        > /opt/torch-constraints.txt

# Install your complete course requirements while preserving CPU PyTorch.
COPY student/requirements.txt /tmp/requirements.txt

RUN --mount=type=cache,target=/root/.cache/pip \
    python -m pip install --retries 5 --timeout 120 \
        -c /opt/torch-constraints.txt \
        -r /tmp/requirements.txt

# Separate checks preserve completed installation layers.
RUN python -m pip check

RUN python -c "import torch, torchvision; assert torch.version.cuda is None; print('CPU PyTorch:', torch.__version__)"

# Disable external extension discovery, news, and update checks.
RUN jupyter labextension disable @jupyterlab/extensionmanager-extension:plugin \
    && jupyter labextension disable @jupyterlab/apputils-extension:announcements

# Create the unprivileged student account and workspace.
RUN groupadd --gid 1000 student \
    && useradd --uid 1000 --gid 1000 \
        --create-home --shell /bin/bash student \
    && mkdir -p \
        /home/student/work \
        /opt/classroom/courses \
        /opt/classroom/datasets \
    && chown -R student:student /home/student

# Bundle course content and configuration.
COPY courses/ /opt/classroom/courses/
COPY datasets/ /opt/classroom/datasets/

COPY student/start_student.py \
     student/check_environment.py \
     /opt/classroom/

COPY student/overrides.json \
     /usr/local/share/jupyter/lab/settings/overrides.json

COPY student/jupyter_server_config.py \
     /etc/jupyter/jupyter_server_config.py

RUN chmod -R a+rX /opt/classroom \
    && python -m pip freeze \
        > /opt/classroom/installed-packages.txt

# Runtime defaults: no package-index queries.
ENV HOME=/home/student \
    PIP_NO_INDEX=1 \
    IPYTHONDIR=/home/student/.ipython \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 \
    MPLBACKEND=module://matplotlib_inline.backend_inline

# Download Docling's standard models while building online.
RUN mkdir -p /opt/classroom/models/docling \
    && docling-tools models download \
        --output-dir /opt/classroom/models/docling \
    && docling-tools models download easyocr \
        --easyocr-lang en \
        --output-dir /opt/classroom/models/docling \
    && chmod -R a+rX /opt/classroom/models

ENV DOCLING_ARTIFACTS_PATH=/opt/classroom/models/docling


USER student
WORKDIR /home/student/work

EXPOSE 8888

ENTRYPOINT ["python", "/opt/classroom/start_student.py"]
CMD ["jupyterhub-singleuser"]