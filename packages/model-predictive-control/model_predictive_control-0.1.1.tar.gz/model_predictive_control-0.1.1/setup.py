"""Python setup.py for model_predictive_control package"""
import io
import os
from setuptools import find_packages, setup


def read(*paths, **kwargs):
    """Read the contents of a text file safely.
    >>> read("model_predictive_control", "VERSION")
    '0.1.0'
    >>> read("README.md")
    ...
    """

    content = ""
    with io.open(
        os.path.join(os.path.dirname(__file__), *paths),
        encoding=kwargs.get("encoding", "utf8"),
    ) as open_file:
        content = open_file.read().strip()
    return content


def read_requirements(path):
    return [
        line.strip()
        for line in read(path).split("\n")
        if not line.startswith(('"', "#", "-", "git+"))
    ]


setup(
    name="model_predictive_control",
    version=read("model_predictive_control", "VERSION"),
    description="Awesome model_predictive_control created by AdityaNG",
    url="https://github.com/AdityaNG/model_predictive_control/",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    author="AdityaNG",
    packages=find_packages(exclude=["tests", ".github"]),
    install_requires=read_requirements("requirements.txt"),
    entry_points={
        "console_scripts": ["model_predictive_control = model_predictive_control.__main__:main"]
    },
    extras_require={"test": read_requirements("requirements-test.txt")},
)
