from setuptools import find_packages, setup

def long_description():
    with open('README.md') as f:
        return f.read()

setup(
    name = 'splut',
    version = '15',
    description = 'Concurrency-related Python utils',
    long_description = long_description(),
    long_description_content_type = 'text/markdown',
    url = 'https://pypi.org/project/splut/',
    author = 'foyono',
    author_email = 'shrovis@foyono.com',
    packages = find_packages(),
    py_modules = [],
    install_requires = [],
    package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
    entry_points = {'console_scripts': []},
)
