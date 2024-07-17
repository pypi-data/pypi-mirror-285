#!/usr/bin/env python
from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

requires = [
    "snowflake-sqlalchemy>=1.1.10",
    "snowflake-connector-python[pandas]>=2.7.8",
    "pandas>=0.25.3",
    "pyyaml==6.0.0",
    "pygsheets==2.0.5",
]


setup(
    name="gitlabdata",
    version="0.3.34",
    author="GitLab Data Team",
    author_email="data@gitlab.com",
    description="GitLab Data Utils",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/gitlab-data/gitlab-data-utils",
    packages=find_packages(),
    install_requires=requires,
)
