from setuptools import setup

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

name = 'biscuit-cookies'
version = '9'
author = 'GooseG4G'
email = 'danilnegusev@inbox.ru'
desc = ('The package is designed to work with cookies for the Chrome browser. The package allows you to delete, '
        'insert, receive and decrypt cookies.')
url = 'https://github.com/GooseG4G/biscuit'
packages = ['biscuit']
requires = [
    'pywin32', 'pycryptodome', 'pyql3==15'
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

