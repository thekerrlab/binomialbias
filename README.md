# Binomial Bias

Library to compute and plot quantitative assessments of discrimination within organizations, based on the binomial distribution.

This code supports the following paper:

**Quantitative assessment of discrimination in appointments to senior Australian university positions.** Robinson PA, Kerr CC. *Under review (2023).*

There are several ways to use this library, described below.


## Webapp

A live webapp is running at http://binomialbias.sciris.org.


## Local installation and usage

### Python

To use locally with Python, run

    pip install binomialbias

This can then be run via e.g.:

    import binomialbias as bb
    bb.plot_bias(n=9, actual=3, expected=4)

### Shiny

To run the Shiny app, clone the repository from GitHub, then install with

    pip install -e .[app]

The PyShiny app can then be run locally via the `run` script.


## Structure

- All code for the Python package is in the `binomialbias` folder.
- The script for generating the figure in the papers is in the `scripts` folder.
- Continuous integration tests are in the `tests` folder.
- Older Jupyter and Matplotlib versions are available in the `archive` folder.