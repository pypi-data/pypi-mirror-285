"""Setup file for the Hermes package."""

from pathlib import Path

from setuptools import find_packages, setup

# Read the version from the VERSION file
with open(Path(__file__).parent.absolute() / "VERSION") as version_file:
    version = version_file.read().strip()

setup(
    name="hermes-cai",
    version=version,
    packages=find_packages(include=["hermes_cai", "hermes_cai.*"]),
    include_package_data=True,
    package_data={"hermes_cai": ["templates/*", "contrib/vocab/*"]},
    install_requires=[
        "prompt-poet==0.0.33",
        "prometheus-client==0.20.0",
        "pydantic==2.7.4",
    ],
    author="James Groeneveld",
    author_email="james@character.ai",
    description="The simplest way of using control flow (like if statements and for loops) to build production-grade prompts for LLMs.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/character-tech/chat-stack",
    python_requires=">=3.10",
    license="MIT",
)
