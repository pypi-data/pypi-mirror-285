# Velocitas Python Library

[![CI workflow](https://github.com/eclipse-velocitas/velocitas-lib/actions/workflows/ci.yml/badge.svg)](https://github.com/eclipse-velocitas/velocitas-lib/actions/workflows/ci.yml)
[![License: Apache](https://img.shields.io/badge/License-Apache-yellow.svg)](http://www.apache.org/licenses/LICENSE-2.0)

A Velocitas python-based library to enable quick Velocitas CLI [package development](https://eclipse.dev/velocitas/docs/concepts/lifecycle_management/packages/development/) by providing:

* easy access and a stable API for all the things exposed via Velocitas CLI
* utility classes for
    * middleware access
    * service access
    * container runtime CLIs

Have a look at the [API documentation](./docs/index.md) to see what is available!

## Installation

To install the library:

```bash

git clone https://github.com/eclipse-velocitas/velocitas-lib.git
pip install ./velocitas-lib

```

## Update API documentation

To update the API documentation (markdown), simply run:

```bash
./update-api-docs.sh
```

## Contribution
- [GitHub Issues](https://github.com/eclipse-velocitas/velocitas-lib/issues)
- [Mailing List](https://accounts.eclipse.org/mailing-list/velocitas-dev)
- [Contribution](CONTRIBUTING.md)
