'''
Classes and functions for calculating binomial bias
'''

import numpy as np
import scipy.stats as st
import sciris as sc
import pylab as pl

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
            fairness: Probability of unbiased selection; values much less than 1 do imply bias; values < 0.1 should be cause for serious concern and values < 0.01 should provoke urgent action.
    
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
        ncdf = sum(e_pmf[x<=actual])
        ncdfround = round(ncdf, 2)
        
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
    
        # Calculate fairness
        fairness = sum(a_pmf[a_low:a_high+1])
        fair_round = round(fairness, 2) ## Add on PU text
        
        
        # Assemble into a results object
        self.results = sc.objdict()
        
        # Store inputs
        self.results.n = self.n
        self.results.actual = self.actual
        self.results.expected = self.expected
        
        # Store outputs
        self.results.cumprob = ncdfround
        self.results.bias = bias
        self.results.fairness = fairness
        self.results.expected_low = e_low
        self.results.expected_high = e_high
        
        # Other things, used for plotting
        pr = sc.objdict()
        pr.x = x
        pr.e_pmf = e_pmf
        pr.a_pmf = a_pmf
        pr.fair_round  = fair_round
        pr.actual_low  = a_low
        pr.actual_high = a_high
        self.plot_results = pr
        
        return self.results
    
    
    def display(self):
        ''' Display the results of the calculation '''
        print(self.results)
        return


    def plot(self, fig=None, color1='r', color2='b'):
        '''
        Plot the results of the bias calculation
        '''
        
        def marea(x, y, fc='r', **kwargs):
            ''' Settings to replicate an area plot in Matlab '''
            return pl.fill_between(x, y1=y, y2=0, facecolor=fc, zorder=10, **kwargs)
    
    
        def mplot(x, y, **kwargs):
            ''' Settings to replicate a line plot in Matlab '''
            return pl.plot(x, y, zorder=20, **kwargs)
        
        # Shorten variables into a data dict
        d = sc.mergedicts(self.results, self.plot_results)
        
        # Shorten variables
        # n  = self.n
        # r  = self.x
        # y  = self.pmf
        # ra = self.actual
        # k  = self.expected
        # f  = self.eprop
        
        # TEMP
        # ncdfround = self.results.cdf
        # lowBnd = self.results.expected_low
        # hiBnd = self.results.expected_high
        # yunb = self.yunb
        # PUround = self.PUround
        # lowBndR = self.lowBndR
        # hiBndR = self.hiBndR
        
    
        

        #%% Create the figure
        if fig is None:
            fig = pl.figure(figsize=(8,6))
        pl.subplots_adjust(top=0.94, bottom=0.08, right=0.98, hspace=0.4)
        pl.figtext(0.02, 0.97, '(a)', fontsize=12)
        pl.figtext(0.02, 0.47, '(b)', fontsize=12)
    
        ## First figure: binomial distribution of expected appointments
        pl.subplot(2,1,1)
        pl.plot(d.x, d.e_pmf, c='k', lw=1.5)
        pl.xlim([0, d.n])
        pl.ylabel(r'$P_F(r)$') # FIX
        pl.xlabel('r') # FIX
    
        ## Calculate cdf
        mplot([d.actual, d.actual], [0, d.e_pmf[d.x==d.actual][0]], c=color1, lw=2.0)
    
        #Two conditions depending on whether group is >/< expected ratio, below adds the shading in fig1a
        if d.actual <= d.expected:
            rarea = d.x[d.x<=d.actual]
            yarea = d.e_pmf[d.x<=d.actual]
            xtext = d.n/8+0.5
            ytext = 3.5*max(d.e_pmf)/4
        else:
            rarea = d.x[d.x>=d.actual]
            yarea = d.e_pmf[d.x>=d.actual]
            xtext = 3*d.n/4
            ytext = 3*max(d.e_pmf)/4
    
        marea(rarea, yarea, color1)
        pl.text(xtext, ytext, f'$cdf(r_a)$ = {d.cumprob}', c=color1, horizontalalignment='center')
    
        #Add vertical line and r_a
        pl.plot([d.actual, d.actual],[0.7*max(d.e_pmf)/4, 0.7*max(d.e_pmf)/2], c=color1, lw=1.0)
        pl.text(d.actual+0.2, 0.9*max(d.e_pmf)/2,'$r_a$' , c=color1, horizontalalignment='center')
    
    
        ## Plot 95% CI  values
    
        # Now plot the CI lines
    
        mplot([d.expected_low, d.expected_low], [0, d.e_pmf[d.x==d.expected_low][0]],c=color2,lw=2.0)
        mplot([d.expected_high, d.expected_high], [0, d.e_pmf[d.x==d.expected_high][0]],c=color2,lw=2.0)
    
        mplot([d.expected_low, d.expected_high], [1.1*max(d.e_pmf), 1.1*max(d.e_pmf)],c=color2,lw=2.0)
        pl.scatter(d.expected, 1.1*max(d.e_pmf), 70, c=color2)
        pl.text(d.expected, 1.2*max(d.e_pmf),'95% CI', c=color2, horizontalalignment='center')
    
        pl.grid(True, axis='y')
        pl.minorticks_on()
        sc.boxoff()
        sc.setylim()
    
        # bigF = ra/n
        #r = np.arange(n+1) #sampling
        
    
        pl.subplot(2,1,2)
    
        mplot(d.x,d.a_pmf,c='k',lw=1.5)
        pl.xlim([0, d.n])
        pl.ylabel('$P_S(R)$')
        pl.xlabel('R')
    
        ## Plot 95% CI values of a resampled appointments
    
        mplot([d.actual_low, d.actual_high], [1.1*max(d.a_pmf), 1.1*max(d.a_pmf)],c=color1,lw=2.0)
        pl.scatter(d.actual, 1.1*max(d.a_pmf), 70, c=color1)
        pl.text(d.actual,1.2*max(d.a_pmf),'95% CI',c=color1,horizontalalignment='center')
    
        marea(d.x[d.expected_low:d.expected_high+1], d.a_pmf[d.expected_low:d.expected_high+1], color2)
    
        #U = trapz(r(lowBnd+1:hiBnd+1),yunb(lowBnd+1:hiBnd+1)) #Calc U using integration # As defined in the appendix
    
        if d.actual < d.n/2:
            pl.text(5*d.n/8, 3*max(d.a_pmf)/4,f'U = {d.fair_round}',c=color2,horizontalalignment='center')
        else:
            pl.text(d.n/4, 3*max(d.a_pmf)/4,f'U = {d.fair_round}',c=color2,horizontalalignment='center')
    
        pl.grid(True, axis='y')
        pl.minorticks_on()
        sc.boxoff()
        sc.setylim()
        
        return fig


def plot_bias(n=10, expected=4, actual=3):
    '''
    Script
    '''
    B = BinomialBias(n=n, expected=expected, actual=actual, plot=True)
    return B


if __name__ == '__main__':
    B = plot_bias()