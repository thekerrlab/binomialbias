# Binomial Bias

Code to compute quantitative assessments of discrimination within organizations, using the binomial distribution.

There are several ways to use this library, described below.

## Webapp

A live webapp is running at http://binomialbias.sciris.org.

## Python

To use locally with Python, run

    pip install binomialbias

This can then be used locally via e.g.:

    import binomialbias as bb
    bb.plotbias(n=9, actual=3, expected=4)

The PyShiny app can also be run locally via `shiny app.py`.

## Jupyter

An equivalent Jupyter notebook is available in the `jupyter` folder.

## Matlab

An equivalent Matlab script is available in the `matlab` folder.