from setuptools import setup, find_packages

setup(
    name='clearspot',
    version='0.1.2',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pyodm',
        'docker',
    ],
    entry_points={
        'console_scripts': [
            'clearspot=clearspot.ortho:main',
        ],
    },
)