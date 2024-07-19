#!/usr/bin/env python
# coding: utf-8



from setuptools import setup, find_packages



setup(
    name = 'qolimpervious',
    author = 'Providence Adu,Ph.D.',
    author_email = '<padu@charlotte.edu>',
    version = '1.5',
    url='https://github.com/ProvidenceAdu/qolimpervious',
    description = 'This library executes impervious surface analysis for the Quality of Life Exporer dashboard',
    long_description = open('README.md').read(),
    long_description_content_type = 'text/markdown',
    packages = find_packages(),
    install_requires = ['pandas>=1.0.0',],
    keywords = ['urban institute','python', 'Mecklenburg County','quality of life explorer', 'impervious','NPA']
)

