from setuptools import setup, find_packages

NAME = 'mak-framework'
VERSION = '1.0.2'
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
    package_data={
        '': ['*.txt', '*.rst', '*.md', '*.yaml', '*.json', 'pytest.ini', 'conftest.py'],
    },
    include_package_data=True,
    install_requires=INSTALL_REQUIRES,
    python_requires='>=3.6',
)



# from setuptools import setup, find_packages
#
#
# NAME = 'mak_framework'
# VERSION = '1.0.0'
# DESCRIPTION = 'Automation Framework Using Playwright Python'
# AUTHOR = 'Muhammad Mutahar Ali Khan'
#
#
# # Define dependencies
# INSTALL_REQUIRES = [
#     'allure-pytest==2.13.5',
#     'allure-python-commons==2.13.5',
#     'Appium-Python-Client==4.0.0',
#     'attrs==23.2.0',
#     'behave==1.2.6',
#     'certifi==2024.2.2',
#     'cffi==1.16.0',
#     'charset-normalizer==3.3.2',
#     'colorama==0.4.6',
#     'contourpy==1.2.1',
#     'coverage==7.5.3',
#     'cycler==0.12.1',
#     'deepdiff==7.0.1',
#     'enum34==1.1.10',
#     'et-xmlfile==1.1.0',
#     'execnet==2.1.1',
#     'fonttools==4.53.0',
#     'greenlet==3.0.3',
#     'h11==0.14.0',
#     'idna==3.7',
#     'iniconfig==2.0.0',
#     'kiwisolver==1.4.5',
#     'lxml==5.2.1',
#     'markdown-it-py==3.0.0',
#     'MarkupSafe==2.1.5',
#     'mdurl==0.1.2',
#     'multipledispatch==1.0.0',
#     'namedlist==1.8',
#     'numpy==1.26.4',
#     'openpyxl==3.1.5',
#     'ordered-set==4.1.0',
#     'outcome==1.3.0.post0',
#     'packaging==24.0',
#     'pandas==2.2.2',
#     'parse==1.20.1',
#     'parse-type==0.6.2',
#     'Pillow==10.3.0',
#     'playwright==1.43.0',
#     'pluggy==1.5.0',
#     'pprintpp==0.4.0',
#     'pretty==0.1',
#     'pretty-py3==0.2.4.post1',
#     'prettyprint==0.1.5',
#     'prettytable==3.10.0',
#     'pycparser==2.22',
#     'pyee==11.1.0',
#     'Pygments==2.18.0',
#     'pyodbc==5.1.0',
#     'pyparsing==3.1.2',
#     'PySocks==1.7.1',
#     'pytest==8.2.1',
#     'pytest-asyncio==0.23.7',
#     'pytest-base-url==2.1.0',
#     'pytest-cov==5.0.0',
#     'pytest-diff==0.1.14',
#     'pytest-html==4.1.1',
#     'pytest-metadata==3.1.1',
#     'pytest-playwright==0.4.4',
#     'pytest-pretty-terminal==1.1.0',
#     'pytest-pspec==0.0.4',
#     'pytest-rerunfailures==14.0',
#     'pytest-spec==3.2.0',
#     'pytest-sugar==1.0.0',
#     'pytest-testdox==3.1.0',
#     'pytest-xdist==3.6.1',
#     'python-dateutil==2.9.0.post0',
#     'python-slugify==8.0.4',
#     'pytz==2024.1',
#     'PyYAML==3.13',
#     'random2==1.0.2',
#     'requests==2.31.0',
#     'rich==13.7.1',
#     'six==1.16.0',
#     'sniffio==1.3.1',
#     'sortedcontainers==2.4.0',
#     'termcolor==2.4.0',
#     'text-unidecode==1.3',
#     'tqdm==4.66.4',
#     'trio==0.25.1',
#     'trio-websocket==0.11.1',
#     'typing-extensions==4.11.0',
#     'tzdata==2024.1',
#     'urllib3==2.2.1',
#     'wcwidth==0.2.13',
#     'websocket-client==1.8.0',
#     'wsproto==1.2.0',
# ]
#
#
# setup(
#     name=NAME,
#     version=VERSION,
#     description=DESCRIPTION,
#     long_description=open('README.md').read(),
#     long_description_content_type='text/markdown',
#     author=AUTHOR,
#     packages=find_packages(),
#     include_package_data=True,
#     package_data={
#         '': ['*.yaml', '*.json', 'pytest.ini'],
#     },
#     install_requires=INSTALL_REQUIRES,
#     python_requires='>=3.9',
# )
