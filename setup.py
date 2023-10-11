import os

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

with open(os.path.join(HERE, "requirements.txt")) as fid:
    REQS = fid.read().splitlines()

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
            ".cvexplore-complete.bash",
            ".schema_version",
            "/common/.sources.ini",
            "/common/.env_example",
        ]
    },
    entry_points="""
            [console_scripts]
            cvexplore=CveXplore.cli:main
        """,
    classifiers=[
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=REQS,
)
