'''
Test app
'''

import binomialbias as bb
from shiny import App, render, ui

desc = '''For more information on this webapp, see the [paper](http://binomialbiaspaper.sciris.org):

**Quantitative assessment of discrimination in appointments to senior Australian university positions**
P. A. Robinson and C. C. Kerr
University of Sydney, Australia
'''

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.h2('BinomialBias'),
            ui.hr(),
            ui.markdown(desc),
            ui.hr(),
            ui.h4('Inputs'),
            ui.input_slider('n', 'Total number of appointments', 0, 100, 20),
            ui.input_slider('expected', 'Expected appointments', 0, 100, 5),
            ui.input_slider('actual', 'Actual appointments', 0, 100, 6),
        ),
        ui.panel_main(
            ui.output_plot('plot_bias', width='100%', height='100%'),
        ),
    ),
)


def server(input, output, session):
    @output
    @render.plot(alt='Bias distributions')
    def plot_bias():
        n        = input.n()
        expected = input.expected()
        actual   = input.actual()
        bb.plot_bias(n, expected, actual, show=False, display=False)


app = App(app_ui, server, debug=True)
