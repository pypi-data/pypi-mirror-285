from setuptools import setup, find_packages

setup(
    name='Flow3D',
    version='0.0.3',
    packages=find_packages(),
    include_package_data=True,  # Include files specified in MANIFEST.in
    package_data={
        "": ["*.txt"],
    },
    install_requires=[
        # List your dependencies here
    ],
)

