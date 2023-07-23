'''
Classes and functions for calculating binomial bias
'''

import numpy as np
import scipy.stats as st
import sciris as sc
import pylab as pl
import matplotlib as mpl


__all__ = ['BinomialBias', 'plot_bias']


class BinomialBias(sc.prettyobj):
    
    def __init__(self, n=20, expected=10, actual=7, display=False, plot=False):
        '''
        Analysis for the paper "Quantitative assessment of discrimination in 
        appointments to senior Australian university positions" -
        by Prof. P. A. Robinson, School of Physics, University of Sydney;
        Python conversion by Dr. C. C. Kerr, Institute for Disease Modeling.
    
        Args:
            n (int): The total number of appointments
            expected (int/float): Expected appointments of a group given a fair process (either proportion or total number)
            actual (int/float): Actual number appointments of a group (either proportion or total number)
            display (bool): whether to display the results
            plot (bool): whether to plot the results
            
        Results are stored in "results", which has the following fields:
            ci: 95% confidence interval for individuals given a fair process
            cdf: Cumulative distribution function of ra or less appointments
            bias: Preference ratio the estimate of the disparity in how two groups are viewed by selectors
            p_future: Probability of unbiased selection; values much less than 1 do imply bias; values < 0.1 should be cause for serious concern and values < 0.01 should provoke urgent action.
    
        **Example**::
            
            import binomialbias as bb
            B = bb.BinomialBias(n=9, expected=4, actual=3)
            B.plot()
        '''
        
        def is_prop(val):
            ''' Check if a value is a proportion or an absolute number '''
            return (val <= 1) and isinstance(val, float)
        
        # Handle inputs
        if is_prop(actual):   actual   *= n
        if is_prop(expected): expected *= n
        self.n        = n
        self.actual   = actual
        self.expected = expected
        
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
        ''' Validate the inputs; called automatically on initialization '''
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
            errormsg = f'Actual appointments ({self.expected}) must be less than or equal to total appointments ({self.n})'
            raise ValueError(errormsg)
        return
    
    
    def calculate(self):
        ''' Calculate the statistics; called automatically on initialization '''
        
        # Shorten variables
        n      = self.n
        actual = self.actual
        expect = self.expected
        
        x     = np.arange(n+1) # X-axis: all possible samples
        eprop = expect/n # Expected proportion of target group
        aprop = actual/n # Actual proportion of target group
        e_pmf = st.binom.pmf(x, n, eprop) # Binomial distribution
        a_pmf = st.binom.pmf(x, n, aprop)
    
        # Calculation of the preference ratio
        # (n-actual)/(n-expected) - ratio for other group
        # actual/expected - ratio for relative proportion
        if actual > 0:
            bias = ((n-actual)/(n-expect))/(actual/expect)
        else:
            bias = np.inf
        if actual <= expect:
            cumprob = sum(e_pmf[x<=actual])
        else:
            cumprob = sum(e_pmf[x>=actual])
        
        # Gaussian CI approximation
        e_mean = n*eprop
        e_std = np.sqrt(e_mean*(1-eprop))

        # Calculate bounds
        e_low  = int(max(0, np.ceil(e_mean-2*e_std)))
        e_high = int(min(n, np.floor(e_mean+2*e_std)))

        ## Actual
        a_mean = n*aprop
        a_std  = np.sqrt(a_mean*(1-aprop))

        # Calculate bounds
        a_low  = int(max(0, np.ceil(a_mean-2*a_std)))
        a_high = int(min(n, np.floor(a_mean+2*a_std)))
    
        # Calculate p_future
        p_future = sum(a_pmf[e_low:e_high+1]) # +1 since used as an index
        
        # Assemble into a results object
        self.results = sc.objdict()
        
        # Store inputs
        self.results.n = self.n
        self.results.actual = self.actual
        self.results.expected = self.expected
        self.results.expected_ratio = self.expected/self.n
        
        # Store outputs
        self.results.expected_low = e_low
        self.results.expected_high = e_high
        self.results.cumprob = cumprob
        self.results.bias = bias
        self.results.p_future = p_future
        
        # Other things, used for plotting
        pr = sc.objdict()
        pr.x = x
        pr.e_pmf = e_pmf
        pr.a_pmf = a_pmf
        # pr.fair_round  = fair_round
        pr.actual_low  = a_low
        pr.actual_high = a_high
        self.plot_results = pr
        
        return self.results
    
    
    def display(self):
        ''' Display the results of the calculation '''
        print(self.results)
        return


    def plot(self, dist_color='cornflowerblue', cdf_color='darkblue', ci_color='k', 
             fig=None, barkw=None, figkw=None, layoutkw=None, textkw=None, show=True):
        '''
        Plot the results of the bias calculation
        
        Args:
            dist_color: the color of the full distribution
            cdf_color: the color of the part of the distribution being integrated
            ci_color: the color of the confidence bounds
            fig: if supplied, plot using this figure
            barkw: a dictionary of keyword arguments for the bar plots (passed to pl.bar())
            figkw: a dictionary of keyword arguments for the figure (passed to pl.figure())
            layoutkw: a dictionary of keyword arguments for the figure layout (passed to pl.subplots_adjust())
            textkw: a dictionary of keyword arguments for the text (passed to pl.text())
            show: whether or not to show the figure
        '''
        
        # Shorten variables into a data dict
        d = sc.mergedicts(self.results, self.plot_results)
        barkw  = sc.mergedicts(sc.objdict(width=0.95, alpha=0.7), barkw)
        textkw = sc.mergedicts(dict(horizontalalignment='center', c=ci_color), textkw)
        bbkw   = dict(facecolor='w', alpha=0.7, edgecolor='none') # For the text bounding box
        figkw  = sc.mergedicts(dict(figsize=(8,8)), figkw)
        layoutkw = sc.mergedicts(dict(top=0.90, bottom=0.08, right=0.98, hspace=0.6), layoutkw)
        

        #%% Create the figure
        if fig is None:
            fig = pl.figure(**figkw)
        pl.subplots_adjust(**layoutkw)
    
        ## First figure: binomial distribution of expected appointments
        ax1 = pl.subplot(2,1,1)
        pl.bar(d.x, d.e_pmf, facecolor=dist_color, **barkw)
        pl.xlim([0, d.n])
        pl.ylabel('Probability')
        pl.xlabel('Number of appointments')
        pl.title(f'Expected ($n_E=${d.expected:0.0f}) vs. actual ($n_A=${d.actual:0.0f}) out of {d.n:0.0f} appointments\n\n')
    
        ## Calculate cdf
    
        # Two conditions depending on whether group is >/< expected ratio, below adds the shading in fig1a
        e_max = max(d.e_pmf)
        a_max = max(d.a_pmf)
        lt_actual = d.x<=d.actual
        if d.actual <= d.expected:
            rarea = d.x[lt_actual]
            yarea = d.e_pmf[lt_actual]
            label = '$P(n ≤ n_A)$'
        else:
            rarea = d.x[d.x>=d.actual]
            yarea = d.e_pmf[d.x>=d.actual]
            label = '$P(n ≥ n_A)$'
            
        if d.expected < d.n/2:
            xtext = d.n*0.9
            ha = 'right'
        else:
            xtext = d.n*0.1
            ha = 'left'
            
        label += f' = {d.cumprob:0.3f}'
        label += '\n'
        label += f'Bias = {d.bias:0.3n}'
    
        pl.bar(rarea, yarea, facecolor=cdf_color, **barkw)
        pl.text(xtext, e_max*0.95, label, c=ci_color, horizontalalignment=ha).set_bbox(bbkw)
    
    
        ## Second plot: if we kept sampling from this distribution    
        ax2 = pl.subplot(2,1,2)
    
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
        futurestr = '$P_{future}$'
        pl.text(fairx, a_max, f'{futurestr} = {d.p_future:0.3f}', c=ci_color, horizontalalignment=ha).set_bbox(bbkw)
        
        
        dw = barkw.width/2
        for i,ax in enumerate([ax1, ax2]):
            if   d.n <=  10: loc = mpl.ticker.MultipleLocator(1)
            elif d.n <=  20: loc = mpl.ticker.MultipleLocator(2)
            elif d.n <=  50: loc = mpl.ticker.MultipleLocator(5)
            elif d.n <= 100: loc = mpl.ticker.MultipleLocator(10)
            else:            loc = mpl.ticker.MaxNLocator(integer=True)
            ax.xaxis.set_major_locator(loc)
            ax.set_xlim([0-dw, d.n+dw])
            sc.boxoff(ax)
            
            ## Plot 95% CI  values
            if i == 0:
                low  = d.expected_low
                high = d.expected_high
                val  = d.expected
                vmax = e_max
                pmf = d.e_pmf
            else:
                low  = d.actual_low
                high = d.actual_high
                val  = d.actual
                vmax = a_max
                pmf = d.a_pmf
            ax.fill_between([low-dw, high+dw], [1.2*vmax]*2, facecolor=ci_color, zorder=-10, alpha=0.05)
            ax.plot([low-dw, high+dw], [1.2*vmax]*2, c=ci_color, lw=2.0)
            ax.scatter(val, 1.2*vmax, 70, c=ci_color)
            ax.text(val, 1.3*vmax,'95% CI', c=ci_color, horizontalalignment='center')
            
            dy = 0.05*max(pmf)
            ire = int(np.round(d.expected))
            ira = int(np.round(d.actual))
            gap = abs(ire - ira) > d.n/20 # Don't plot both if they're too close together
            if gap or i == 0:
                ax.text(ire, dy+pmf[ire],'$n_E$', **textkw)
            if gap or i == 1: 
                ax.text(ira, dy+pmf[ira],'$n_A$', **textkw)
            
            ax.set_aspect(d.n/vmax*0.3)
        
        if show:
            pl.show()
        
        return fig


def plot_bias(n=20, expected=10, actual=7, show=True, display=True):
    '''
    Script to simply plot the bias without creating a class instance; see BinomialBias for arguments
    '''
    B = BinomialBias(n=n, expected=expected, actual=actual)
    B.plot(show=show)
    if display:
        B.display()
    return B


if __name__ == '__main__':
    B = plot_bias()