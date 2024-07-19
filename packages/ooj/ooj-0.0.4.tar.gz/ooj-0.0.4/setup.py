from io import open
from setuptools import setup

"""
:authors: KiryxaTech
:license Apache License, Version 2.0, see LICENSE file
:copyright: (c) 2024 KiryxaTech
"""

version = "0.0.4"

with open('README.md', encoding='utf-8') as f:
    long_discription = f.read()

setup(
    name='ooj',
    version=version,

    author='KiryxaTech',
    author_email='kiryxatech@gmail.com',

    description=(u'OOJ (Object Oriented JSON) is a Python library designed to simplify working with JSON data. '
                 u'It allows you to create, process, and interact with JSON data using an object-oriented approach.'),
    long_description=long_discription,
    long_description_content_type='text/markdown',

    url='https://github.com/KiryxaTechDev/ooj',
    download_url=f'https://github.com/KiryxaTechDev/ooj/archive/refs/tags/{version}.zip',

    packages=['ooj',
              'ooj.exceptions'],

    classifiers=[
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
    ]
)