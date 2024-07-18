"""
Setup file for the availability checker library.
"""

from setuptools import find_packages, setup

with open("PypiReadme.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="availability_checker",
    version="0.0.6",
    author="Gabriel Gonzalez",
    author_email="gabriel.gonzalez@meliusid.com",
    description="A package to check the availability of a bunch of variables in P60 trams por ITS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/melius/availability_data_check.git",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "pandas==2.2.2"
    ],
)
