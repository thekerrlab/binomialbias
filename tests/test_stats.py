'''
Simple tests of the app
'''

import sciris as sc
import binomialbias as bb

def test_stats(atol=0.01):
    out = sc.objdict()
    
    # Examples from the paper
    for k,(n,e,a) in dict(
            coin = [10, 5, 2],
            die  = [12, 2, 2],
            vcs  = [40, 20, 13],
            sen  = [38, 0.38, 2],
            ).items():
        B = bb.BinomialBias(n=n, expected=e, actual=a)
        out[k] = B.results
        
    ## Tests from paper
    
    # Fig. 1
    assert sc.approx(out.coin.cumprob, 0.055, atol=atol)
    assert sc.approx(out.coin.p_future, 0.62, atol=atol)
    
    # Fig. 2
    assert sc.approx(out.die.cumprob, 0.68, atol=atol)
    assert sc.approx(out.die.p_future, 0.96, atol=atol)
    
    # Fig. 3
    assert sc.approx(out.vcs.cumprob, 0.019, atol=atol)
    assert sc.approx(out.vcs.p_future, 0.43, atol=atol)
    
    # Fig. 6
    assert sc.approx(out.sen.cumprob, 3.9e-6, atol=1e-6)
    assert sc.approx(out.sen.p_future, 1.3e-4, atol=1e-5)
        
    return out

if __name__ == '__main__':
    out = test_stats()

    