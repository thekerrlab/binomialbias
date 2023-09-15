"""
Classes and functions for calculating binomial bias
"""

import numpy as np
import scipy.stats as st
import sciris as sc
import pylab as pl
import matplotlib as mpl


__all__ = ['BinomialBias', 'plot_bias']


def to_str(x, sf=3):
    """ Convert a number to a string with specified significant figures """
    fmt = f'0.{sf}g' # e.g. '0.3g'
    if isinstance(x, str):
        x = to_num(x) # Doesn't matter what we convert it to, the string is the same
    if isinstance(x, float):
        string = f'{x:{fmt}}' # e.g. f'{0.47162:0.3g}'
    else:
        string = str(x) # Handle ints
        
    return string


def to_num(x, die=False):
    """ Convert a string to a number, handling either ints or floats """
    try:
        if sc.isnumber(x):
            x = to_str(x)
        num = float(x) if '.' in x else int(x) # Handle int or float
    except Exception as E:
        if die:
            raise E
        else:
            num = np.nan
    return num


class BinomialBias(sc.prettyobj):
    
    def __init__(self, n=20, n_e=10, n_a=7, f_e=None, f_a=None, one_sided=True,
                 display=False, plot=False, **kwargs):
        """
        Analysis for the paper "Quantitative assessment of discrimination in 
        appointments to senior Australian university positions" -
        by Prof. P. A. Robinson, School of Physics, University of Sydney;
        Python conversion by Dr. C. C. Kerr, Institute for Disease Modeling.
    
        Args:
            n (int): The total number of appointments
            n_e (int/float): Expected number of appointments of a group given a fair process
            n_a (int/float): Actual number appointments of a group
            f_e (float): Explicitly specify the fraction of expected appointments (instead of n_e)
            f_a (float): Explicitly specify the fraction of actual appointments (instead of n_a)
            one_sided: Whether to always show the probability on the same side (else, swap above 50%)
            display (bool): Whether to display the results (equivalent to calling B.display())
            plot (bool): Whether to plot the results (equivalent to calling B.plot())
            
        Results are stored in "results", which has the following fields:
            expected_low, expected_high: 95% confidence interval for individuals given a fair process
            cum_prob: Cumulative distribution function of n_a or fewer appointments
            bias: Preference ratio the estimate of the disparity in how two groups are viewed by selectors
            p_future: Probability of unbiased selection; values much less than 1 do imply bias; values < 0.1 should be cause for serious concern and values < 0.01 should provoke urgent action.
    
        **Examples**::
            
            import binomialbias as bb
            
            # Use absolute numbers and plot
            B = bb.BinomialBias(n=9, n_e=4, n_a=3)
            B.plot()
            
            # Use fractions and print
            B = bb.BinomialBias(n=155, f_e=0.44, f_a=0.2)
            B.display()
        """
        # Handle deprecations
        expected = kwargs.pop('expected', None) or n_e
        actual   = kwargs.pop('actual', None) or n_a
        if 0 < expected < 1: f_e = expected # Treat as fractions
        if 0 < actual   < 1: f_a = actual
        
        # Handle inputs
        if f_e is not None: expected = f_e*n
        if f_a is not None: actual   = f_a*n
        self.n         = n
        self.expected  = expected
        self.actual    = actual
        self.one_sided = one_sided
        
        
        # Perform validation
        self.validate()
        
        # Calculate the results
        self.calculate()
        if display:
            self.display()
        if plot:
            self.plot()
        
        return

    
    def validate(self):
        """ Validate the inputs; called automatically on initialization """
        if self.n < 2:
            errormsg = 'There must be ≥2 appointments'
            raise ValueError(errormsg)
        if self.expected < 1:
            errormsg = 'There must be ≥1 expected appointments'
            raise ValueError(errormsg)
        if self.expected >= self.n:
            errormsg = f'Expected appointments ({self.expected}) must be less than total appointments ({self.n})'
            raise ValueError(errormsg)
        if self.actual > self.n:
            errormsg = f'Actual appointments ({self.actual}) must be less than or equal to total appointments ({self.n})'
            raise ValueError(errormsg)
        return
    
    
    def calculate(self):
        """ Calculate the statistics; called automatically on initialization """
        
        # Shorten variables
        n      = self.n
        actual = self.actual
        expect = self.expected
        
        x     = np.arange(n+1) # X-axis: all possible samples
        f_e = expect/n # Expected proportion of target group
        f_a = actual/n # Actual proportion of target group
        e_pmf = st.binom.pmf(x, n, f_e) # Binomial distribution
        a_pmf = st.binom.pmf(x, n, f_a)
    
        # Calculation of the preference ratio
        # (n-actual)/(n-expected) - ratio for other group
        # actual/expected - ratio for relative proportion
        if actual > 0:
            bias = ((n-actual)/(n-expect))/(actual/expect)
        else:
            bias = np.inf
        if self.one_sided or actual <= expect:
            cum_prob = sum(e_pmf[x<=actual])
        else:
            cum_prob = sum(e_pmf[x>=actual])
        
        # Gaussian CI approximation
        e_mean = n*f_e
        e_std = np.sqrt(e_mean*(1-f_e))

        # Calculate bounds
        e_low  = int(max(0, np.ceil(e_mean-2*e_std)))
        e_high = int(min(n, np.floor(e_mean+2*e_std)))

        ## Actual
        a_mean = n*f_a
        a_std  = np.sqrt(a_mean*(1-f_a))

        # Calculate bounds
        a_low  = int(max(0, np.ceil(a_mean-2*a_std)))
        a_high = int(min(n, np.floor(a_mean+2*a_std)))
    
        # Calculate p_future
        p_future = sum(a_pmf[e_low:e_high+1]) # +1 since used as an index
        
        # Assemble into a results object
        self.results = sc.objdict()
        
        # Store inputs
        self.results.n = self.n
        self.results.expected = self.expected
        self.results.actual = self.actual
        self.results.f_expected = self.expected/self.n
        self.results.f_actual = self.actual/self.n
        
        # Store outputs
        self.results.expected_low = e_low
        self.results.expected_high = e_high
        self.results.cum_prob = cum_prob
        self.results.bias = bias
        self.results.p_future = p_future
        
        # Other things, used for plotting
        pr = sc.objdict()
        pr.x = x
        pr.e_pmf = e_pmf
        pr.a_pmf = a_pmf
        pr.actual_low  = a_low
        pr.actual_high = a_high
        self.plot_results = pr
        
        return self.results
    
    
    def display(self):
        """ Display the results of the calculation """
        print(self.results)
        return
    
    
    def to_df(self, string=False):
        """ Convert to a dataframe, optionally casting to string for correct s.f. """
        df = sc.dataframe.from_dict(self.results, orient='index')
        df = df.reset_index()
        df = df.rename(columns={'index':'Parameter', 0:'Value'})
        if string:
            df['Value'] = df['Value'].apply(lambda x: to_str(x))
        return df


    def plot(self, dist_color='cornflowerblue', cdf_color='darkblue', ci_color='k', letters=True, wrap=False,
             fig=None, barkw=None, figkw=None, layoutkw=None, textkw=None, max_bars=1000, show=True):
        """
        Plot the results of the bias calculation
        
        Args:
            dist_color: the color of the full distribution
            cdf_color: the color of the part of the distribution being integrated
            ci_color: the color of the confidence bounds
            letters: if True, show frame labels with letters
            wrap: if True, wrap the plot title across two lines
            fig: if supplied, plot using this figure
            barkw: a dictionary of keyword arguments for the bar plots (passed to pl.bar())
            figkw: a dictionary of keyword arguments for the figure (passed to pl.figure())
            layoutkw: a dictionary of keyword arguments for the figure layout (passed to pl.subplots_adjust())
            textkw: a dictionary of keyword arguments for the text (passed to pl.text())
            max_bars: the maximum number of bars to show (else just plot the text)
            show: whether or not to show the figure
        """
        
        # Shorten variables into a data dict
        d = sc.mergedicts(self.results, self.plot_results)
        barkw  = sc.mergedicts(sc.objdict(width=0.95, alpha=0.7), barkw)
        textkw = sc.mergedicts(dict(horizontalalignment='center', c=ci_color), textkw)
        bbkw   = dict(facecolor='w', alpha=0.7, edgecolor='none') # For the text bounding box
        figkw  = sc.mergedicts(dict(figsize=(8,8)), figkw)
        layoutkw = sc.mergedicts(dict(top=0.90, bottom=0.08, right=0.98, hspace=0.6), layoutkw)
        too_many = d.n > max_bars # Check if we're asked to plot too many bars
        

        # Create the figure
        if fig is None:
            fig = pl.figure(**figkw)
        pl.subplots_adjust(**layoutkw)
    
        ## First figure: binomial distribution of expected appointments
        ax1 = pl.subplot(2,1,1)
        if not too_many:
            pl.bar(d.x, d.e_pmf, facecolor=dist_color, **barkw)
        pl.xlim([0, d.n])
        pl.ylabel('Probability')
        pl.xlabel('Number of appointments')
        sep = '\n' if wrap else ' ' # Choose between line break and space
        estr = to_str(d.expected)
        astr = to_str(d.actual)
        nstr = to_str(d.n)
        pl.title(f'Expected ($n_e=${estr}) vs. actual ($n_a=${astr}){sep}out of $n_t=${nstr} appointments\n\n')
    
        ## Calculate cdf
    
        # Two conditions depending on whether group is >/< expected ratio, below adds the shading in fig1a
        e_max = max(d.e_pmf)
        a_max = max(d.a_pmf)
        lt_actual = d.x<=d.actual
        if self.one_sided or (d.actual <= d.expected):
            rarea = d.x[lt_actual]
            yarea = d.e_pmf[lt_actual]
            plabel = '$P(n ≤ n_a)$'
        else:
            rarea = d.x[d.x>=d.actual]
            yarea = d.e_pmf[d.x>=d.actual]
            plabel = '$P(n ≥ n_a)$'
            
        if d.expected < d.n/2:
            xtext = d.n*0.9
            ha = 'right'
        else:
            xtext = d.n*0.1
            ha = 'left'
        
        label  = f'$f_e$ = {to_str(d.f_expected, 2)}\n'
        label += f'$f_a$ = {to_str(d.f_actual, 2)}\n'
        label += '\n'
        label += f'{plabel} = {to_str(d.cum_prob)}\n'
        label += f'$B$ = {to_str(d.bias)}'
    
        if not too_many:
            pl.bar(rarea, yarea, facecolor=cdf_color, **barkw)
        pl.text(xtext, e_max*1.2, label, c=ci_color, horizontalalignment=ha, verticalalignment='top').set_bbox(bbkw)
    
    
        ## Second plot: if we kept sampling from this distribution    
        ax2 = pl.subplot(2,1,2)
    
        if not too_many:
            pl.bar(d.x, d.a_pmf, facecolor=dist_color, **barkw)
            pl.bar(d.x[d.expected_low:d.expected_high+1], d.a_pmf[d.expected_low:d.expected_high+1], facecolor=cdf_color, **barkw)
        pl.xlim([0, d.n])
        pl.ylabel('Probability')
        pl.xlabel('Number of appointments')
        pl.title('Predicted distribution of future appointments\n\n')
    
        if d.actual < d.n/2:
            fairx = d.n*0.9
            ha = 'right'
        else:
            fairx = d.n*0.1
            ha = 'left'
        futurestr = '$P_{fut}$'
        pl.text(fairx, a_max, f'{futurestr} = {to_str(d.p_future)}', c=ci_color, horizontalalignment=ha).set_bbox(bbkw)
        
        
        dw = barkw.width/2
        for i,ax in enumerate([ax1, ax2]):
            
            # Set axis labels
            if   d.n <=  10: loc = mpl.ticker.MultipleLocator(1)
            elif d.n <=  20: loc = mpl.ticker.MultipleLocator(2)
            elif d.n <=  50: loc = mpl.ticker.MultipleLocator(5)
            elif d.n <= 100: loc = mpl.ticker.MultipleLocator(10)
            else:            loc = mpl.ticker.MaxNLocator(integer=True)
            ax.xaxis.set_major_locator(loc)
            ax.set_xlim([0-dw, d.n+dw])
            sc.boxoff(ax)
            
            # Plot 95% CI  values
            if i == 0:
                low  = d.expected_low
                high = d.expected_high
                val  = d.expected
                vmax = e_max
                pmf  = d.e_pmf
            else:
                low  = d.actual_low
                high = d.actual_high
                val  = d.actual
                vmax = a_max
                pmf  = d.a_pmf
            ax.fill_between([low-dw, high+dw], [1.2*vmax]*2, facecolor=ci_color, zorder=-10, alpha=0.05)
            ax.plot([low-dw, high+dw], [1.2*vmax]*2, c=ci_color, lw=2.0)
            ax.scatter(val, 1.2*vmax, 70, c=ci_color)
            ax.text(val, 1.3*vmax,'95% CI', c=ci_color, horizontalalignment='center')
            
            # Print text
            dy = 0.05*max(pmf)
            ire = int(np.round(d.expected))
            ira = int(np.round(d.actual))
            gap = abs(ire - ira) > d.n/20 # Don't plot both if they're too close together
            if gap or i == 0:
                ax.text(ire, dy+pmf[ire],'$n_e$', **textkw)
            if gap or i == 1: 
                ax.text(ira, dy+pmf[ira],'$n_a$', **textkw)
            
            ax.set_aspect(d.n/vmax*0.3)
            
        # Add frame labels
        if letters:
            for label,y in zip(['(a)','(b)'], [1, 0.5]):
                fig.text(0.03, y-0.05, label, fontsize=14)
                
        # Show a warning if too many bars
        if too_many:
            fig.text(0.5, 0.7, f'Cannot show bar chart for $n_t$ > {max_bars}', horizontalalignment='center', fontsize=14)
        
        if show:
            pl.show()
        
        return fig


def plot_bias(show=True, letters=True, display=True, **kwargs):
    """
    Script to simply plot the bias without creating a class instance; see BinomialBias for arguments
    
    **Example**::
        
        import binomialbias as bb
        bb.plot_bias(n=20, n_e=10, n_a=7)    
    """
    bb_keys = ['n', 'n_e', 'n_a', 'f_e', 'f_a', 'expected', 'actual']
    bb_kwargs = {k:kwargs.pop(k) for k in bb_keys if k in kwargs}
    B = BinomialBias(**bb_kwargs)
    B.plot(show=show, letters=letters, **kwargs)
    if display:
        B.display()
    return B


if __name__ == '__main__':
    B = plot_bias()