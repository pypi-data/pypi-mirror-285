#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages
from os import path
top_level_directory = path.abspath(path.dirname(__file__))

with open('README.md') as readme_file:
    readme = readme_file.read()

with open(path.join(top_level_directory, 'requirements.txt')) as file:
    required = file.read().splitlines()


setup(
    author="Óscar Hurtado",
    author_email='ohurtadp@sens.solutions',
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
    description="NetBox plugin for SWUpdate.",
    license="MIT",  # Make sure to include a license field
    install_requires=required,
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords=['netbox', 'netbox-plugin', 'plugin'],
    name='netbox_swupdate',
    packages=find_packages(include=['netbox_swupdate', 'netbox_swupdate.*']),
    test_suite='tests',
    url='https://github.com/netbox-community/netbox-swupdate',
    version='0.0.1.103',
    zip_safe=False,
)
