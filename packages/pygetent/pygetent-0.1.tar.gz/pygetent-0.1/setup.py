from setuptools import setup, find_packages

setup(
    name         = 'pygetent',
    version      = '0.22',
    author       = 'ScreamingPigeon',
    author_email = 'visitprakhar@gmail.com',
    description  = 'Python interface to the POSIX getent family of commands',
    long_description = open('README.rst').read(),
    packages     = ['pygetent'],
)

