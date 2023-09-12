"""
Shiny app for BinomialBias

The complexity of the app is due to the fact that the user can enter inputs as either
numbers or fractions, and these must be consistent. However, this can lead to infinite
loops (i.e. the user updates a fraction, which auto-updates the slider, which updates
the fraction again, etc.), so care must be taken to update things in the right order
and at the right times.
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
import version as bbv
import main as bbm


#%% Global variables

# Set the global dictionary defaults
g = sc.objdict()
g.nt = 20 # Number of appointments
g.ne = 10 # Expected number
g.na = 7 # Actual number
g.ntt = g.nt # Number of appointments (text)
g.fe = g.ne/g.nt # Expected fraction
g.fa = g.na/g.nt # Actual fraction

# Set the component keys
slider_keys = ['nt',  'ne', 'na']
text_keys   = ['ntt', 'fe', 'fa']
ui_keys = slider_keys + text_keys

# Define the app defaults
nmin = 0 # Minimum slider value
nmax = 100 # Default maximum slider value
slider_max = 1_000_000 # Absolute maximum slider value
width = '50%' # Width of the text entry boxes
delay = 0.0 # Optionally wait for user to finish input before updating


#%% Define the interface

desc = '''
<div>This webapp calculates bias and discrimination in appointment processes, based 
on the binomial distribution. It is provided in support of the following paper:<br>
<br>
<b>Quantitative assessment of discrimination in appointments to senior Australian university positions.</b>
Robinson PA, Kerr CC. <i>Under review (2023).</i><br>
<br>
For more information, please see the <a href="https://github.com/thekerrlab/binomialbias">GitHub repository</a>,
the <a href="http://binomialbiaspaper.sciris.org">paper</a> (TBC), or 
<a href="mailto:cliff@thekerrlab.com">contact us</a>.<br>
<br>
</div>
'''

version = f'''
<div><br>
<i>Version: {bbv.__version__} ({bbv.__versiondate__})</i><br>
</div>
'''

instr = ui.HTML('''
This webapp calculates the bias in a selection process, such as
the number of people of a certain group who are expected to be appointed to a committee,
versus how many actually were.<br>
<br>
For example, consider a committee with a total of <i>n<sub>t</sub></i> = 20 members.
We might expect that half would be women, i.e. <i>n<sub>e</sub></i> = 10, but that the actual
number of women on the committee is <i>n<sub>a</sub></i> = 7.<br>
<br>
Using the binomial distribution, we can calculate how fair the selection process
that produced this committee was likely to have been. In this example, the probability 
that 7 women would have been selected given a completely fair process is <i>P(n&le;n<sub>a</sub>)</i> = 0.135
(compared to 0.588 had there been 10 women selected). We can also calculate that 
the bias against women being selected for this committee is <i>B = 1.86</i>.<br>
<br>
Further information and examples are available in the manuscript.
''')

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
            ui.input_action_button("instructions", "Instructions", width='200px'),
            ui.HTML(version),
            ui.hr(),
            ui.h4('Inputs'),
            ui.div(flexgap, wg.nt, wg.ntt),
            ui.div(flexgap, wg.ne, wg.fe),
            ui.div(flexgap, wg.na, wg.fa),
        ),
        ui.panel_main(
            ui.div(flexwrap,
                ui.div(plotwrap,
                    ui.panel_conditional("input.show_p",
                        ui.output_plot('plot_bias', width='100%', height='800px'),
                    ),
                    ui.div(flexgap,
                        ui.input_checkbox("show_p", "Show plot", True),
                        ui.input_checkbox("show_s", "Show statistics", False),
                    )
                ),
                ui.div(
                    ui.panel_conditional("input.show_s",
                        ui.h4('Statistics'),
                        ui.output_table('stats_table'),
                    ),
                ),
            )
        ),
    ),
    title = 'BinomialBias',
)


#%% Define the server

def server(inputdict, output, session):
    """ The PyShiny server, which includes all the update logic """
    
    @sh.reactive.Effect
    @sh.reactive.event(inputdict.instructions)
    def instructions():
        m = ui.modal(instr, title="Instructions", easy_close=True)
        return ui.modal_show(m)

    def reconcile_fracs(*args):
        """ Convert from numbers to fractions """
        if 'ne' in args: g.fe = bbm.to_num(g.ne/g.nt)
        if 'na' in args: g.fa = bbm.to_num(g.na/g.nt)
        if 'fe' in args: g.ne = round(bbm.to_num(g.nt*g.fe))
        if 'fa' in args: g.na = round(bbm.to_num(g.nt*g.fa))
        return

    def get_ui():
        """ Get all values from the UI """
        sc.timedsleep(delay) # Don't update the UI before the user is done
        u = sc.objdict()
        for key in ui_keys:
            try:
                raw = inputdict[key]()
                v = bbm.to_num(raw)
                u[key] = v
            except:
                print(f'Encountered error with input: {key} = "{raw}", continuing...')
                u[key] = g[key]
        print(f'Current UI state:\n{u}')
        return u
    
    def check_sliders():
        """ Check that slider ranges are OK, and update if needed """
        new_max = np.median([nmax, g.ntt, slider_max])
        for key in slider_keys:
            ui.update_slider(key, max=new_max)
        return
        
    def reconcile_inputs():
        """ Reconcile the input from the sliders and text boxes """
        sc.heading('Starting to reconcile inputs!')
        u = get_ui()
        for k in ui_keys:
            print(f'{k}: g={g[k]}, u={u[k]}')
        for k in ui_keys:
            gv = g[k]
            uv = bbm.to_num(u[k])
            if k in slider_keys:
                uv = round(uv)
            match = sc.approx(gv, uv)
            if not match: # Avoid floating point errors
                print(f'Mismatch for {k}: {gv} ≠ {uv}')
                g[k] = uv # Always set the current key to the current value
                if k in ['nt', 'ntt']:
                    g.nt = uv
                    g.ntt = uv
                    reconcile_fracs('ne', 'na')
                    if k == 'ntt':
                        check_sliders()
                else:
                    reconcile_fracs(k)
                break
        
        # The isolation here avoids a potential infinite loop
        with sh.reactive.isolate():
            set_ui(u)
        sc.heading('Done reconciling inputs.')
        return
        
    def set_ui(u):
        """ Update the UI, and ensure the dict matches exactly """
        print('Updating UI')
        for k in ui_keys:
            uv = u[k]
            gv = g[k]
            if uv != gv:
                print(f'  Updating {k}: {uv} → {gv}')
                if   k in slider_keys: ui.update_slider(k, value=gv)
                elif k in text_keys:   ui.update_text(k,   value=gv)
        return
    
    def make_bias():
        """ Run the actual calculations -- the easiest part! """
        bb = bbm.BinomialBias(n=g.ntt, f_e=g.fe, f_a=g.fa)
        return bb
    
    @output
    @sh.render.plot(alt='Bias distributions')
    def plot_bias():
        """ Plot the graphs """
        reconcile_inputs() # Reconcile inputs here since this gets called before the table
        bb = make_bias()
        bb.plot(show=False, letters=False)
        return
    
    @output
    @sh.render.table
    def stats_table():
        """ Create a dataframe of the results """
        show_p = inputdict.show_p()
        if show_p: # If we're showing the plot, trigger an event by getting the UI values
            get_ui()
        else: # If we're not showing the plot, we need to reconcile inputs
            reconcile_inputs()
        bb = make_bias()
        df = bb.to_df(string=True)
        return df

    return


#%% Define and optionally run the app

app = sh.App(app_ui, server, debug=True)


def run(**kwargs):
    ''' Run the app -- equivalent to "shiny run --reload" '''
    return sh.run_app(app, **kwargs)


if __name__ == '__main__':
    run()
    
