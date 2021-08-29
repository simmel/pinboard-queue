import glob

import nox

# Run in poetry's default venv
nox.options.default_venv_backend = "none"


@nox.session
def typing(session):
    session.run("python3", "-m", "mypy", ".")


@nox.session
def lint(session):
    session.run("python3", "-m", "pylint", *glob.glob("*.py"))


@nox.session
def format(session):
    session.run("python3", "-m", "black", "--check", "--diff", ".")


@nox.session
def sort(session):
    session.run("python3", "-m", "isort", "--check", "--diff", ".")
