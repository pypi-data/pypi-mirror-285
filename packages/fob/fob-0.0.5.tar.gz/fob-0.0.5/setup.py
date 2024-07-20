import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


# from https://packaging.python.org/guides/single-sourcing-package-version/
def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(here, rel_path), "rt") as fp:
        return fp.read()


def get_version(rel_path):
    for line in read(rel_path).splitlines():
        if line.startswith("__version__"):
            delim = '"' if '"' in line else "'"
            return line.split(delim)[1]

    raise RuntimeError("Unable to find version string.")


setuptools.setup(
    name="fob",
    version=get_version("fob/__init__.py"),
    author="Andrew Yates",
    author_email="first-then-last@mail-service-by-g.com",
    description="a library for building configurable, repeatable experiments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/andrewyates/fob",
    packages=setuptools.find_packages(),
    install_requires=[
        "colorlog",
        "numpy",
    ],
    classifiers=["Programming Language :: Python :: 3", "Operating System :: OS Independent"],
    python_requires=">=3.9",
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "fob=fob.base:__main__",
        ]
    },
)
