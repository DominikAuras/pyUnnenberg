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
    install_requires = ['pySSTV>=0.2.5','ditndah==1.0',],
    license='GPL',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Topic :: Communications :: Ham Radio',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        ],
    long_description=open('README.md').read(),
    entry_points = {},
)

