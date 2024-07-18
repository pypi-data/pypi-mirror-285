"""Setup file for the Hermes package."""

import os

from setuptools import find_packages, setup

# Get the current directory of the setup.py script
here = os.path.abspath(os.path.dirname(__file__))

# Read the version from the VERSION file
with open(os.path.join(here, "VERSION")) as version_file:
    version = version_file.read().strip()

setup(
    name="hermes-cai",
    version=version,
    packages=find_packages(include=["hermes_cai", "hermes_cai.*"]),
    include_package_data=True,
    package_data={"hermes_cai": ["templates/*", "contrib/vocab/*"]},
    install_requires=[
        "prompt-poet==0.0.25",
        "prometheus-client==0.20.0",
        "pydantic==2.7.4",
    ],
    author="James Groeneveld",
    author_email="james@character.ai",
    description="Defining and constructing production-grade LLM prompts via rich structured templates.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/character-tech/chat-stack",
    python_requires=">=3.10",
    license="MIT",
)
