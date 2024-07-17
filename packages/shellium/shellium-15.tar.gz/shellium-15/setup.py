from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

name = 'shellium'
version = '15'
author = 'GooseG4G'
email = 'danilnegusev@inbox.ru'
desc = 'The package provides a wrapper for working with chrome driver.'
url = 'https://github.com/GooseG4G/shellium'
packages = ['shellium']
install_requires = [
    'psutil',
    'selenium==4.22.0',
    'undetected_chromedriver==3.5.5',
]
python_requires = '>=3.10.6'

setup(
    name=name,
    author=author,
    author_email=email,
    url=url,
    version=version,
    description=desc,
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=packages,
    install_requires=install_requires,
    python_requires=python_requires,
)
