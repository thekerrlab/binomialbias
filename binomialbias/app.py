"""
Shiny app for BinomialBias
"""

#%% Imports

# Get path right -- needed for Shiny deployment
import sys
import sciris as sc
sys.path.append(sc.thisdir())

# Import components
import numpy as np
import sciris as sc
import shiny as sh
from shiny import ui
import version
import main


#%% Global variables

# Set the global dictionary defaults
g = sc.objdict()
g.nt = 20
g.ne = 10
g.na = 7
g.ntt = g.nt
g.fe = g.ne/g.nt
g.fa = g.na/g.nt
g.stale = True
g.fig = None

# Set the slider
slider_keys = ['nt',  'ne', 'na']
text_keys   = ['ntt', 'fe', 'fa']
ui_keys = slider_keys + text_keys


#%% Define the interface

desc = f'''
<div>This webapp calculates bias and discrimination in appointment processes, based 
on the binomial distribution. It is provided in support of the following paper:<br>
<br>
<b>Quantitative assessment of discrimination in appointments to senior Australian university positions.</b>
Robinson PA, Kerr CC. <i>Under review (2023).</i><br>
<br>
For more information, please see the <a href="https://github.com/thekerrlab/binomialbias">GitHub repository</a>
or the <a href="http://binomialbiaspaper.sciris.org">paper</a> (TBC), or 
<a href="mailto:cliff@thekerrlab.com">contact us</a>.<br>
<br>
<i>Version: {version.__version__} ({version.__versiondate__})</i><br>
</div>
'''

nt_str = ui.HTML('Total number of appointments (<i>n<sub>t</sub></i>)')
ne_str = ui.HTML('Expected appointments (<i>n<sub>e</sub></i>)')
na_str = ui.HTML('Actual appointments (<i>n<sub>a</sub></i>)')
ntt_str = '(or type any value)'
fe_str = ui.HTML('Expected fraction (<i>f<sub>e</sub></i>)')
fa_str = ui.HTML('Actual fraction (<i>f<sub>a</sub></i>)')
pagestyle = {"style": "margin-top: 2rem"} # Increase spacing at the top
flexgap   = {"style": "display: flex; gap: 2rem"}
flexwrap  = {"style": "display: flex; flex-wrap: wrap"}
plotwrap  = {'style': 'width: 50vw; min-width: 400px; max-width: 1200px'}

# Define the defaults
nmin = 0
nmax = 100
slider_max = 1_000_000
width = '50%'
delay = 1.0 # Wait for user to finish input before updating

# Define the widgets
wg = sc.objdict()
wg.nt  = ui.input_slider('nt', label=nt_str, min=nmin, max=nmax, value=g.nt)
wg.ne  = ui.input_slider('ne', label=ne_str, min=nmin, max=nmax, value=g.ne)
wg.na  = ui.input_slider('na', label=na_str, min=nmin, max=nmax, value=g.na)
wg.ntt = ui.input_text('ntt',  label=ntt_str, width=width, value=g.ntt)
wg.fe  = ui.input_text('fe',   label=fe_str,  width=width, value=g.fe)
wg.fa  = ui.input_text('fa',   label=fa_str,  width=width, value=g.fa)

# Define the app layout
app_ui = ui.page_fluid(pagestyle,
    ui.layout_sidebar(
        ui.panel_sidebar(
            ui.h2('BinomialBias'),
            ui.hr(),
            ui.HTML(desc),
            ui.hr(),
            ui.h4('Inputs'),
            ui.div(flexgap, wg.nt, wg.ntt),
            ui.div(flexgap, wg.ne, wg.fe),
            ui.div(flexgap, wg.na, wg.fa),
        ),
        ui.panel_main(
            ui.output_ui('everything')
        ),
    ),
    title = 'BinomialBias',
)


#%% Define the server

def server(inputdict, output, session):
    """ The PyShiny server, which includes all the update logic """

    def n_to_f():
        """ Convert from numbers to fractions """
        g.fe = main.to_num(g.ne/g.nt)
        g.fa = main.to_num(g.na/g.nt)
        return
    
    def f_to_n():
        """ Convert from fractions to numbers """
        g.ne = main.to_num(g.nt*g.fe)
        g.na = main.to_num(g.nt*g.fa)
        return
    
    def get_ui():
        """ Get all values from the UI """
        # sc.timedsleep(delay) # Don't update the UI before the user is done
        d = sc.objdict()
        for key in ui_keys:
            try:
                raw = inputdict[key]()
                v = main.to_num(raw)
                d[key] = v
            except:
                print(f'Encountered error with input: {key} = "{raw}", continuing...')
                d[key] = g[key]
        print(f'Current UI state:\n{d}')
        return d
    
    def check_stale(d=None):
        """ Check if the UI has been updated """
        if d is None:
            d = get_ui()
        g.stale = any([d[k] != g[k] for k in ui_keys])
        if g.stale:
            g.pop('fig', None)
        return g.stale
    
    def check_sliders():
        """ Check that slider ranges are OK, and update if needed """
        new_max = np.median([nmax, g.ntt, slider_max])
        for key in slider_keys:
            ui.update_slider(key, max=new_max)
        return
        
    def reconcile_inputs(max_tries=5):
        """ Reconcile the input from the sliders and text boxes """
        sc.heading('Starting to reconcile inputs!')
        d = get_ui()
        for k,v in d.items():
            if not sc.approx(g[k], v): # Avoid floating point errors
                print(f'Mismatch for {k}: {g[k]} ≠ {v}')
                v = main.to_num(v)
                g[k] = v # Always set the current key to the current value
                if k in ['nt', 'ntt']:
                    g.nt = v
                    g.ntt = v
                    n_to_f()
                    if k == 'ntt':
                        check_sliders()
                elif k in ['ne', 'na']:
                    n_to_f()
                elif k in ['fe', 'fa']:
                    f_to_n()
                break
        
        with sh.reactive.isolate():
            set_ui(d)
        sc.heading('Done reconciling inputs.')
        return
        
    def set_ui(curr):
        """ Update the UI, and ensure the dict matches exactly """
        print('Updating UI')
        for key in ui_keys:
            curr_v = curr[key]
            v = g[key]
            if curr_v != v:
                print(f'Updating: {curr_v} → {v}')
                if key in slider_keys:
                    ui.update_slider(key, value=v)
                elif key in text_keys:
                    ui.update_text(key, value=v)
        return
    
    def make_bias():
        """ Run the actual app """
        bb = main.BinomialBias(n=g.ntt, f_e=g.fe, f_a=g.fa)
        return bb
    
    @output
    @sh.render.plot(alt='Bias distributions')
    def plot_bias():
        """ Plot the graphs """
        print("I AM GRAPHHHHHHHH")
        # check_stale()
        # if g.stale:
        # with sh.reactive.isolate():
        #     reconcile_inputs()
        bb = make_bias()
        bb.plot(show=False, letters=False)
        print('DONE GRAPH')
        return
    
    @output
    @sh.render.table
    def results():
        """ Create a dataframe of the results """
        print('I AM TABBLLLLLELEEEEEEE')
        # check_stale()
        # if g.stale:
        #     reconcile_inputs()
        bb = make_bias()
        df = bb.to_df(string=True)
        return df
    
    
    @output
    @sh.render.ui
    def everything():
        check_stale()
        if g.stale:
            reconcile_inputs()
        
        return ui.TagList(
            ui.div(flexwrap,
                ui.div(plotwrap,
                    ui.output_plot('plot_bias', width='100%', height='800px'),
                    ui.input_checkbox("show", "Show statistics", False),
                ),
                ui.div(
                    ui.panel_conditional("input.show",
                        ui.h4('Statistics'),
                        ui.output_table('results'),
                    ),
                ),
            )
            )

    return


#%% Define and optionally run the app
app = sh.App(app_ui, server, debug=True)


def run(**kwargs):
    ''' Run the app -- equivalent to "shiny run --reload" '''
    return sh.run_app(app, **kwargs)


if __name__ == '__main__':
    run()
    
