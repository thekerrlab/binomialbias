"""
Setup file
"""

# Define the things that need to be updated
name     = 'binomialbias'
author   = 'P.A. Robinson, C. C. Kerr'
email    = 'cliff@thekerrlab.com'
desc     = 'Quantitative assessment of discrimination based on the binomial distribution'
url      = 'http://binomialbias.sciris.org'
keywords = ["binomial distribution", "discrimination", "bias", "sexism", "racism"]
requires = [
    'numpy',
    'scipy',
    'matplotlib',
    'sciris',
]
extras = {
    'app':  [
        'shiny',
        'rsconnect-python',
    ],
}


#%% Below here is boilerplate -- usually does not need to be updated

# Imports
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

CLASSIFIERS = [
    'Environment :: Console',
    'Intended Audience :: Science/Research',
    'License :: Other/Proprietary License',
    'Operating System :: OS Independent',
    'Topic :: Software Development :: Libraries :: Python Modules',
    'Development Status :: 5 - Production/Stable',
    'Programming Language :: Python',
    'Programming Language :: Python :: 3.11',
]

setup(
    name=name,
    version=version,
    author=author,
    author_email=email,
    description=desc,
    keywords=keywords,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=url,
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    include_package_data=True,
    install_requires=requires,
    extras_require=extras
)
