# Contributing to SCPYTSDK

First of all, thanks for contributing to SCPYTSDK!

## Where to notify bugs

If you find a bug or have a suggestion, just create an [issue](https://github.com/SCSDC-co/SCPYTSDK/issues).

## Environment setup

SCPYTSDK is managed with `uv` and uses `pre-commit` hooks:

```bash
git clone https://github.com/SCSDC-co/SCPYTSDK.git
cd SCPYTSDK
uv sync
uv run pre-commit install
```

## Coding style

- Format the code using ruff and isort
- Type hint your code
- Document all the functions using the google style docstrings:

```py
"""
This is an example of Google style.

Args:
    param1: This is the first param.
    param2: This is a second param.

Returns:
    This is a description of what is returned.

Raises:
    KeyError: Raises an exception.
"""
```

[Other examples](https://www.sphinx-doc.org/en/master/usage/extensions/example_google.html#example-google)

## Commit messages style

- Use the present tense ("Add feature" not "Added feature")
- Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
- Limit the first line to 72 characters or less
- Use the correct naming conventions for commit messages:
  - `feat:` For adding features
  - `fix:` For fixing bugs
  - `docs:` For updating the docs
  - `chore:` When making changes that don't change the code behavior
  - `refactor:` When refactoring the code
  - `perf:` For changes that upgrade the performance
  - `ci:` When changing the CI/CD workflow
  - `style:` When changing the code style
  - `revert:` When reverting to the previous commit

## Branches name style

If you have the permission you can create a branch,
but make sure to follow this naming conventions:

- `feat/` For adding features
- `fix/` For fixing bugs
- `docs/` For updating the docs
- `chore/` When making changes that don't change the code behavior
- `refactor/` When refactoring the code
- `perf/` For changes that upgrade the performance
- `ci/` When changing the CI/CD workflow
- `style/` When changing the code style
- `revert/` When reverting to the previous commit

## Code of conduct

By contributing to SCPYTSDK, you agree to follow the [Code of Conduct](/CODE_OF_CONDUCT.md).
