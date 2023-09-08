"""
Shiny app for BinomialBias
"""

#%% Imports

# Get path right -- needed for Shiny deployment
import sys
import sciris as sc
sys.path.append(sc.thisdir())

# Import components
import version as bv
import main as bm
import shiny as sh
from shiny import ui


#%% Define the interface

desc = f'''
<div>This webapp calculates bias and discrimination in appointment processes, based 
on the binomial distribution. It is provided in support of the following paper:<br>
<br>
<b>Quantitative assessment of discrimination in appointments to senior Australian university positions.</b>
Robinson PA, Kerr CC. <i>Under review (2023).</i><br>
<br>
For more information, please see the <a href="https://github.com/braindynamicsusyd/binomialbias">GitHub repository</a>
or the <a href="http://binomialbiaspaper.sciris.org">paper</a>, or <a href="mailto:peter.robinson@sydney.edu.au">contact us</a>.<br>
<br>
<i>Version: {bv.__version__} ({bv.__versiondate__})</i><br>
</div>
'''

nt_str = ui.HTML('Total number of appointments (<i>n<sub>t</sub></i>)')
ne_str = ui.HTML('Expected appointments (<i>n<sub>e</sub></i>)')
na_str = ui.HTML('Actual appointments (<i>n<sub>a</sub></i>)')
fe_str = ui.HTML('Expected fraction (<i>f<sub>e</sub></i>)')
fa_str = ui.HTML('Actual fraction (<i>f<sub>a</sub></i>)')
flex = {"style": "display: flex; gap: 2rem"}

nmin = 0
nmax = 100
width = '40%'
app_ui = ui.page_fluid(
    {"style": "margin-top: 2rem"}, # Increase spacing at the top
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.h2('BinomialBias'),
            ui.hr(),
            ui.HTML(desc),
            ui.hr(),
            ui.h4('Inputs'),
            ui.div(
                flex,
                ui.input_slider('nt', label=nt_str, min=nmin, max=nmax, value=20),
                ui.input_text('ntt', '(or type any value)', width=width),
            ),
            ui.div(
                flex,
                ui.input_slider('ne', label=ne_str, min=nmin, max=nmax, value=10),
                ui.input_text('fe', label=fe_str, width=width),
            ),
            ui.div(
                flex,
                ui.input_slider('na', label=na_str, min=nmin, max=nmax, value=7),
                ui.input_text('fa', label=fa_str, width=width),
            ),
        ),
        ui.panel_main(
            ui.output_plot('plot_bias', width='100%', height='100%'),
        ),
    ),
    title = 'BinomialBias',
)


#%% Define the server

def server(input, output, session):
    
    @sh.reactive.Effect()
    def _():
        x = input.ntt()
        try:
            x = int(x)
            print('UPDATING TO', x)
            ui.update_slider('nt', value=x)
            print('UPDATED TO', x)
        except Exception as E:
            print('NOT VALID UPDATE', E)
    
    @output
    @sh.render.plot(alt='Bias distributions')
    def plot_bias():
        n = input.nt()
        e = input.ne()
        a = input.na()
        n2 = input.ntt()
        bm.plot_bias(n=n, expected=e, actual=a, show=False, display=False, letters=False, tmp=n2)
        return

    return


#%% Define and optionally run the app
app = sh.App(app_ui, server, debug=True)


def run(**kwargs):
    ''' Run the app -- equivalent to "shiny run --reload" '''
    return sh.run_app(app, **kwargs)


if __name__ == '__main__':
    run()
    
