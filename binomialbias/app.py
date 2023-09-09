"""
Shiny app for BinomialBias
"""

#%% Imports

# Get path right -- needed for Shiny deployment
import sys
import sciris as sc
sys.path.append(sc.thisdir())

# Import components
import sciris as sc
import shiny as sh
from shiny import ui
import version
import main



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
<i>Version: {version.__version__} ({version.__versiondate__})</i><br>
</div>
'''

nt_str = ui.HTML('Total number of appointments (<i>n<sub>t</sub></i>)')
ne_str = ui.HTML('Expected appointments (<i>n<sub>e</sub></i>)')
na_str = ui.HTML('Actual appointments (<i>n<sub>a</sub></i>)')
fe_str = ui.HTML('Expected fraction (<i>f<sub>e</sub></i>)')
fa_str = ui.HTML('Actual fraction (<i>f<sub>a</sub></i>)')
pagestyle = {"style": "margin-top: 2rem"} # Increase spacing at the top
flex = {"style": "display: flex; gap: 2rem"}

nmin = 0
nmax = 100
default_nt = 20
default_ne = 10
default_na = 7
width = '40%'
app_ui = ui.page_fluid(pagestyle,
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.h2('BinomialBias'),
            ui.hr(),
            ui.HTML(desc),
            ui.hr(),
            ui.h4('Inputs'),
            ui.div(flex,
                ui.input_slider('nt', label=nt_str, min=nmin, max=nmax, value=default_nt),
                ui.input_text('nt2', '(or type any value)', width=width),
            ),
            ui.div(flex,
                ui.input_slider('ne', label=ne_str, min=nmin, max=nmax, value=default_ne),
                ui.input_text('fe', label=fe_str, width=width),
            ),
            ui.div(flex,
                ui.input_slider('na', label=na_str, min=nmin, max=nmax, value=default_na),
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
    
    # Set global dictionary defaults
    slider_keys = ['nt', 'ne', 'na']
    text_keys = ['nt2', 'fe', 'fa']
    g = sc.objdict()
    g.nt = default_nt
    g.nt2 = default_nt
    g.ne = default_ne
    g.na = default_na
    g.fe = g.ne/g.nt
    g.fa = g.na/g.nt
    
    def set_ui():
        """ Update the UI """
        for key in slider_keys:
            ui.update_slider(key, value=g[key])
        for key in text_keys:
            ui.update_text(key, value=g[key])
        return
        
    
    @sh.reactive.Effect()
    def reconcile_nt():
        x = input.nt2()
        try:
            x = int(x)
            print('UPDATING TO', x)
            ui.update_slider('nt', value=x)
            print('UPDATED TO', x)
        except Exception as E:
            print('NOT VALID UPDATE', E)
        return
    
    def get_n():
        d = sc.objdict()
        d.nt = input.nt()
        d.ne = input.ne()
        d.na = input.na()
        return d
            
    def update_texts():
        
        ui.update_text('nt2', value=input.nt())
        ui.update_text('fe', value=input.nt())
        return
    
    @output
    @sh.render.plot(alt='Bias distributions')
    def plot_bias():
        d = get_n()
        # n = input.nt()
        # e = input.ne()
        # a = input.na()
        if g.first:
            update_texts()
            g.first = False
        n2 = input.nt2()
        main.plot_bias(n=d.nt, expected=d.ne, actual=d.na, show=False, display=False, letters=False, tmp=n2)
        return

    return


#%% Define and optionally run the app
app = sh.App(app_ui, server, debug=True)


def run(**kwargs):
    ''' Run the app -- equivalent to "shiny run --reload" '''
    return sh.run_app(app, **kwargs)


if __name__ == '__main__':
    run()
    
