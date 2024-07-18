from setuptools import find_packages, setup

def long_description():
    with open('README.md') as f:
        return f.read()

setup(
    name = 'soak',
    version = '30',
    description = 'Process aridity templates en masse, like Helm but much more DRY',
    long_description = long_description(),
    long_description_content_type = 'text/markdown',
    url = 'https://pypi.org/project/soak/',
    author = 'foyono',
    author_email = 'shrovis@foyono.com',
    packages = find_packages(),
    py_modules = [],
    install_requires = ['aridity>=68', 'diapyr>=22', 'lagoon>=24', 'PyYAML>=5.2', 'tblib>=1.7.0'],
    package_data = {'': ['*.pxd', '*.pyx', '*.pyxbld', '*.arid', '*.aridt']},
    entry_points = {'console_scripts': ['soak=soak.soak:main']},
)
