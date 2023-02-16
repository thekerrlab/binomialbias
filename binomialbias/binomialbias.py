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
    
    def __init__(self, n=10, actual=2, expected=5, display=True, plot=False):
        '''
        Code to supplement Quantitative Assessment of University Discrimination -
        by Prof. P. A. Robinson, School of Physics, University of Sydney
        Python conversion by Dr. C. C. Kerr, Institute for Disease Modeling
    
        Args:
            n (int): The total number of appointments
            actual (int/float): Actual number appointments of a group (either proportion or total number)
            expected (int/float): Expected appointments of a group given a fair process (either proportion or total number)
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
        
        eprop = expect/n # Expected proportion of target group
        aprop = actual/n
        x = np.arange(n+1) # X-axis: all possible samples
        pmf = st.binom.pmf(x, n, eprop) # Binomial distribution
        yunb = st.binom.pmf(x, n, aprop)
    
        # Calculation of the preference ratio
        # (n-actual)/(n-expected) - ratio for other group
        # actual/expected - ratio for relative proportion
        bias = ((n-actual)/(n-expect))/(actual/expect)
        
        # Shorten variables
        # x  = self.x
        # pmf  = self.pmf
        # ra = self.actual
        # k  = self.expected
        # f  = self.eprop
        
        ncdf = sum(pmf[x<=actual])
        ncdfround = sc.sigfig(ncdf, 2)
        
        #Gaussian CI approximation
        bnpMean = n*eprop
        bnpSTD = np.sqrt(n*eprop*(1-eprop))
    
        #3 std 99.7# CI
        lowBnd2 = bnpMean-3*bnpSTD
        hiBnd2 = bnpMean+3*bnpSTD
    
        #2 std or 95% CI
        lowBnd = bnpMean-2*bnpSTD
        hiBnd = bnpMean+2*bnpSTD
    
        # Ceil the lower bound of CI -- Integer value of individuals
        lowBnd2 = np.ceil(lowBnd2)
        lowBnd = np.ceil(lowBnd)
    
        # Floor the upper bound of CI -- Integer value of individuals
        hiBnd2 = np.floor(hiBnd2)
        hiBnd = np.floor(hiBnd)
    
        # Catching for values over/under -- we cannot have negative individuals or
        # more than the population
        if lowBnd2 < 0:
            lowBnd2 = 0
    
        if lowBnd < 0:
            lowBnd = 0
    
        if hiBnd2 > n:
            hiBnd2 = n
    
        if hiBnd > n:
            hiBnd = n
        
        
        bnpMean = n*aprop
        bnpSTD = np.sqrt(n*aprop*(1-aprop))
    
        lowBndR = bnpMean-2*bnpSTD
        hiBndR = bnpMean+2*bnpSTD
        lowBndR = round(lowBndR)
        hiBndR = round(hiBndR)
    
        # Catching for values over/under
        if lowBndR < 0:
            lowBndR = 0
    
        if hiBndR > n:
            hiBndR = n
        
        lowBnd = int(lowBnd)
        hiBnd = int(hiBnd)
        U = sum(yunb[lowBnd:hiBnd+1])
        PUround = sc.sigfig(U, 2) ## Add on PU text
        
        
        
        # Assemble into a results object
        self.results = sc.objdict()
        self.results.cdf = ncdfround
        self.results.bias = bias
        self.results.fairness = U
        self.results.low = lowBnd
        self.results.high = hiBnd
        
        # Other things
        self.x = x
        self.pmf = pmf
        self.yunb = yunb
        self.PUround = PUround
        self.lowBndR = lowBndR
        self.hiBndR = hiBndR
        
        return self.results
    
    
    def display(self):
        ''' Display the results of the calculation '''
        print(self.results)
        return


    def plot(self, fig=None):
        '''
        Plot the results of the bias calculation
        '''
        
        def marea(x, y, fc='r', **kwargs):
            return pl.fill_between(x, y1=y, y2=0, facecolor=fc, zorder=10, **kwargs)
    
    
        def mplot(x, y, *args, **kwargs):
            return pl.plot(x, y, zorder=20, **kwargs)
        
        # Shorten variables
        n  = self.n
        r  = self.x
        y  = self.pmf
        ra = self.actual
        k  = self.expected
        # f  = self.eprop
        
        # TEMP
        ncdfround = self.results.cdf
        lowBnd = self.results.low
        hiBnd = self.results.high
        yunb = self.yunb
        PUround = self.PUround
        lowBndR = self.lowBndR
        hiBndR = self.hiBndR
        
    
        

        #%% Create the figure
        if fig is None:
            fig = pl.figure(figsize=(8,6))
        pl.subplots_adjust(top=0.94, bottom=0.08, right=0.98, hspace=0.4)
        pl.figtext(0.02, 0.97, '(a)', fontsize=12)
        pl.figtext(0.02, 0.47, '(b)', fontsize=12)
    
        ## First figure binomial distribution of expected appointments
        pl.subplot(2,1,1)
        pl.plot(self.x, self.pmf, c='k', lw=1.5)
        pl.xlim([0, self.n])
        pl.ylabel(r'$P_F(r)$') # FIX
        pl.xlabel('r') # FIX
    
        ## Calculate cdf
        mplot([ra, ra], [0, y[r==ra][0]], c='r', lw=2.0)
    
        #Two conditions depending on whether group is >/< expected ratio, below adds the shading in fig1a
        if ra <= k:
            rarea = r[r<=ra]
            yarea = y[r<=ra]
            xtext = n/8+0.5
            ytext = 3.5*max(y)/4
        else:
            rarea = r[r>=ra]
            yarea = y[r>=ra]
            xtext = 3*n/4
            ytext = 3*max(y)/4
    
        marea(rarea, yarea, 'r')
        pl.text(xtext, ytext, f'$cdf(r_a)$ = {ncdfround}', c='r', horizontalalignment='center')
    
        #Add vertical line and r_a
        pl.plot([ra, ra],[0.7*max(y)/4, 0.7*max(y)/2], c='r', lw=1.0)
        pl.text(ra+0.2, 0.9*max(y)/2,'$r_a$' , c='r', horizontalalignment='center')
    
    
        ## Plot 95% CI  values
    
        # Now plot the CI lines
    
        mplot([lowBnd, lowBnd], [0, y[r==lowBnd][0]],c='b',lw=2.0)
        mplot([hiBnd, hiBnd], [0, y[r==hiBnd][0]],c='b',lw=2.0)
    
        mplot([lowBnd, hiBnd], [1.1*max(y), 1.1*max(y)],c='b',lw=2.0)
        pl.scatter(k, 1.1*max(y), 70, c='b')
        pl.text(k, 1.2*max(y),'95% CI', c='b', horizontalalignment='center')
    
        pl.grid(True, axis='y')
        pl.minorticks_on()
        sc.boxoff()
        sc.setylim()
    
        # bigF = ra/n
        r = np.arange(n+1) #sampling
        
    
        pl.subplot(2,1,2)
    
        mplot(r,yunb,c='k',lw=1.5)
        pl.xlim([0, n])
        pl.ylabel('$P_S(R)$')
        pl.xlabel('R')
    
        ## Plot 95% CI values of a resampled appointments
    
        mplot([lowBndR, hiBndR], [1.1*max(yunb), 1.1*max(yunb)],c='r',lw=2.0)
        pl.scatter(ra, 1.1*max(yunb), 70, c='r')
        pl.text(ra,1.2*max(yunb),'95% CI',c='r',horizontalalignment='center')
    
        marea(r[lowBnd:hiBnd+1], yunb[lowBnd:hiBnd+1], 'b')
    
        #U = trapz(r(lowBnd+1:hiBnd+1),yunb(lowBnd+1:hiBnd+1)) #Calc U using integration # As defined in the appendix
    
        if ra < n/2:
            pl.text(5*n/8, 3*max(yunb)/4,f'U = {PUround}',c='b',horizontalalignment='center')
        else:
            pl.text(n/4, 3*max(yunb)/4,f'U = {PUround}',c='b',horizontalalignment='center')
    
        pl.grid(True, axis='y')
        pl.minorticks_on()
        sc.boxoff()
        sc.setylim()
        
        return fig


def plot_bias(n=10, actual=2, expected=3):
    '''
    Script
    '''
    B = BinomialBias(n=n, actual=actual, expected=expected, plot=True)
    # B.calculate()
    # B.plot()
    return B


if __name__ == '__main__':
    B = plot_bias()