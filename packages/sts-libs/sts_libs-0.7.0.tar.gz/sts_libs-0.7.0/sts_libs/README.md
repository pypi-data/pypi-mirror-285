# sts-libs
Python library to be used by storage tests on Fedora-based Linux distributions.

## About
sts-libs is designed to be used with [pytest](https://pytest.org) and [testinfra](https://testinfra.readthedocs.io) pytest plugin.
Used by [sts](https://gitlab.com/rh-kernel-stqe/sts) tests managed by [tmt](https://github.com/teemtee/tmt).

## Status
Actively being developed, not ready for production.

## Installation
#### Fedora and EPEL9
rpm packages can be found on [Fedora Copr](https://copr.fedorainfracloud.org/coprs/packit/gitlab.com-rh-kernel-stqe-sts-releases/)

#### Pytest virtual environment with pipx
`pipx install pytest`
`pipx inject pytest sts-libs`
#### Libs only with pip
`pip install sts-libs`

## Get involved
Feel free to open issues or merge requests at [sts gitlab page]([sts](https://gitlab.com/rh-kernel-stqe/sts)).
There you can also find the [contributing](https://gitlab.com/rh-kernel-stqe/sts/docs/contributing.md) doc.
