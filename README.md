# BinomialBias

[![PyPI](https://badgen.net/pypi/v/binomialbias/?color=blue)](https://pypi.org/project/binomialbias)
[![Tests](https://github.com/thekerrlab/binomialbias/actions/workflows/tests.yaml/badge.svg)](https://github.com/thekerrlab/binomialbias/actions/workflows/tests.yaml?query=workflow)

This library computes and plots quantitative assessments of discrimination within organizations, based on the binomial distribution.

This code supports the following paper:

**Quantitative assessment of discrimination in appointments to senior Australian university positions.** Robinson PA, Kerr CC. *Under review (2023).*

There are several ways to use this library, described below.


## Webapp

A live webapp is running at https://binomialbias.sciris.org.


## Local installation and usage

### Python

To use locally with Python, run

    pip install binomialbias

This can then be run via e.g.:

    import binomialbias as bb
    bb.plot_bias(n=20, n_e=10, n_a=7)

This example shows the statistics for the case where there were `n = 20` appointments (e.g., the size of a committee), out of which `n_e = 10` people were expected to belong to a given group (e.g., female), and for which `n_a = 7` actually were.

### Shiny

To run the [Shiny](https://shiny.posit.co/py/) app locally, clone the repository from GitHub, then install with

    pip install -e .[app]

The Shiny app can then be run locally via the `run` script.


## Structure

- All code for the Python package is in the `binomialbias` folder.
- The script for generating the figure in the paper is in the `scripts` folder.
- Continuous integration tests are in the `tests` folder.
- Older Jupyter and Matplotlib versions are available in the `archive` folder.