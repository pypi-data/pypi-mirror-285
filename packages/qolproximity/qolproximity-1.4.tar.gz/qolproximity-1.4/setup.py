#!/usr/bin/env python
# coding: utf-8


from setuptools import setup,find_packages



setup(
    name = 'qolproximity',
    author = 'Providence Adu,Ph.D.',
    author_email = 'padu@charlotte.edu',
    version = '1.4',
    url='https://github.com/ProvidenceAdu/qolproximity',
    description = 'library code execute various proximity analyses using ArcPy for qol proximity analyses',
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    packages = find_packages(),
    install_requires = ['pandas>=1.0.0']
)

