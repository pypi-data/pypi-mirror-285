from setuptools import setup, find_packages

setup(
    name='Flow3D',
    version='0.0.4',
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'Flow3D': ['src/flow3d/template/material/*.txt'],
    },
)

