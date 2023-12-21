import os
from itertools import chain

from setuptools import setup, find_packages

try:
    from version import VERSION
except ModuleNotFoundError:
    _PKG_DIR = os.path.dirname(__file__)
    version_file = os.path.join(_PKG_DIR, "CveXplore", "VERSION")
    with open(version_file, "r") as fdsec:
        VERSION = fdsec.read()

# The directory containing this file
HERE = os.path.abspath(os.path.dirname(__file__))

# The text of the README file
with open(os.path.join(HERE, "README.rst")) as fid:
    README = fid.read().split("##INCLUDE_MARKER##")[1]


# -*- Extras -*-
MODULES = {
    "docs",
    "kafka",
    "mongodb",
    "mysql",
    "postgres",
    "redis",
    "sqlalchemy",
    "sqllite",
}


# -*- Requirements -*-
def _strip_comments(l):
    return l.split("#", 1)[0].strip()


def _pip_requirement(req):
    if req.startswith("-r "):
        _, path = req.split()
        return reqs(*path.split("/"))
    return [req]


def _reqs(*f):
    if len(f) == 2:
        if os.getcwd().endswith("modules") and f[0] == "modules":
            f = [f[1]]
        if not os.getcwd().endswith("modules") and f[0] == ".":
            f = ("modules", f[1])
    return [
        _pip_requirement(r)
        for r in (
            _strip_comments(l)
            for l in open(os.path.join(os.getcwd(), "requirements", *f)).readlines()
        )
        if r
    ]


def reqs(*f):
    """Parse requirement file.

    Example:
        reqs('default.txt')          # requirements/default.txt
        reqs('modules', 'redis.txt')  # requirements/modules/redis.txt
        reqs('.', 'loggers.txt')  # requirements/modules/loggers.txt -> this is a reference in a requirements file
        like -r ./loggers.txt
    Returns:
        List[str]: list of requirements specified in the file.
    """
    return [req for subreq in _reqs(*f) for req in subreq]


def extras(*p):
    """Parse requirement in the requirements/modules/ directory."""
    return reqs("modules", *p)


def install_requires():
    """Get list of requirements required for installation."""
    return reqs("default.txt")


def extras_require():
    """Get map of all extra requirements."""
    module_requirements = {x: extras(x + ".txt") for x in MODULES}

    # add an 'all' value to install all requirements for all modules
    module_requirements["all"] = list(set(chain(*module_requirements.values())))

    return module_requirements


setup(
    name="CveXplore",
    version=VERSION,
    packages=find_packages(exclude=("tests", "docs")),
    url="https://github.com/cve-search/CveXplore",
    license="GNU General Public License v3.0",
    author="Paul Tikken",
    author_email="paul.tikken@gmail.com",
    home_page="https://github.com/cve-search/CveXplore",
    project_urls={
        "Documentation": "https://cve-search.github.io/CveXplore/",
        "Issues": "https://github.com/cve-search/CveXplore/issues",
    },
    description="Package for interacting with cve-search",
    long_description=README,
    long_description_content_type="text/x-rst",
    package_data={
        "CveXplore": [
            "LICENSE",
            "VERSION",
            ".schema_version",
            "common/.sources.ini",
            "common/.env_example",
            "alembic/*",
            "alembic/**/*",
            "alembic.ini",
        ]
    },
    entry_points="""
            [console_scripts]
            cvexplore=CveXplore.cli:main
        """,
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
    install_requires=install_requires(),
    extras_require=extras_require(),
)
