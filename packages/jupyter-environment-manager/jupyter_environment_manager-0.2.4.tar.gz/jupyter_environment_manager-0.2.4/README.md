# jupyter-environment-manager

[![Documentation](https://img.shields.io/badge/Documentation-DF0982)](https://docs.qbraid.com/projects/lab/en/latest/lab/environments.html)
[![PyPI version](https://img.shields.io/pypi/v/jupyter-environment-manager.svg?color=blue)](https://pypi.org/project/jupyter-environment-manager/)
[![GitHub](https://img.shields.io/badge/issue_tracking-github-blue?logo=github)](https://github.com/qBraid/qBraid-Lab/issues)
[![Discord](https://img.shields.io/discord/771898982564626445.svg?color=pink)](https://discord.gg/TPBU2sa8Et)

JupyterLab extension for managing execution environments, packages, and kernels.

This extension is composed of a Python package named `jupyter_environment_manager` for the server extension and
an NPM package named `@qbraid/jupyter-environment-manager` for the frontend extension.

[<img src="https://qbraid-static.s3.amazonaws.com/logos/Launch_on_qBraid_white.png" width="150">](https://account.qbraid.com?gitHubUrl=https://github.com/qBraid/qBraid-Lab.git)

## Installation & Setup

For the best experience, use the Environment Manager on [lab.qbraid.com](https://lab.qbraid.com).
Login (or [create an account](https://account.qbraid.com)) and follow instructions in [user guide](https://docs.qbraid.com/projects/lab/en/latest/lab/environments.html) to get started.

The Environment manager requires **Python 3.9 or greater**, and is compatible with **JupyterLab 3.x**.

### Local Install

The Environment Manager can be installed using pip:

```shell
pip install jupyter-environment-manager
```

**If your notebook version is < 5.3**, you need to enable the extension manually:

```shell
jupyter serverextension enable --py jupyter_environment_manager --sys-prefix
jupyter nbextension install --py jupyter_environment_manager --sys-prefix
jupyter nbextension enable --py jupyter_environment_manager --sys-prefix
```

### Local Setup

[<img src="https://qbraid-static.s3.amazonaws.com/manage-account.png" width="300" align="right">](https://account.qbraid.com)

To use the Environment Manager locally, you must configure your qBraid account credentials:

1. Create a qBraid account or log in to your existing account by visiting [account.qbraid.com](https://account.qbraid.com/)
2. Copy your API Key token from the left side of your [account page](https://account.qbraid.com/):
3. Save your API key using the [qbraid-cli](https://docs.qbraid.com/projects/cli/en/latest/guide/overview.html):

```bash
pip install qbraid-cli
qbraid configure
```

The command above stores your credentials locally in a configuration file `~/.qbraid/qbraidrc`,
where `~` corresponds to your home (`$HOME`) directory.

Alternatively, the Environment Manager can discover credentials from environment variables:

```bash
export QBRAID_API_KEY='QBRAID_API_KEY'
```

## Community

- For feature requests and bug reports: [Submit an issue](https://github.com/qBraid/qBraid-Lab/issues)
- For discussions, and specific questions about the Environment Manager, qBraid Lab, or
  other topics, [join our discord community](https://discord.gg/TPBU2sa8Et)
- Want your open-source project featured as its own runtime environment on qBraid Lab? Fill out our
  [New Environment Request Form](https://forms.gle/a4v7Kdn7G7bs9jYD8)

## Launch on qBraid

The "Launch on qBraid" button (below) can be added to any public GitHub
repository. Clicking on it automaically opens qBraid Lab, and performs a
`git clone` of the project repo into your account's home directory. Copy the
code below, and replace `YOUR-USERNAME` and `YOUR-REPOSITORY` with your GitHub
info.

[<img src="https://qbraid-static.s3.amazonaws.com/logos/Launch_on_qBraid_white.png" width="150">](https://account.qbraid.com?gitHubUrl=https://github.com/qBraid/qBraid.git)

Use the badge in your project's `README.md`:

```markdown
[<img src="https://qbraid-static.s3.amazonaws.com/logos/Launch_on_qBraid_white.png" width="150">](https://account.qbraid.com?gitHubUrl=https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git)
```

Use the badge in your project's `README.rst`:

```rst
.. image:: https://qbraid-static.s3.amazonaws.com/logos/Launch_on_qBraid_white.png
    :target: https://account.qbraid.com?gitHubUrl=https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
    :width: 150px
```
