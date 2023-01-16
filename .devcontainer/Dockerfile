FROM mcr.microsoft.com/devcontainers/anaconda:0-3

# Copy environment.yml (if found) to a temp location so we update the environment. Also
# copy "noop.txt" so the COPY instruction does not fail if no environment.yml exists.
COPY environment.yml* .devcontainer/noop.txt /tmp/conda-tmp/
RUN if [ -f "/tmp/conda-tmp/environment.yml" ]; then umask 0002 && /opt/conda/bin/conda env update -n base -f /tmp/conda-tmp/environment.yml; fi \
    && rm -rf /tmp/conda-tmp

# [Optional] Uncomment this section to install additional OS packages.
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && apt-get -y install --no-install-recommends <your-package-list-here>

# COPY environment files to tmp dir and install with Pip
RUN mkdir -p /tmp/pip-reqs 
COPY requirements.txt /tmp/pip-reqs/requirements.txt
COPY requirements_dev.txt /tmp/pip-reqs/requirements_dev.txt

RUN pip install -r /tmp/pip-reqs/requirements.txt
RUN pip install -r /tmp/pip-reqs/requirements_dev.txt 
