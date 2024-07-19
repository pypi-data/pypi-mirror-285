"""
"  _____                         _______ ______
" |     |_.-----.-----.--------.|   |   |   __ \
" |       |  _  |  _  |        ||       |      <
" |_______|_____|_____|__|__|__||___|___|___|__|
"
"        Copyright (C) 2023 LoomHR, Inc.
"             All rights reserved.
"""

from setuptools import setup


def readme():
    with open('README.md', 'r') as f:
        return f.read()


setup(
    name='loomhr-python-sdk',
    version='1.0.0',
    author='LoomHR',
    author_email='spec-support@loomhr.ai',
    description='SDK library for LoomHR specialist developers',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://loomhr.ai/build/api_reference',
    packages=[
        'loomhr'
    ],
    install_requires=['locked-dict>=2023.10.22'],
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent'
    ],
    keywords='LoomHR python',
    python_requires='>=3.10'
)