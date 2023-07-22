'''
Test app
'''

import binomialbias as bb
from shiny import App, render, ui

desc = '''
<div>This webapp calculates bias and discrimination in appointment processes, based 
on the binomial distribution. It is provided in support of the following paper:<br>
<br>
<b>Quantitative assessment of discrimination in appointments 
to senior Australian university positions.</b> Robinson PA, Kerr CC. <i>Under review (2023).</i><br>
<br>
For more information, please see the <a href="https://github.com/braindynamicsusyd/binomialbias">GitHub repository</a>
or the <a href="http://binomialbiaspaper.sciris.org">paper</a>, or <a href="mailto:peter.robinson@sydney.edu.au">contact us</a>.
</div>
'''

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.h2('BinomialBias'),
            ui.hr(),
            ui.HTML(desc),
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
