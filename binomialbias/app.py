'''
Shiny app for BinomialBias
'''

#%% Imports

# Get path right -- needed for Shiny deployment
import sys
import sciris as sc
sys.path.append(sc.thisdir())

# Import components
import version as bv
import main as bm
from shiny import App, render, ui, run_app


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

app_ui = ui.page_fluid(
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.h2('BinomialBias'),
            ui.hr(),
            ui.HTML(desc),
            ui.hr(),
            ui.h4('Inputs'),
            ui.input_slider('n', 'Total number of appointments', 0, 100, 20),
            ui.input_slider('e', 'Expected appointments', 0, 100, 10),
            ui.input_slider('a', 'Actual appointments', 0, 100, 7),
        ),
        ui.panel_main(
            ui.output_plot('plot_bias', width='100%', height='100%'),
        ),
    ),
    title = 'BinomialBias',
)


#%% Define the server

def server(input, output, session):
    
    @output
    @render.plot(alt='Bias distributions')
    def plot_bias():
        n = input.n()
        e = input.e()
        a = input.a()
        bm.plot_bias(n=n, expected=e, actual=a, show=False, display=False)
        return

    return


#%% Define and optionally run the app
app = App(app_ui, server, debug=True)


def run(**kwargs):
    ''' Run the app -- equivalent to "shiny run --reload" '''
    return run_app(app, **kwargs)


if __name__ == '__main__':
    run()
    
