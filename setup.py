import os
import runpy
from setuptools import setup, find_packages

# Get version
cwd = os.path.abspath(os.path.dirname(__file__))
versionpath = os.path.join(cwd, 'binomialbias', 'version.py')
version = runpy.run_path(versionpath)['__version__']

# Get the documentation
with open("README.md", "r") as fh:
    long_description = fh.read()

# Get the requirements
with open('requirements.txt') as f:
    required = f.read().splitlines()

CLASSIFIERS = [
    "Environment :: Console",
    "Intended Audience :: Science/Research",
    "License :: Other/Proprietary License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Development Status :: 5 - Production/Stable",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
]

setup(
    name="binomialbias",
    version=version,
    author="P.A. Robinson, C. C. Kerr",
    author_email="peter.robinson@sydney.edu.au",
    description="Library for quantitative assessment of discrimination",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://binomialbias.sciris.org',
    keywords=["binomial distribution", "discrimination", "bias", "sexism", "racism"],
    platforms=["OS Independent"],
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'numpy',
        'scipy',
        'matplotlib',
        'sciris',
    ],
    extras_require={
        'app':  [
            'shiny',
            'rsconnect-python',
        ],
    }
)
