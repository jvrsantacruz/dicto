# -*- coding: utf-8 -*-

import os

from setuptools import setup, find_packages

here = os.path.dirname(os.path.abspath(__file__))
README = open(os.path.join(here, 'README.rst')).read()
REQUIREMENTS = open(os.path.join(here, 'requirements.txt')).readlines()

setup(
    name='dicto',
    version='0.4.0',
    description='Notification generator',
    author='Javier Santacruz',
    author_email='jsl@taric.es',
    install_requires=REQUIREMENTS,
    long_description=README,
    py_modules=['dicto'],
    packages=find_packages(),
    classifiers=[
        "Internal :: Do not upload"
    ],
    entry_points="""
    [console_scripts]
    dicto=dicto:cli
    """
)
