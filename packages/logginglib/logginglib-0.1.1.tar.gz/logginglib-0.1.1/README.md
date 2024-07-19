# Publishing LoggingLib with Poetry

This guide will walk you through the steps to publish your Python package using Poetry. Poetry is a dependency management and packaging tool for Python projects. 

## Prerequisites

1. **Poetry Installed**: Make sure Poetry is installed on your system. You can install it by following the instructions on the [Poetry official website](https://python-poetry.org/docs/#installation).

2. **PyPI Account**: Ensure you have an account on [PyPI](https://pypi.org/). You'll need your username and password for publishing.

## Steps to Publish a Python Package

### 1. Build Your Package

Navigate to your project directory and run the following command to build your package:

```sh
poetry build
```

This command will generate distribution archives (e.g., `.whl` and `.tar.gz` files) in the `dist` directory.

### 2. Publish Your Package

To publish your package to PyPI, use the following command:

```sh
poetry publish --username <your-username> --password <your-password>
```

Alternatively, you can use the `--build` option to build and publish your package in one step:

```sh
poetry publish --build --username <your-username> --password <your-password>
```

### 3. Using PyPI Token

For better security, you can use an API token instead of your username and password. First, generate an API token from your [PyPI account settings](https://pypi.org/manage/account/#api-tokens).

Then, you can publish your package using the token:

```sh
poetry publish --build --username __token__ --password <your-token>
```

### 4. Publishing to TestPyPI (Optional)

Before publishing to the official PyPI repository, you might want to publish to TestPyPI to test your package. 

To publish to TestPyPI, use the following command:

```sh
poetry publish --build --repository testpypi --username <your-username> --password <your-password>
```

To use an API token with TestPyPI:

```sh
poetry publish --build --repository testpypi --username __token__ --password <your-token>
```
