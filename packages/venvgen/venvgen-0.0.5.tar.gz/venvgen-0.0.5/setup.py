from setuptools import setup, find_packages
from venvgen.venvgen_version import __version__

with open('README.md', 'r') as f:
    description = f.read()


setup(
    name = 'venvgen',
    version = __version__,
    packages = find_packages(),
    install_requires = [
        'pandas',
        'inquirer',
        'tabulate'
    ],
    entry_points = {
        'console_scripts': [
            'venvgen = venvgen:main',
        ]
    },
    # include_package_data = True,
    # package_data = {
    #     'venvgen': ['database/*'],
    # },
    long_description = description,
    long_description_content_type = 'text/markdown',
)