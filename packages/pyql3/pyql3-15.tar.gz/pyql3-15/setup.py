from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

name = 'pyql3'
version = '15'
author = 'GooseG4G'
email = 'danilanegusev@gmail.com'
desc = 'The package provides a wrapper for working with SQLite databases.'
url = 'https://github.com/GooseG4G/pyql3'
packages = ['PyQL3']
requires = []

setup(
    name=name,
    version=version,
    author=author,
    author_email=email,
    description=desc,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=url,
    packages=packages,
    install_requires=requires
)
