# Skyler's CLI
[![Test](https://github.com/bouldersky/skylers-cli/actions/workflows/test.yml/badge.svg)](https://github.com/bouldersky/skylers-cli/actions/workflows/test.yml)

This is a modular CLI tool box that I tailor to my needs over time. It includes:

- A command to bootstrap all my . files onto a new workstation
- Pretty printing DICOM files

### Setting up
This project uses pre-commit hooks for linting & whatnot. Set it up first by [installing pre-commit](https://pre-commit.com/#install):

```shell
# You can probably also use in a pip in a venv, I imagine
pipx install pre-commit
```

and then by running:

```shell
pre-commit install
```
