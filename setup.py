#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""
from setuptools import setup, find_packages


with open('README.md') as readme_file:
    readme = readme_file.read()

# list of strings specifying what other distributions need to be present in order for the setup script to run
setup_requires = ['pytest-runner']

# ut package requirements here
install_requires = ["pandas",
                    "prompt_toolkit"]

tests_require = ['pytest']

setup(
    name='project_night',
    version='0.1.0',
    description="Utilities for ChiPy's Project Night",
    long_description=readme,
    url='https://github.com/zaxr/project_night',
    author="Zax Rosenberg",
    author_email='zaxr@protonmail.com',
    classifiers=['Development Status :: 3 - Alpha',
                 'Intended Audience :: Developers',
                 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                 'Natural Language :: English',
                 'Programming Language :: Python :: 3.6'],
    packages=find_packages(exclude=['docs', 'tests']),
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='tests',
)
