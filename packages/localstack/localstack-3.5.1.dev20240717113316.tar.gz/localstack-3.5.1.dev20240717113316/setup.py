#!/usr/bin/env python
import os
import urllib.request

from setuptools import setup

# download the README.md from the community repo
readme_content = ""
try:
    url = "https://raw.githubusercontent.com/localstack/localstack/master/README.md"
    response = urllib.request.urlopen(url)
    charset = response.info().get_content_charset()
    readme_content = response.read().decode(charset)
except Exception:
    print("Long Description could not be fetched from GitHub.")
    import traceback

    traceback.print_exc()


# read the version from the VERSION file
def get_version():
    with open(os.path.join(os.path.dirname(__file__), "VERSION"), "r") as version_file:
        return version_file.read().strip()


VERSION = get_version()

setup(
    name="localstack",
    version=VERSION,
    long_description=readme_content,
    long_description_content_type="text/markdown",
    description="LocalStack - A fully functional local Cloud stack",
    author="LocalStack Contributors",
    author_email="info@localstack.cloud",
    url="https://github.com/localstack/localstack",
    license="Apache License 2.0",
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Internet",
        "Topic :: Software Development :: Testing",
        "Topic :: System :: Emulators",
    ],
    install_requires=["localstack-core", f"localstack-ext=={VERSION}"],
    extras_require={
        "runtime": ["localstack-core[runtime]", f"localstack-ext[runtime]=={VERSION}"],
    },
)
