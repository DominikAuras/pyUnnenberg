#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='PyUnnenberg',
    version='0.1',
    description='Python Module for the Unnenberg Beacon',
    author='Dominik Auras',
    author_email='DominikAuras@users.noreply.github.com',
    url='https://github.com/DominikAuras/pyUnnenberg',
    packages=find_packages(),
    keywords='HAM SSTV Beacon',
    install_requires = ['pySSTV>=0.2.5','pyalsaaudio>=0.5','pillowfight'],
    license='MIT',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Topic :: Communications :: Ham Radio',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        ],
    long_description=open('README.md').read(),
    entry_points = {},
)

