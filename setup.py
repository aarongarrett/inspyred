#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='inspyred',
    version='1.0.1',
    description="A framework for creating bio-inspired computational intelligence algorithms in Python",
    long_description=readme + '\n\n' + history,
    author="Aaron Garrett",
    author_email='garrett@inspiredintelligence.io',
    url='https://github.com/aarongarrett/inspyred',
    packages=[
        'inspyred',
        'inspyred.ec',
        'inspyred.ec.variators',
        'inspyred.swarm'
    ],
    package_dir={'inspyred':
                 'inspyred'},
    entry_points={
        'console_scripts': [
            'inspyred=inspyred.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='optimization evolutionary computation genetic algorithm particle ' + \
             'swarm estimation distribution differential evolution nsga paes ' + \
             'island model multiobjective ant colony',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
