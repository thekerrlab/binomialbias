'''
Simple tests of plotting
'''

import sciris as sc
import binomialbias as bb


def test_plotting(show=False):
    ''' Test several different plotting options '''
    
    sc.options(interactive=show)
    
    out = []
    for (n,e,a) in [
            [ 20, 10,  7],
            [ 10,  5,  5],
            [ 30, 15, 20],
            [100, 50, 30],
            ]:
        B = bb.BinomialBias(n=n, expected=e, actual=a)
        B.plot(show=show)
        out.append(B)
        
    return out


if __name__ == '__main__':
    out = test_plotting(show=True)

    