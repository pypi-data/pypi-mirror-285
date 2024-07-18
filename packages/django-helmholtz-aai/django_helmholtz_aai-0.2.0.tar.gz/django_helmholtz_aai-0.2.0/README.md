<!--
SPDX-FileCopyrightText: 2022-2023 Helmholtz-Zentrum hereon GmbH

SPDX-License-Identifier: CC-BY-4.0
-->

# Helmholtz AAI Django App

[![CI](https://codebase.helmholtz.cloud/hcdc/django/django-helmholtz-aai/badges/main/pipeline.svg)](https://codebase.helmholtz.cloud/hcdc/django/django-helmholtz-aai/-/pipelines?page=1&scope=all&ref=main)
[![Code coverage](https://codebase.helmholtz.cloud/hcdc/django/django-helmholtz-aai/badges/main/coverage.svg)](https://codebase.helmholtz.cloud/hcdc/django/django-helmholtz-aai/-/graphs/main/charts)
[![Docs](https://readthedocs.org/projects/django-helmholtz-aai/badge/?version=latest)](https://django-helmholtz-aai.readthedocs.io/en/latest/)
[![Latest Release](https://codebase.helmholtz.cloud/hcdc/django/django-helmholtz-aai/-/badges/release.svg)](https://codebase.helmholtz.cloud/hcdc/django/django-helmholtz-aai)
[![PyPI version](https://img.shields.io/pypi/v/django-helmholtz-aai.svg)](https://pypi.python.org/pypi/django-helmholtz-aai/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Imports: isort](https://img.shields.io/badge/%20imports-isort-%231674b1?style=flat&labelColor=ef8336)](https://pycqa.github.io/isort/)
[![PEP8](https://img.shields.io/badge/code%20style-pep8-orange.svg)](https://www.python.org/dev/peps/pep-0008/)
[![Checked with mypy](http://www.mypy-lang.org/static/mypy_badge.svg)](http://mypy-lang.org/)
[![REUSE status](https://api.reuse.software/badge/codebase.helmholtz.cloud/hcdc/django/django-helmholtz-aai)](https://api.reuse.software/info/codebase.helmholtz.cloud/hcdc/django/django-helmholtz-aai)


A generic Django app to login via Helmholtz AAI

## Features

Features include

- ready-to-use views for authentification against the Helmholtz AAI
- a new `HelmholtzUser` model based upon djangos `User` model and derived
  from the Helmholtz AAI
- a new `HelmholtzVirtualOrganization` model based upon djangos
  `Group` model and derived from the Helmholtz AAI
- several signals to handle the login of Helmholtz AAI user for your specific
  application
- automated synchronization of VOs of on user authentification

Get started by following the [installation instructions][install] and have a look into
the [configuration][config] and examples provided there.


[install]: https://django-helmholtz-aai.readthedocs.io/en/latest/installation.html
[config]: https://django-helmholtz-aai.readthedocs.io/en/latest/configuration.html



## Installation

Install this package in a dedicated python environment via

```bash
python -m venv venv
source venv/bin/activate
pip install django-helmholtz-aai
```

To use this in a development setup, clone the [source code][source code] from
gitlab, start the development server and make your changes::

```bash
git clone https://codebase.helmholtz.cloud/hcdc/django/django-helmholtz-aai
cd django-helmholtz-aai
python -m venv venv
source venv/bin/activate
make dev-install
```

More detailed installation instructions my be found in the [docs][docs].


[source code]: https://codebase.helmholtz.cloud/hcdc/django/django-helmholtz-aai
[docs]: https://django-helmholtz-aai.readthedocs.io/en/latest/installation.html

## Technical note

This package has been generated from the template
https://codebase.helmholtz.cloud/hcdc/software-templates/django-app-template.git.

See the template repository for instructions on how to update the skeleton for
this package.


## License information

Copyright © 2022-2023 Helmholtz-Zentrum hereon GmbH



Code files in this repository are licensed under the
EUPL-1.2, if not stated otherwise
in the file.

Documentation files in this repository are licensed under CC-BY-4.0, if not stated otherwise in the file.

Supplementary and configuration files in this repository are licensed
under CC0-1.0, if not stated otherwise
in the file.

Please check the header of the individual files for more detailed
information.



### License management

License management is handled with [``reuse``](https://reuse.readthedocs.io/).
If you have any questions on this, please have a look into the
[contributing guide][contributing] or contact the maintainers of
`django-helmholtz-aai`.

[contributing]: https://django-helmholtz-aai.readthedocs.io/en/latest/contributing.html
