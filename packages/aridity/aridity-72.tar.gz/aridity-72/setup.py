from setuptools import find_packages, setup

def long_description():
    with open('README.md') as f:
        return f.read()

setup(
    name = 'aridity',
    version = '72',
    description = 'DRY config and template system, easily extensible with Python',
    long_description = long_description(),
    long_description_content_type = 'text/markdown',
    url = 'https://pypi.org/project/aridity/',
    author = 'foyono',
    author_email = 'shrovis@foyono.com',
    packages = find_packages(),
    py_modules = ['parabject'],
    install_requires = ['importlib-metadata>=2.1.3', 'importlib-resources>=3.3.1', 'pyparsing==2.4.7'],
    package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
    entry_points = {'console_scripts': ['aridity=aridity.__init__:main', 'arid-config=aridity.arid_config:main', 'processtemplate=aridity.processtemplate:main']},
)
