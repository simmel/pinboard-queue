ARG PYTHON_VERSION=3.7
FROM python:${PYTHON_VERSION}-slim-buster AS build

WORKDIR /usr/src

RUN python3 -m venv /venv
ENV PATH=/venv/bin:$PATH
ENV PYTHONPATH=/venv/lib/python${PYTHON_VERSION}/site-packages

COPY poetry.lock pyproject.toml ./
RUN touch \
    pinboard_queue.py \
    sanitize_url.py \
    ;
RUN --mount=type=cache,target=/root/.cache pip install .
COPY *.py *.capnp ./
RUN --mount=type=cache,target=/root/.cache pip install .

# venv won't overwrite symlinks when they point to non-existing files...
## python3 -m venv --upgrade /venv
#Error: [Errno 2] No such file or directory: '/venv/bin/python3': '/venv/bin/python3'
RUN rm -f /venv/bin/python*

# Distroless don't currently have version tags
FROM gcr.io/distroless/python3-debian10:debug@sha256:396827c703e8f43f6483d2e723592ea3bfaeafc5d327bcfca9cddaed74ead3cf
ARG PYTHON_VERSION=3.7

COPY --from=build /venv /venv
ENV PATH=/venv/bin:$PATH
ENV PYTHONPATH=/venv/lib/python${PYTHON_VERSION}/site-packages

# Upgrade the venv so we get this containers python3
# Also, without --without-pip it will try to install pip which will fail.
RUN python3 -m venv --upgrade --without-pip /venv

ENTRYPOINT ["pinboard-queue"]
CMD ["--help"]
