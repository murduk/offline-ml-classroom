FROM quay.io/jupyterhub/jupyterhub:5.3.0

USER root

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

COPY hub/requirements.txt /tmp/requirements.txt

RUN python -m pip install --no-cache-dir --retries 5 --timeout 60 \
        -r /tmp/requirements.txt \
    && python -m pip check \
    && configurable-http-proxy --version

COPY hub/jupyterhub_config.py /etc/jupyterhub/jupyterhub_config.py

RUN mkdir -p /data

ENV PIP_NO_INDEX=1

WORKDIR /data
EXPOSE 8000

CMD ["jupyterhub", "-f", "/etc/jupyterhub/jupyterhub_config.py"]