# Edgegap CLI

This is the README for the Edgegap CLI, which is part of the Edgegap suite of helpers.
This library provides a UI CLI to interact with multiple entity.

## Table of Contents

- [Overview](#overview)
- [Installation](#installation)
- [Usage](#usage)
- [Seeder](#seeder)
- [Running Tests](#running-tests)
- [Uploading Package](#uploading-package)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Overview

The Edgegap CLI includes various tools and helpers for helping with Scheduling Task.
It is designed for use within the Edgegap organization.

## Installation

To install this library, ensure you have Python and `poetry` installed. Then, use the following command:

```bash
poetry add edgegap-scheduling
```

Ensure you have the necessary permissions to install and use this library, as it is intended for Edgegap employees only.

## Usage

Please consult Obsidian Documentation for Usage

## Seeder

The `db` feature have the option to seed data in any postgresql database

you can invoke it with the CLI like this

```shell
# Not safe since it will write the pass in the history
edgegap-cli db seed --uri 'postgresql://<user>:<pass>@<localhost>:<port>/<db>' --folder /path/to/json/folder

# or, using stdin and setting the URI into a variable or env variable
echo "$POSTGRES_URI" | edgegap-cli db seed --uri 'stdin' --folder /path/to/json/folder
```

This will scan 2 folders of depth into the `/path/to/json/folder` and will try to load all json file into the 

`SeederModel` (pydantic load), any bad file or data will be discarded but the script will run all valid one

You can inspect the `SeederModel.schema()` to see the documentation for the fields

All `SeederElement` are wrapped in a database transaction and any failure of a sub-elements will result in a rollback
of the parent/child in creation. The script won't exit completely in such case but rather skip the Element and seed
the rest of the Seeds/Elements

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