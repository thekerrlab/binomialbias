'''
Simple tests of plotting
'''

import sciris as sc
import binomialbias as bb

sc.options(interactive=False)

def test_plotting():
    out = []
    for (n,e,a) in [
            [ 10, 5, 5],
            [ 30, 15, 20],
            [100, 50, 30],
            ]:
        B = bb.BinomialBias(n=n, expected=e, actual=a)
        B.plot()
        out.append(B)
    return out

if __name__ == '__main__':
    out = test_plotting()

    