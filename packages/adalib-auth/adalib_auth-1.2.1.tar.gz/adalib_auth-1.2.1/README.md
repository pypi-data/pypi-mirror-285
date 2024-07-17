# adalib-auth

This repository contains the source code of `adalib-auth`, the Python library used to authenticate with the AdaLab platform.

## Installation

`adalib-auth` can be installed from PyPI or a `devpi` index:

```sh
# PyPI
pip install adalib-auth
# devpi
pip install --extra-index-url <devpi_index_url> adalib-auth
```

In order to add it to the dependencies of a Python project using `poetry` use:

```sh
poetry source add --priority=supplemental <repo_name> <devpi_index_url>
poetry source add --priority=primary PyPI
poetry add --source <repo_name> adalib-auth
```

## Usage

See the corresponding `adalib` example notebooks.

## Contributing

See the [contributor's guide](CONTRIBUTING.md).
