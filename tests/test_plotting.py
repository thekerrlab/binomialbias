'''
Simple tests of the app
'''

import binomialbias as bb

def test_plotting():
    for (n,e,a) in [
            [ 10, 5, 5],
            [ 30, 15, 20],
            [100, 50, 30],
            ]:
        B = bb.BinomialBias(n=n, expected=e, actual=a)
        B.plot()
    return B

if __name__ == '__main__':
    B = test_plotting()

    