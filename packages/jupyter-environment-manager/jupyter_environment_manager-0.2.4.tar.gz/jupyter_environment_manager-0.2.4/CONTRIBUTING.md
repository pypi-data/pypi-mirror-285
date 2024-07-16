# Contributing

[![Build](https://github.com/qBraid/lab-environment-manager/actions/workflows/build.yml/badge.svg)](https://github.com/qBraid/lab-environment-manager/actions/workflows/build.yml)

## API authentication

Install the qBraid-CLI tool using pip:

```bash
pip install qbraid-cli==0.8.0.dev1
```

Save your qBraid account credentials locally:

```bash
qbraid configure
```

This will generate a configuration file located at `~/.qbraid/qbraidrc`, which will be populated with your API URL, user email, and API key. You can update your configuration values at any time using the `qbraid configure set` command. For example, to change the API-Key for local development:

```bash
qbraid configure set api-key <your-key>
```

Right now, the API url declared in your qbraidrc has not effect on the actual endpoint used. To modify the API url for local testing purposes, you
must explicitly edit the `default` value in [ApiActions.js](./src/actions/ApiActions.js).

Using only an API key for authentication may result in permissions errors, especially for routes in development that have not yet been approved for API key authentication. To bypass these errors, it's recommended to add your refresh token as well:

```bash
qbraid configure set refresh-token <your-token>
```

To get your refresh token:

- Login to account.qbraid.com and open DevTools
- Go to Application $\rightarrow$ Storage $\rightarrow$ Cookies $\rightarrow$ https://account.qbraid.com
- The value corresponding to `REFRESH` is your refresh token.
  Note, your refresh token is updated monthly.

You can also add your `EMAIL` and `REFRESH` cookies to the local storage in the developer console. Make sure you put the cookies under the 'cookies' section.

## Configure environment

Testing new routes and handlers will often require locally recreating one or more components of the qBraid Lab environment.

- In [handlers.py](./jupyter_environment_manager/handlers.py), set variable `TEST = True` to bypass routes that require use of environment's `pip`

## Development install

Follow these steps to install and enable the extension for local development.

```bash
# Clone the repository
git clone https://github.com/qBraid/lab-environment-manager.git

# Go to the extension folder
cd lab-environment-manager

# Create a new environment
conda env create

# Activate the environment
conda activate env-manager

# Install the extension in editable mode
pip install -e .

# Link your development version of the extension with JupyterLab
jupyter labextension develop . --overwrite

# Enable the server extension
jupyter serverextension enable --py jupyter_environment_manager --sys-prefix

# Rebuild extension Typescript source after making changes
jlpm run build
```

## Development uninstall

```bash
# Server extension must be manually disabled in develop mode
jupyter server extension disable jupyter_environment_manager
pip uninstall jupyter_environment_manager
```

In development mode, you will also need to remove the symlink created by `jupyter labextension develop`
command. To find its location, you can run `jupyter labextension list` to figure out where the `labextensions`
folder is located. Then you can remove the symlink named `@qbraid/jupyter-environment-manager` within that folder.

## Auto rebuilding

You can watch the source directory and run JupyterLab at the same time in different terminals to watch for changes in the extension's source and automatically rebuild the extension.

```bash
# Watch the source directory in one terminal, automatically rebuilding when needed
jlpm run watch
# Run JupyterLab in another terminal
jupyter lab
```

With the watch command running, every saved change will immediately be built locally and available in your running JupyterLab. Refresh JupyterLab to load the change in your browser (you may need to wait several seconds for the extension to be rebuilt).

By default, the `jlpm run build` command generates the source maps for this extension to make it easier to debug using the browser dev tools. To also generate source maps for the JupyterLab core extensions, you can run the following command:

```bash
jupyter lab build --minimize=False
```

### Using qBraid API docker container

Clone qBraid API repo,

```bash
git clone https://github.com/qBraid/api.git
```

and follow instructions to [Run API in container](https://github.com/qBraid/api/blob/main/README.md#running-api-in-a-container). Before running container: create local qBraid environments directory (to be used in docker bind-mount),

```bash
qbraid envs create -n <env-name>
```

## Troubleshoot

If you are seeing the frontend extension, but it is not working, check
that the server extension is enabled:

```bash
jupyter serverextension list
```

If the server extension is installed and enabled, but you are not seeing
the frontend extension, check the frontend extension is installed:

```bash
jupyter labextension list
```

## Testing routes for the server extension

With properly installed server-extension, the routes should be available at their defined urls in `setup_handlers` method in `handlers.py`. e.g. most likely the jupyterlab will run at `http://localhost:8888/`. This is the `base_url` and the `url_path` for environment manager is `jupyter-environment-manager` and then the exact routes are available in the `handlers.py`. So, to check installed environments from postman, make a request to `http://localhost:8888/jupyter-environment-manager/installed-environments`. Remember to include your credentials.

The same route on lab.qbraid.com is available at `https://lab.qbraid.com/user/{email}/jupyter-environment-manager/installed-environments`.
