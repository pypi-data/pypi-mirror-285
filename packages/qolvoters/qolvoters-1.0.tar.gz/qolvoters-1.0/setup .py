#!/usr/bin/env python
# coding: utf-8



from setuptools import setup, find_packages




setup(
    name = 'qolvoters',
    author = 'Providence Adu,Ph.D.',
    author_email = '<padu@charlotte.edu>',
    version = '1.0',
    url='https://github.com/ProvidenceAdu/qolvoters',
    description = 'This library execute voter participation rate analysis for the Quality of Life Exporer variables',
    long_description = open('README.md').read(),
    long_description_content_type = 'text/markdown',
    packages = find_packages(),
    install_requires = ['pandas>=1.0.0',],
    keywords = ['urban institute','python', 'Mecklenburg County','quality of life explorer', 'voters','NPA']
)

