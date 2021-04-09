import numpy as np
import scipy.stats as st
import sciris as sc
import pylab as pl

pl.rc('figure', dpi=150)

def binomial_discrimination(n=9, ra=3, rbar=4):
    '''
    Code to supplement Objective Assessment of University Discrimination -
    by Prof. P. A. Robinson, School of Physics, University of Sydney
    Python conversion by Dr. C. C. Kerr, Institute for Disease Modeling

    Input:
    n - The total number of appointments
    ra - Actual appointments of a group
    rbar - Expected number of appointments expected given a fair process

    Output:
    CI - 95% Confidence interval for individuals given a fair process
    cdfra - Cumulative distribution function of ra or less appointments
    B - Preference ratio the estimate of the disparity in how two groups are viewed by selectors
    U - Probability of unbiased selection numbers much less than 1 do imply bias and U < 0.1 should be cause for serious concern and U < 0.01 should provoke urgent action.

    Example:
    The below code will generate figure 1 of the paper
    '''
    # n = 9 #40 possible appointments
    # rbar = 4 #An expected 50# of appointments
    # ra = 3 #13 actual appointments were observed

    def siground(x, n):
        """ Return 'x' rounded to 'n' significant digits. """
        return round(x, int(n-np.ceil(np.log10(abs(x)))))

    def marea(x, y, fc='r', **kwargs):
        return pl.fill_between(x, y1=y, y2=0, facecolor=fc, zorder=10, **kwargs)



    def mtext(x, y, string, *args, **kwargs):
        return pl.text(x, y, string, **kwargs)

    def mplot(x, y, *args, **kwargs):
        return pl.plot(x, y, zorder=20, **kwargs)

    def mscatter(x, y, *args, **kwargs):
        return pl.scatter(x, y, **kwargs)

    f = rbar/n
    r = np.arange(n+1) #sampling
    y = st.binom.pmf(r,n,f) #binomial distn #FIX
    k = f*n

    #Calculation of the preference ratio
    #(n-ra)./(n-rbar) - ratio for other group
    #ra./rbar - ratio for relative proportion
    B = ((n-ra)/(n-rbar))/(ra/rbar)


    #%% Create the figure
    fig = pl.figure(figsize=(8,6))
    pl.subplots_adjust(top=0.94, bottom=0.08, right=0.98, hspace=0.4)
    pl.figtext(0.02, 0.97, '(a)', fontsize=12)
    pl.figtext(0.02, 0.47, '(b)', fontsize=12)

    ## First figure binomial distribution of expected appointments
    ax1 = pl.subplot(2,1,1)
    pl.plot(r, y, c='k', lw=1.5)
    pl.xlim([0, n])
    pl.ylabel(r'$P_F(r)$')
    pl.xlabel('r')

    ## Calc cdf
    mplot([ra, ra], [0, y[r==ra][0]],c='r',lw=2.0)

    #Two conditions depending on whether group is >/< expected ratio, below adds the shading in fig1a
    if ra <= k:
        rarea = r[r<=ra]
        yarea = y[r<=ra]
        xtext = n/8+0.5
        ytext = 3*max(y)/4
    else:
        rarea = r[r>=ra]
        yarea = y[r>=ra]
        xtext = 3*n/4
        ytext = 3*max(y)/4

    ncdf = sum(y[r<=ra])
    ncdfround = siground(ncdf, 2)
    marea(rarea, yarea, 'r')
    pl.text(xtext, ytext, f'$cdf(r_a)$ = {ncdfround}', c='r', horizontalalignment='center')

    #Save cdf for output
    cdfra = ncdfround

    #Add vertical line and r_a
    pl.plot([ra, ra],[0.7*max(y)/4, 0.7*max(y)/2], c='r', lw=1.0)
    mtext(ra+0.2, 0.9*max(y)/2,'$r_a$' , c='r', horizontalalignment='center')


    ## Plot 95% CI  values

    #Gaussian CI approximation
    bnpMean = n*f
    bnpSTD = np.sqrt(n*f*(1-f))

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

    # Now plot the CI lines

    mplot([lowBnd, lowBnd], [0, y[r==lowBnd][0]],c='b',lw=2.0)
    mplot([hiBnd, hiBnd], [0, y[r==hiBnd][0]],c='b',lw=2.0)

    mplot([lowBnd, hiBnd], [1.1*max(y), 1.1*max(y)],c='b',lw=2.0)
    mscatter(k, 1.1*max(y), 70, c='b')
    mtext(k,1.2*max(y),'95% CI', c='b', horizontalalignment='center')

    pl.grid(True, axis='y')
    pl.minorticks_on()
    sc.boxoff()
    sc.setylim()


    CI = [lowBnd, hiBnd]

    #Uncomment below for 99.7# CI
    # plot([lowBnd2 lowBnd2], [0 y(r==lowBnd2)],'r',lw=2.0)
    # plot([hiBnd2 hiBnd2], [0 y(r==hiBnd2)],'r',lw=2.0)
    #
    # plot([lowBnd2 hiBnd2], [1.15.*max(y) 1.15.*max(y)],'r',lw=2.0)
    # text(k,1.1.*max(y),'99.7#','Color','r',horizontalalignment='center')

    ## Plot the unbiased ratio fig 1b
    #Inferred distribution of the numbers of appointments if the selectors made multiple new selections

    bigF = ra/n
    r = np.arange(n+1) #sampling
    yunb = st.binom.pmf(r,n,bigF)

    pl.subplot(2,1,2)

    mplot(r,yunb,c='k',lw=1.5)
    pl.xlim([0, n])
    pl.ylabel('$P_S(R)$')
    pl.xlabel('R')

    ## Plot 95% CI values of a resampled appointments

    bnpMean = n*bigF
    bnpSTD = np.sqrt(n*bigF*(1-bigF))

    lowBndR = bnpMean-2*bnpSTD
    hiBndR = bnpMean+2*bnpSTD
    lowBndR = round(lowBndR)
    hiBndR = round(hiBndR)

    # Catching for values over/under
    if lowBndR < 0:
        lowBndR = 0

    if hiBndR > n:
        hiBndR = n


    mplot([lowBndR, hiBndR], [1.1*max(yunb), 1.1*max(yunb)],c='r',lw=2.0)
    mscatter(ra, 1.1*max(yunb), 70, c='r')
    mtext(ra,1.2*max(yunb),'95% CI',c='r',horizontalalignment='center')

    lowBnd = int(lowBnd)
    hiBnd = int(hiBnd)

    marea(r[lowBnd:hiBnd+1], yunb[lowBnd:hiBnd+1], 'b')

    #U = trapz(r(lowBnd+1:hiBnd+1),yunb(lowBnd+1:hiBnd+1)) #Calc U using integration # As defined in the appendix
    U = sum(yunb[lowBnd:hiBnd+1])
    PUround = siground(U, 2) ## Add on PU text

    if ra < n/2:
        mtext(5*n/8, 3*max(yunb)/4,f'U = {PUround}',c='b',horizontalalignment='center')
    else:
        mtext(n/4, 3*max(yunb)/4,f'U = {PUround}',c='b',horizontalalignment='center')

    pl.grid(True, axis='y')
    pl.minorticks_on()
    sc.boxoff()
    sc.setylim()
    pl.show()

    return [CI,cdfra,B,U]


if __name__ == '__main__':
    CI,cdfra,B,U = binomial_discrimination()