#!/usr/bin/env python

import pathlib

from setuptools import setup


def get_requirement(name):
    with open(f"requirements/{name}.txt") as fp:
        return [line.strip() for line in fp.readlines() if not line.startswith("#")]


def get_requirements(requirements):
    contents = []
    for requirement in requirements:
        contents.extend(get_requirement(requirement))
    return contents


setup(
    name="aws-log-parser",
    version="2.0.1",
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
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    install_requires=get_requirement("install"),
    setup_requires=get_requirement("setup"),
    tests_require=get_requirement("test"),
    extras_require={
        "dev": (get_requirements(["dev", "test", "cli"])),
        "cli": get_requirement("cli"),
    },
    entry_points={
        "console_scripts": [
            "aws-log-parser=aws_log_parser.cli.main:main",
        ]
    },
)
