# Edgegap Settings Library

This is the README for the Edgegap Settings Helper, which is part of the Edgegap suite of helpers.
This library provides utilities for interacting with Explicit Settings Models.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Running Tests](#running-tests)
- [Uploading Package](#uploading-package)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Overview

The Edgegap Settings library includes various tools and helpers for interacting with Explicit Settings Models. It is
designed for use within the Edgegap organization.

## Installation

To install this library, ensure you have Python and `poetry` installed. Then, use the following command:

```bash
poetry add edgegap-settings
```

Ensure you have the necessary permissions to install and use this library, as it is intended for Edgegap employees only.

## Usage

Please consult Obsidian Documentation for Usage

## Running Tests

To run tests for this library, you need to have pytest installed. You can install dev dependencies with:

```bash
poetry install --with=dev
```

then run

```bash
pytest
```

This will execute all the tests in the tests folder.

## Uploading Package

To upload the distribution to pypi, you will need an API token from Pypi

```bash
poetry config pypi-token.pypi <your-api-token>
poetry version x.x.x
poetry publish --build
```

## Contributing

If you'd like to contribute to this library and you're an Edgegap employee, please follow these steps:

- Fork the repository.
- Create a new branch for your changes (e.g., feature/my-feature).
- Commit your changes with a clear message.
- Push your branch to your fork.
- Open a Pull Request, explaining the changes and providing any necessary context.

## License

This software is proprietary to Edgegap. Only current Edgegap employees are allowed to use this library. Refer to the
LICENSE file for detailed licensing information.

## Contact

For support or questions related to this library, please contact support@edgegap.com.

## Acknowledgements

Thanks to the Edgegap development team for creating and maintaining this library.