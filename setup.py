#!/usr/bin/env python

from setuptools import setup

setup(
    name='aws-log-parser',
    version='1.3.1',
    description='Python module for parsing AWS CloudFront and LoadBalancer logs',
    packages=[
        'aws_log_parser',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
    ],
)
