'''
Classes and functions for calculating binomial bias
'''

import numpy as np
import scipy.stats as st
import sciris as sc
import pylab as pl
import matplotlib as mpl

pl.rc('figure', dpi=150)

__all__ = ['BinomialBias', 'plot_bias']


class BinomialBias(sc.prettyobj):
    
    def __init__(self, n=10, expected=5, actual=2, display=True, plot=False):
        '''
        
        ### UPDATE DOCSTRING!!!!
        
        
        Code to supplement Quantitative Assessment of University Discrimination -
        by Prof. P. A. Robinson, School of Physics, University of Sydney
        Python conversion by Dr. C. C. Kerr, Institute for Disease Modeling
    
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
            B = bb.BinomialBias(n=9, actual=3, expected=4)
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
        
        # Calculate the results
        self.calculate()
        if display:
            self.display()
        if plot:
            self.plot()
        
        return
    
    
    def calculate(self):
        ''' Calculate the bias '''
        
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
        bias = ((n-actual)/(n-expect))/(actual/expect)
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
        # future_low  = int(np.median([a_low,  e_low, e_high]))
        # future_high = int(np.median([a_high, e_low, e_high]))
    
        # Calculate p_future
        p_future = sum(a_pmf[e_low:e_high+1]) # +1 since used as an index
        # fair_round = round(p_future, 2) ## Add on PU text
        
        
        # Assemble into a results object
        self.results = sc.objdict()
        
        # Store inputs
        self.results.n = self.n
        self.results.actual = self.actual
        self.results.expected = self.expected
        self.results.expected_ratio = self.expected/self.n
        
        # Store outputs
        self.results.cumprob = cumprob
        self.results.bias = bias
        self.results.p_future = p_future
        self.results.expected_low = e_low
        self.results.expected_high = e_high
        
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


    def plot(self, fig=None, dist_color='cornflowerblue', cdf_color='darkblue', ci_color='k', show=True):
        '''
        Plot the results of the bias calculation
        '''
        
        def marea(x, y, fc='r', **kwargs):
            ''' Settings to replicate an area plot in Matlab '''
            return pl.fill_between(x, y1=y, y2=0, facecolor=fc, zorder=10, **kwargs)
    
    
        def mplot(x, y, **kwargs):
            ''' Settings to replicate a line plot in Matlab '''
            return pl.plot(x, y, zorder=20, **kwargs)
    
        def mbar(x, y, **kwargs):
            ''' Settings to replicate a line plot in Matlab '''
            kwargs['facecolor'] = kwargs.pop('c', None)
            return pl.bar(x, y, zorder=20, **kwargs)
        
        # Shorten variables into a data dict
        d = sc.mergedicts(self.results, self.plot_results)
        barkw = sc.objdict(width=0.95, alpha=0.7)
        tkw = sc.objdict(horizontalalignment='center', c=ci_color)
        

        #%% Create the figure
        if fig is None:
            fig = pl.figure(figsize=(8,8))
        pl.subplots_adjust(top=0.90, bottom=0.08, right=0.98, hspace=0.6)
    
        ## First figure: binomial distribution of expected appointments
        ax1 = pl.subplot(2,1,1)
        pl.bar(d.x, d.e_pmf, facecolor=dist_color, **barkw)
        # pl.plot(d.x, d.e_pmf, c='k', lw=1.5)
        pl.xlim([0, d.n])
        pl.ylabel('Probability')
        pl.xlabel('Number of appointments')
        pl.title(f'Expected ($n_E$={d.expected}) vs. actual ($n_A$={d.actual}) appointments\n\n')
    
        ## Calculate cdf
    
        #Two conditions depending on whether group is >/< expected ratio, below adds the shading in fig1a
        e_max = max(d.e_pmf)
        a_max = max(d.a_pmf)
        lt_actual = d.x<=d.actual
        if d.actual <= d.expected:
            rarea = d.x[lt_actual]
            yarea = d.e_pmf[lt_actual]
            xtext = d.n*0.1
            label = '$P(n ≤ n_A)$'
            ha = 'left'
        else:
            rarea = d.x[d.x>=d.actual]
            yarea = d.e_pmf[d.x>=d.actual]
            xtext = d.n*0.9
            label = '$P(n ≥ n_A)$'
            ha = 'right'
            
        label += f' = {d.cumprob:0.3f}'
        label += '\n'
        label += f'Bias = {d.bias:0.2n}'
    
        pl.bar(rarea, yarea, facecolor=cdf_color, **barkw)
        pl.text(xtext, e_max, label, c=ci_color, horizontalalignment=ha)
    
        # dye = 0.05*max(d.e_pmf)
        # pl.text(d.expected, dye+d.e_pmf[d.expected],'$n_E$', **tkw)
        # if d.expected != d.actual:
        #     pl.text(d.actual, dye+d.e_pmf[d.actual],'$n_A$', **tkw)
        
    
        ## Second plot: if we kept sampling from this distribution    
        ax2 = pl.subplot(2,1,2)
    
        pl.bar(d.x, d.a_pmf, facecolor=dist_color, **barkw)
        pl.bar(d.x[d.expected_low:d.expected_high+1], d.a_pmf[d.expected_low:d.expected_high+1], facecolor=cdf_color, **barkw)
        pl.xlim([0, d.n])
        pl.ylabel('Probability')
        pl.xlabel('Number of appointments')
        pl.title('Expected distribution of future appointments\n\n', fontweight='bold')
    
        if d.actual < d.n/2:
            fairx = d.n*0.9
            ha = 'right'
        else:
            fairx = d.n*0.1
            ha = 'left'
        futurestr = '$P_{future}$'
        pl.text(fairx, a_max, f'{futurestr} = {d.p_future:0.3f}', c=ci_color, horizontalalignment=ha)
        
        
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
            ax.text(d.expected, dy+pmf[d.expected],'$n_E$', **tkw)
            if d.expected != d.actual:
                ax.text(d.actual, dy+pmf[d.actual],'$n_A$', **tkw)
        
        if show:
            pl.show()
        
        return fig


def plot_bias(n=10, expected=5, actual=6, show=True):
    '''
    Script
    '''
    B = BinomialBias(n=n, expected=expected, actual=actual)
    fig = B.plot(show=show)
    return fig


if __name__ == '__main__':
    B = plot_bias()
    pl.show()