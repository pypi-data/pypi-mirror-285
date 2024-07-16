from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

name = 'shellium'
version = '11'
author = 'GooseG4G'
email = 'danilnegusev@inbox.ru'
desc = 'The package provides a wrapper for working with chrome driver.'
url = 'https://github.com/GooseG4G/shellium'
packages = ['shellium']
requires = [
    'selenium==4.22.0',
    'undetected_chromedriver==3.5.5'
]

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
