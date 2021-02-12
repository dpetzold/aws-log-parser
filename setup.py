#!/usr/bin/env python

import pathlib

from setuptools import setup


def get_requirements(name):
    with open(f"requirements/{name}.txt") as fp:
        return [line.strip() for line in fp.readlines() if not line.startswith("#")]


setup(
    name="aws-log-parser",
    version="1.8.2",
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
    install_requires=get_requirements("install"),
    setup_requires=get_requirements("setup"),
    tests_require=get_requirements("test"),
    extras_require={
        "dev": get_requirements("dev") + get_requirements("test"),
    },
)
