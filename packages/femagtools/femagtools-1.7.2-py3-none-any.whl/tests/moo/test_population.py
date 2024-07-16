#!/usr/bin/env python
#
import unittest
import os
from femagtools import moo
import math

p=[
[1    , -10.90      ,1.99     ,23.45       ,0.9514    ,0.0051    ,0.0030],
[0    , -11.10      ,1.77     ,21.61       ,0.9369    ,0.0067    ,0.0028],
[0    , -10.90      ,1.66     ,21.00       ,0.8679    ,0.0062    ,0.0029],
[1    , -10.90      ,2.22     ,22.24       ,0.9625    ,0.0052    ,0.0035],
[1    , -10.90      ,2.29     ,21.46       ,0.9666    ,0.0055    ,0.0036],
[0    , -10.60      ,1.64     ,16.14       ,0.8211    ,0.0083    ,0.0040],
[2    , -10.60      ,2.07     ,21.73       ,0.9045    ,0.0046    ,0.0040],
[0    , -10.30      ,1.24     ,16.20       ,0.7529    ,0.0079    ,0.0035],
[0    , -10.70      ,1.50     ,21.48       ,0.8053    ,0.0071    ,0.0021],
[1    , -11.00      ,1.76     ,26.14       ,0.9500    ,0.0053    ,0.0021],
[2    , -10.90      ,2.34     ,21.68       ,0.9668    ,0.0052    ,0.0037],
[1    , -10.70      ,1.75     ,18.21       ,0.8442    ,0.0065    ,0.0039],
[0    , -10.60      ,1.50     ,18.19       ,0.7929    ,0.0082    ,0.0028],
[0    , -10.50      ,1.48     ,19.49       ,0.7809    ,0.0070    ,0.0026],
[1    , -10.20      ,1.54     ,25.97       ,0.7977    ,0.0044    ,0.0022],
[2    , -10.40      ,1.82     ,23.19       ,0.8608    ,0.0044    ,0.0033],
[0    , -10.70      ,1.53     ,19.30       ,0.8178    ,0.0074    ,0.0028],
[0    , -10.80      ,1.60     ,18.14       ,0.8642    ,0.0088    ,0.0030],
[2    , -10.60      ,1.85     ,25.52       ,0.9219    ,0.0043    ,0.0029],
[0    , -11.00      ,1.57     ,21.06       ,0.9113    ,0.0087    ,0.0022],
[2    , -10.40      ,1.87     ,22.97       ,0.8633    ,0.0043    ,0.0035],
[0    , -11.10      ,1.82     ,20.09       ,0.9572    ,0.0084    ,0.0028],
[0    , -11.10      ,1.85     ,20.04       ,0.9570    ,0.0082    ,0.0029],
[3    , -10.60      ,2.22     ,24.30       ,0.9548    ,0.0043    ,0.0034]
]
p2=[
[0    , -10.30      ,1.20     ,16.15       ,0.7503    ,0.0079    ,0.0035],
[0    , -11.00      ,2.01     ,17.63       ,0.9423    ,0.0082    ,0.0040],
[0    , -10.60      ,1.60     ,15.57       ,0.8126    ,0.0089    ,0.0040],
[0    , -10.30      ,1.32     ,15.34       ,0.7638    ,0.0081    ,0.0040],
[0    , -11.20      ,1.73     ,22.51       ,0.9595    ,0.0078    ,0.0022],
[0    , -10.90      ,1.53     ,20.72       ,0.8756    ,0.0090    ,0.0021],
[0    , -11.00      ,1.58     ,20.58       ,0.9090    ,0.0087    ,0.0023],
[0    , -10.50      ,1.43     ,17.14       ,0.7783    ,0.0085    ,0.0030],
[0    , -11.10      ,1.57     ,21.86       ,0.9129    ,0.0082    ,0.0021],
[0    , -10.80      ,1.57     ,18.94       ,0.8336    ,0.0077    ,0.0029],
[0    , -10.70      ,1.51     ,17.72       ,0.8185    ,0.0088    ,0.0029],
[0    , -10.50      ,1.46     ,16.82       ,0.7860    ,0.0090    ,0.0031],
[0    , -10.60      ,1.49     ,17.80       ,0.7929    ,0.0084    ,0.0029],
[0    , -10.80      ,1.74     ,16.41       ,0.8693    ,0.0088    ,0.0040],
[0    , -11.00      ,1.99     ,17.89       ,0.9442    ,0.0082    ,0.0038],
[0    , -10.80      ,1.55     ,19.24       ,0.8319    ,0.0079    ,0.0027],
[0    , -10.90      ,1.54     ,20.53       ,0.8735    ,0.0089    ,0.0022],
[0    , -10.90      ,1.60     ,18.11       ,0.8681    ,0.0087    ,0.0031],
[0    , -10.70      ,1.65     ,16.18       ,0.8251    ,0.0083    ,0.0040],
[0    , -10.40      ,1.36     ,15.68       ,0.7673    ,0.0080    ,0.0039],
[0    , -11.10      ,1.80     ,19.57       ,0.9454    ,0.0083    ,0.0030],
[0    , -11.10      ,1.93     ,18.48       ,0.9457    ,0.0082    ,0.0035],
[0    , -10.70      ,1.50     ,21.48       ,0.8053    ,0.0071    ,0.0021],
[0    , -10.70      ,1.64     ,16.18       ,0.8311    ,0.0085    ,0.0040]
]


class DummyProblem(moo.Problem):
    def __init__(self, x, n, nf):
        super(DummyProblem,self).__init__(n, 0, nf)

        kmax=int(math.sqrt(x))+1
        self.f=[]
        for i in range(kmax):
            for k in range(kmax):
                self.f.append((i*0.8/kmax +0.1, k*0.8/kmax +0.1))
        self.pos = 0
        
    def objfun( self, x ):
        fret = self.f[self.pos]
        self.pos +=1
        return fret

class PropulationTest(unittest.TestCase):
    def test_merge( self ):
        dim = 3
        prob = DummyProblem( 0, dim, dim )

        pop = moo.Population(prob, 0 )
        for ip in p:
            pop.append(ip[4:])
        for i,f in zip(*(pop.individuals, p)):
            i.cur_f = f[1:4]
        pop.update()
        self.assertEqual(pop.pareto_rank, [1, 0, 0, 1, 1, 0, 2, 0, 0, 1, 2, 1,
                                           0, 0, 1, 2, 0, 0, 2, 0, 2, 0, 0, 3])

        pop.individuals=[]
        for ip in p2:
            pop.append(ip[4:])
        for i,f in zip(*(pop.individuals, p2)):
            i.cur_f = f[1:4]
        pop.update()
        self.assertEqual(pop.pareto_rank, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                                           0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0])
        
    def test_eval( self ):
        dim = 8
        prob = DummyProblem( dim, 2, 2 )
        pop = moo.Population(prob,  dim )
        pop.eval()

        self.assertEqual(pop.compute_nadir(), [0.1, 0.1] )
        self.assertEqual(pop.compute_ideal(), [0.1, 0.1] )
        self.assertEqual(pop.dom_count, [0, 1, 2, 1, 3, 5, 2, 5])
        self.assertEqual(pop.pareto_rank, [0, 1, 2, 1, 2, 3, 2, 3])
        self.assertEqual(pop.best_idx(), [0, 1, 3, 4, 2, 6, 5, 7] )

if __name__ == '__main__':
  unittest.main()
