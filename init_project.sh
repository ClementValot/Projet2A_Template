#!/bin/sh

# Install the package managers
pip install pdm uv

# PDM configuration
pdm config use_uv true

# Setup VSCode extensions
code-server --install-extension charliermarsh.ruff meta.pyrefly ms-python.debugpy pamaron.pytest-runner tamasfe.even-better-toml
code-server --uninstall-extension ms-python.flake8