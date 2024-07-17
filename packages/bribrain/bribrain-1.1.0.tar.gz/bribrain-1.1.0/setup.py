from setuptools import setup, find_packages
import os


VERSION = '1.1.0'


# Setting up

setup(

    # Name of the package
    name="bribrain",

    # Start with a small number and increase it with every change you make
    # https://semver.org
    version=VERSION,

    # Author information
    author="Andri Ariyanto",
    author_email="ariyant.andri@gmail.com",

    # Short description of your library
    description="BRIBrain Standardization Code",

    # Long description of your library
    #long_description = open('README.md').read(),
    #long_description_context_type = 'text/markdown',

    # List of keyword arguments
    keywords=['bribrain', 'dbb', 'ddb', 'python', 'gondrol', 'andri ariyanto'],

    # Packages to include into the distribution
    packages=find_packages(),

    # List of packages to install with this one
    install_requires=['mysql-connector-python==8.0.28', 'psycopg2'],

    # https://pypi.org/classifiers/
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]

)