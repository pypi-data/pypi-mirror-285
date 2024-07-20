from setuptools import setup, find_packages

setup(
    name='trufflepig-py',
    version='0.1.12',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    install_requires=['aiohttp', 'requests']
)