import os
from setuptools import setup, find_packages

import nrt_threads_utils

PATH = os.path.dirname(__file__)

with open(os.path.join(PATH, 'requirements.txt')) as f:
    requirements = f.read().splitlines()

with open(os.path.join(PATH, 'README.md')) as f:
    readme = f.read()

packages = find_packages()

if 'tests' in packages:
    packages.remove('tests')


setup(
    name='nrt-threads-utils',
    version=nrt_threads_utils.__version__,
    author='Eyal Tuzon',
    author_email='eyal.tuzon.dev@gmail.com',
    description='Threads utilities for Python',
    keywords='python python3 python-3 tool tools thread threads pool thread-pool'
             ' util nrt nrt-utils nrt-utilities threads-utils threads-utilities'
             ' nrt-utilities nrt-thread-utils nrt-threads-utilities',
    long_description_content_type='text/markdown',
    long_description=readme,
    url='https://github.com/etuzon/python-nrt-threads-utils',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    install_requires=[requirements],
    data_files=[('', ['requirements.txt'])],
)
