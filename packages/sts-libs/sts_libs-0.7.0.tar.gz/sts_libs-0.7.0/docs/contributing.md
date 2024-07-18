# Contributing to sts

## Python code contributions
### Local environment
- Fork the [project](https://gitlab.com/rh-kernel-stqe/sts/)
- Clone your fork and enter the directory
- Create and enter python virtualenv
  - `hatch shell`
- Enable pre-commit hooks
  - `pre-commit install`
- If you're using an IDE
  - set max line length to `120` and Python compatibility checks to 3.9+.
  - consider installing ruff plugin
- To check your changes without commiting
  - pre-commit run --all-files
- To list available hatch env scripts, run `hatch env show`
  - `hatch run container-prep` will use buildah to prepare a Fedora container
  - `hatch run tests` will run the tests within the container
  - `hatch run format` will run ruff formatter and linter with autofix enabled
  - `hatch run lint` will run ruff without autofix
  - `hatch run check` will run mypy type annotation checks
  - `hatch run all` will run format, check and tests

### Typing and Docstrings
All new functions, methods, classes in sts-libs should include
[type annotations](https://docs.python.org/3/library/typing.html), so they pass `mypy --strict` check.

There should always be a single-line docstring and optionally:

  - Argument documentation.

    - when the usage of the argument is not clear even with proper type annotation
    - not all arguments needs to be documented

  - Usage example

Docstrings are in 'google format'.
Example of typed and documented method:
```
def add(
    self,
    name: str = '/',
    result: Literal['pass', 'fail', 'info', 'warn', 'error'] = 'pass',
    note: Optional[str] = None,
    log: Optional[List[str]] = None,
    errors: Optional[List[str]] = None,
) -> None:
    """Add result to custom results list.

    When tmt plan is set to 'result: custom', use this followed by submit() to create the necessary result.json.
    Use multiple times when test have distinctive steps (parts).

    Usage example:
        results = tmt.Results()
        results.add(name='setup', result='pass')
        results.add(name='test', errors=errors, log=['dmesg.log', 'messages.log'])
        results.submit()

    Args:
        name: Optional path-like string. e.g. '/setup/something' or 'setup'.
        log: Paths in the custom results file are treated as relative to ${TMT_TEST_DATA} path.
        errors: Can be used with atomic_run. If errors are not None, result is overwritten to 'false'.
    """
```

The pre-commit check does not include `--strict` mypy argument, mainly due to the existing untyped legacy code (contributions very welcome),
but also to allow more freedom when writing sts tests. You might be however asked to add type annotations when creating a merge request to sts-libs.

### Commits
First line up to 50 characters.
Additional details should be separated by a blank line.

Consider following [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/) rules.

It is encouraged to do multiple smaller commits instead of one large one.

The pre-commit hooks include some auto-fixes by ruff linter and formatter.
Please check any changed files before trying to commit again.

### Creating a merge request
Follow the [gitlab documentation](https://docs.gitlab.com/ee/user/project/merge_requests/creating_merge_requests.html#when-you-work-in-a-fork)
for how to create a merge request.
