#!/usr/bin/env python

import pathlib

from setuptools import setup

setup(
    name='aws-log-parser',
    version='1.6.0',
    description='Python module for parsing AWS CloudFront and LoadBalancer logs',
    long_description=(pathlib.Path(__file__).parent / 'README.md').read_text(),
    long_description_content_type='text/markdown',
    url='https://github.com/dpetzold/aws-log-parser',
    author='Derrick Petzold',
    author_email='github@petzold.io',
    license='Apache',
    packages=[
        'aws_log_parser',
    ],
    install_requires=[
        'user-agents==2.0',
        'geoip2==2.9.0',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
        'pytest-cov',
        'python-coveralls',
    ],
)
