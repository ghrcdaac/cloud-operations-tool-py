from os import path
from codecs import open as codopen
from importlib import import_module
from setuptools import setup, find_packages


here = path.abspath(path.dirname(__file__))

__version__ = import_module('pylot.version').__version__

description = """
Python cLoud Operations Tool (PyLOT) is a python command line tool designed to
help DAAC operators solve the operations edge cases.
"""

# get dependencies

with codopen(path.join(here, 'requirements.txt'), encoding='utf-8') as f:
    all_reqs = f.read().split('\n')
install_requires = [x.strip() for x in all_reqs]


setup(
    name='cloud_operations_tool',
    version=__version__,
    author='Abdelhak Marouane (am0089@uah.edu)',
    description=description,
    url='https://github.com/ghrcdaac/cloud-operations-tool-py',
    license='Apache 2.0',
    classifiers=[
        'Framework :: Pytest',
        'Topic :: Scientific/Engineering',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: Freeware',
        'Programming Language :: Python :: 3.9',
    ],
    entry_points={
        'console_scripts': ['pylot=pylot.main:PyLOTClient.cli']
    },
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,
    install_requires=install_requires,
)
