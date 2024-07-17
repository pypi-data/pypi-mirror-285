import re
from pathlib import Path

from setuptools import setup

with open("charachorder/__init__.py") as f:
    match = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)
    if not match:
        raise RuntimeError("version is not set")
    version = match.group(1)

PROJECT_URL = "https://github.com/GetPsyched/charachorder.py"

setup(
    name="charachorder",
    version=version,
    license="MIT",
    description="A mirror package for charachorder.py. Please install that instead",
    long_description=Path("readme.md").read_text(),
    long_description_content_type="text/markdown",
    url=PROJECT_URL,
    author="GetPsyched",
    author_email="dev@getpsyched.dev",
    packages=["charachorder"],
    include_package_data=True,
    python_requires=">=3.9.0",
    install_requires=["inquirer", "pyserial"],
)
