# DAQview

DAQview is a desktop application for viewing live and historic DAQ data
from the Airborne Engineering Ltd DAQ system.

For more information and the user manual, refer to our website:

https://www.ael.co.uk/pages/daqview.html

Licensed under the GPL 3.0 license.

## Installation

The recommended way to install is to use `pipx` to install from the published
version on PyPI:

```
pipx install daqview
```

To run DAQview after installation, run `daqview`.

On a Linux desktop, complete installation by running `daqview --install`
to add the application to your list of locally-installed applications.

## Development Environment

First ensure poetry is installed:

```
pipx install poetry
```

Then you should be able to install all dependencies using:

```
poetry install
```

Run using:
```
poetry run python -m daqview
```

Run tests with:
```
poetry run pytest
```

Run linters with:
```
poetry run flake8 daqview
```
