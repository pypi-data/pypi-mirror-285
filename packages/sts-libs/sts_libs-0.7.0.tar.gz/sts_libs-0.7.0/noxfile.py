#  Copyright: Contributors to the sts project
#  GNU General Public License v3.0+ (see LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt)

import nox


@nox.session(python=['3.9', '3.12'])
def tests(session: nox.Session) -> None:
    """Runs pytest."""
    session.install('-e', '.')
    session.install('pytest', 'pytest-cov')
    with session.chdir('sts_libs'):
        session.run(
            'pytest',
            '--cov=sts',
            '--cov-config',
            '../pyproject.toml',
            '--cov-report=',
            *session.posargs,
            env={'COVERAGE_FILE': f'.coverage.{session.python}'},
        )
    session.notify('coverage')


@nox.session
def coverage(session) -> None:  # noqa: ANN001
    """Coverage analysis."""
    session.install('coverage[toml]')
    with session.chdir('sts_libs'):
        session.run('coverage', 'combine')
        session.run('coverage', 'report')
        session.run('coverage', 'erase')
