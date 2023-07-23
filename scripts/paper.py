'''
Generate the figures from the manuscript
'''

import sciris as sc
import pylab as pl
import binomialbias as bb

do_save = True
do_show = True
do_close = False

def make_fig(label, n, e, a):
    B = bb.BinomialBias(n=n, expected=e, actual=a)
    B.plot(show=False)
    if do_save:
        sc.savefig(f'{label}.png')
    return


def make_figs():
    ''' Make all figures for the paper '''
    figs = dict(
        fig1 = [10, 5, 2], # Coin toss
        fig2 = [12, 2, 2], # Die roll
        fig3 = [40, 20, 13], # VC selection
        fig6 = [38, 0.38, 2], # Senate selection
    )
    
    for fig,(n,e,a) in figs.items():
        print(f'Processing {fig}...')
        make_fig(fig, n, e, a)
        
    # Tidy up
    if do_show:
        pl.show()
    if do_close:
        pl.close()
        
    return
    


if __name__ == '__main__':
    make_figs()