"""Setup file for package."""
from pathlib import Path
from subprocess import CalledProcessError, run

from setuptools import find_packages, setup

CUR_DIR = Path(__file__).parent
git_root_path = (CUR_DIR / "../..").resolve()

# We want the semantic version to come in the form
# of `git describe`.
#
# Our naming scheme is at odds with PEP 440, so we have to
# make it conforming but using "+" to join the public
# identity (version.txt) with our local identifier, which
# is the string that git describe appends.
with open(git_root_path / "version.txt", encoding="utf-8") as f:
    version_txt = f.read().strip()
try:
    semver = run(
        [git_root_path / "ci/bin/rime-semver"],
        check=True,
        encoding="utf-8",
        capture_output=True,
    ).stdout.strip()
except (CalledProcessError, AttributeError):
    semver = version_txt

with open(CUR_DIR / "README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="rime_sdk",
    version=semver,
    packages=find_packages(include=["rime_sdk*"]),
    description="Package to programmatically access a RIME deployment",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        # Note: click is a dependency of `requests` but has to be pinned here
        # due to https://github.com/psf/black/issues/2964 .
        "click>=8.0.1,<8.1.4",
        "deprecated>=1.0.0,<2.0.0",
        "simplejson",
        "pandas>=1.1.0,<1.5.0",
        "requests>=2.0.0",
        "tqdm",
        "importlib_metadata",
        "protobuf",
        #
        # below reqs are for data_format_check
        "schema",
        "numpy<2.0.0",
    ],
    python_requires=">=3.6",
    license="OSI Approved :: Apache Software License",
    entry_points={
        "console_scripts": [
            "rime-data-format-check=rime_sdk.data_format_check.cli:main",
        ]
    },
)
