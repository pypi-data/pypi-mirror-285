# See license.txt for license details.
# Copyright (c) 2024, Chris Withers

import os

from setuptools import setup, find_packages

base_dir = os.path.dirname(__file__)

setup(
    name='manipulate',
    version='0.0.0.dev1',
    author='Chris Withers',
    author_email='chris@withers.org',
    license='MIT',
    description=(
        "Manipulating files in smart ways"
    ),
    long_description=open('README.rst').read(),
    url='https://github.com/simplistix/manipulate',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
    ],
    packages=find_packages(exclude=["tests"]),
    zip_safe=False,
    include_package_data=True,
    python_requires=">=3.11",
    extras_require=dict(
        test=[
            'mypy',
            'pytest',
            'pytest-cov',
            'sybil',
            'testfixtures',
        ],
        build=[
            'build',
            'chardet',
            'furo',
            'sphinx',
            'setuptools',
            'setuptools-git',
            'twine',
            'wheel',
        ]
    ),
)
