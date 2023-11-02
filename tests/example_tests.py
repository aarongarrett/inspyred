import unittest
import random
import sys, os
pth = os.path.split( os.path.split( os.path.abspath(__file__) )[0] )[0] 
sys.path.append( pth )

import examples

prng = random.Random()
prng.seed(12345) 

class ACS_Test(unittest.TestCase):
    def test(self):
        ac = examples.standard.acs_example.main(prng=prng)
        best = max(ac.archive)
        assert 1550 < (1/best.fitness) < 1553

class Custom_EC_Test(unittest.TestCase):
    def test(self):
        ea = examples.custom.custom_ec_example.main(prng=prng)
        best = max(ea.population)
        assert best.fitness < 0.34

class DEA_Test(unittest.TestCase):
    def test(self):
        dea = examples.standard.dea_example.main(prng=prng)
        best = max(dea.population)
        assert best.fitness < 0.3

class EDA_Test(unittest.TestCase):
    def test(self):
        eda = examples.standard.eda_example.main(prng=prng)
        best = max(eda.population)
        assert best.fitness < 2.5

class ES_Test(unittest.TestCase):
    def test(self):
        es = examples.standard.es_example.main(prng=prng)
        best = max(es.population)
        assert best.fitness < 0.044

class GA_Test(unittest.TestCase):
    def test(self):
        ga = examples.standard.ga_example.main(prng=prng)
        best = max(ga.population)
        assert best.fitness < 0.005

class Knapsack_ACS_Test(unittest.TestCase):
    def test(self):
        ac = examples.advanced.knapsack_acs_example.main(prng=prng)
        best = max(ac.archive)
        assert best.fitness > 1130

class Knapsack_EC_Test(unittest.TestCase):
    def test(self):
        ea = examples.advanced.knapsack_ec_example.main(prng=prng)
        best = max(ea.population)
        assert best.fitness > 1130

class Niche_Test(unittest.TestCase):
    def test(self):
        ea = examples.advanced.niche_example.main(prng=prng)
        candidates = [p.candidate[0] for p in ea.population]
        self.assertTrue(any([1 < x < 2 for x in candidates]), 'expected a solution in [1, 2]')
        self.assertTrue(any([7 < x < 8 for x in candidates]), 'expected a solution in [7, 8]')
        self.assertTrue(any([14 < x < 15 for x in candidates]), 'expected a solution in [14, 15]')
        self.assertTrue(any([20 < x < 21 for x in candidates]), 'expected a solution in [20, 21]')

class NSGA_Test(unittest.TestCase):
    def test(self):
        nsga = examples.standard.nsga_example.main(prng=prng)
        fitnesses = [a.fitness for a in nsga.archive]
        assert all([(-21 < f[0] < -12) and (-12 < f[1] < 1) for f in fitnesses])

class PAES_Test(unittest.TestCase):
    def test(self):
        paes = examples.standard.paes_example.main(prng=prng)
        fitnesses = [a.fitness for a in paes.archive]
        assert all([(-21 < f[0] < -11) and (-12 < f[1] < 1) for f in fitnesses])

class PSO_Test(unittest.TestCase):
    def test(self):
        pso = examples.standard.pso_example.main(prng=prng)
        best = max(pso.population)
        assert best.fitness < 2

class TSP_EC_Test(unittest.TestCase):
    def test(self):
        ea = examples.advanced.tsp_ec_example.main(prng=prng)
        best = max(ea.population)
        assert 1550 < (1/best.fitness) < 1553
        
if __name__ == '__main__':
    unittest.main()
