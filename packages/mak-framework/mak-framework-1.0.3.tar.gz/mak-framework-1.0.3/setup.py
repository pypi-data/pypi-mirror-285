from setuptools import setup, find_packages

NAME = 'mak-framework'
VERSION = '1.0.3'
DESCRIPTION = 'Automation Framework Using Playwright Python'
AUTHOR = 'Muhammad Mutahar Ali Khan'
README_FILE = 'README.md'

with open('requirements.txt') as f:
    INSTALL_REQUIRES = f.read().strip().split('\n')

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=open(README_FILE).read(),
    long_description_content_type='text/markdown',
    author=AUTHOR,
    packages=find_packages(),
    py_modules=['conftest'],
    package_data={
        '': ['*.txt', '*.rst', '*.md', '*.yaml', '*.json', 'pytest.ini'],
    },
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    python_requires='>=3.6',
)


