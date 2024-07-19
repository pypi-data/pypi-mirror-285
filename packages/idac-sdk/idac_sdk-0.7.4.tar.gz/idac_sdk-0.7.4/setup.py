import os
import re

from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def get_version():
    VERSIONFILE = "idac_sdk/_version.py"
    verstrline = open(VERSIONFILE, "rt").read()
    VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
        return verstr
    else:
        raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))


setup(
    name="idac_sdk",
    version=get_version(),
    author="Cisco GDE CAT",
    author_email="cat-dev-support@cisco.com",
    description="Python 3 SDK for iDAC",
    license="MIT",
    keywords="idac sdk",
    url="https://www-github.cisco.com/GDE-Content-Engineering/idac-sdk-python",
    packages=find_packages(include=["idac_sdk", "idac_sdk.*", "tests"]),
    long_description=read("README.md"),
    install_requires=[
        "asyncclick>=8.0.3.2",
        "httpx>=0.22.0",
        "xmltodict>=0.12.0",
        "pydantic>=1.9.0,<2.0.0",
        "deepmerge>=1.0.1",
        "PyYAML>=5.4.1",
        "jsonpath-ng>=1.5.3",
    ],
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    entry_points={"console_scripts": ["idac = idac_sdk.cli.idac:main"]},
)
