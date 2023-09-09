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
slider_max = 2000
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

def server(inputdict, output, session):
    """ The PyShiny server, which includes all the update logic """
    
    # Set the slider
    slider_keys = ['nt', 'ne', 'na']
    text_keys = ['nt2', 'fe', 'fa']
    ui_keys = slider_keys + text_keys

    # Set global dictionary defaults
    g = sc.objdict()
    g.nt = default_nt
    g.ne = default_ne
    g.na = default_na
    g.nt2 = default_nt
    g.fe = g.ne/g.nt
    g.fa = g.na/g.nt
    
    def n_to_f():
        """ Convert from numbers to fractions """
        g.fe = g.ne/g.nt
        g.fa = g.na/g.nt
        return
    
    def f_to_n():
        """ Convert from fractions to numbers """
        g.ne = g.nt*g.fe
        g.na = g.nt*g.fa
        return
    
    def get_ui():
        """ Get all values from the UI """
        d = sc.objdict()
        for key in ui_keys:
            try:
                raw = inputdict[key]()
                v = int(raw) if key in slider_keys else float(raw)
                d[key] = v
            except:
                tb = sc.traceback()
                print(f'Encountered error with input:\n{tb}')
                d[key] = g[key]
        print(f'Current UI state:\n{d}')
        return d
    
    def reconcile_inputs(max_tries=5):
        """ Reconcile the input from the sliders and text boxes """
        sc.heading('Starting to reconcile inputs!')
        d = get_ui()
        not_reconciled = {}
        for k,v in d.items():
            if not sc.approx(g[k], v): # Avoid floating point errors
                not_reconciled[k] = [g[k], v]
                g[k] = v # Always set the current key to the current value
                if k == 'nt':
                    g.nt2 = v
                    n_to_f()
                elif k == 'nt2':
                    g.nt = v
                    n_to_f()
                elif k == 'ne': n_to_f()
                elif k == 'na': n_to_f()
                elif k == 'fe': f_to_n()
                elif k == 'fa': f_to_n()
                break
        
        with sh.reactive.isolate():
            set_ui()
        sc.heading('Done reconciling inputs.')
                    
        return
        
    def set_ui():
        """ Update the UI, and ensure the dict matches exactly """
        print(f'Updating UI to\n{g}')
        for key in slider_keys:
            v = round(g[key])
            g[key] = v
            ui.update_slider(key, value=v)
        for key in text_keys:
            v = float(f'{g[key]:0.3g}')
            g[key] = v
            ui.update_text(key, value=v)
        return
    
    @output
    @sh.render.plot(alt='Bias distributions')
    def plot_bias():
        """ Plot the graphs """
        reconcile_inputs()
        main.plot_bias(n=g.nt, expected=g.fe, actual=g.fa, show=False, display=False, letters=False)
        return

    return


#%% Define and optionally run the app
app = sh.App(app_ui, server, debug=True)


def run(**kwargs):
    ''' Run the app -- equivalent to "shiny run --reload" '''
    return sh.run_app(app, **kwargs)


if __name__ == '__main__':
    run()
    
