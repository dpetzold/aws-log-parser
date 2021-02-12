#!/usr/bin/env python

import pathlib

from setuptools import setup


def get_requirements(name):
    with open(f"requirements/{name}.txt") as fp:
        return [line.strip() for line in fp.readlines() if not line.startswith("#")]


setup(
    name="aws-log-parser",
    version="1.9.0",
    description="Parse AWS CloudFront and LoadBalancer logs into Python dataclasses",
    long_description=(pathlib.Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/dpetzold/aws-log-parser",
    author="Derrick Petzold",
    author_email="github@petzold.io",
    license="Apache",
    packages=[
        "aws_log_parser",
    ],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=get_requirements("install"),
    setup_requires=get_requirements("setup"),
    tests_require=get_requirements("test"),
    extras_require={
        "dev": get_requirements("dev") + get_requirements("test"),
    },
)
