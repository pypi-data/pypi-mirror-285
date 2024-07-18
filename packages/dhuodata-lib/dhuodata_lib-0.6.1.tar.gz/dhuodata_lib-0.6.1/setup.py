# https://setuptools.pypa.io/en/latest/userguide/declarative_config.html
import os

from setuptools import find_packages, setup

REQUIRED_PACKAGES = open("requirements.txt").readlines()

DEV_PACKAGES = []
if os.path.exists("requirements.dev.txt"):
    DEV_PACKAGES = open("requirements.dev.txt").readlines()

README = ""
if os.path.exists("README.md"):
    README = open("README.md").read()

setup(
    name="dhuodata-lib",
    version="0.6.1",
    long_description=README,
    long_description_content_type="text/markdown",
    author="DHuO Data Team",
    author_email="diego.salles@engdb.com.br",
    url="https://gitlab.engdb.com.br/dhuo-plat/dhuo-data/data-science/dhuolib",
    install_requires=REQUIRED_PACKAGES,
    extras_require={"interactive": DEV_PACKAGES},
    package_dir={"": "src"},
    packages=find_packages(
        where="src", include=["dhuolib", "dhuolib.*"], exclude=["tests*"]
    ),
    platforms="any",
)
