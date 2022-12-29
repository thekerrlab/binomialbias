from setuptools import setup, find_packages

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
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 3.9",
]

setup(
    name="binomialbias",
    version="1.0.0",
    author="P.A. Robinson, C. C. Kerr",
    author_email="robinson@physics.usyd.edu.au",
    description="Library for quantitative assessment of discrimination",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='http://binomialbias.sciris.org',
    keywords=["binomial distribution", "discrimination", "bias", "sexism", "racism"],
    platforms=["OS Independent"],
    classifiers=CLASSIFIERS,
    packages=find_packages(),
    include_package_data=True,
    install_requires=required,
)
