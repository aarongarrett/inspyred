import inspyred
import multiprocessing
import random
import unittest


class AnalysisTests(unittest.TestCase):
    def test_hypervolume(self):
        assert True
        

class BounderTests(unittest.TestCase):
    def test_bounder(self):
        a = inspyred.ec.Bounder(0, 1)
        b = inspyred.ec.Bounder(0, [3, 5])
        c = inspyred.ec.Bounder([1, 2], 3)
        d = inspyred.ec.Bounder([1, 2], [3, 5])
        u = a([-1, 2], {})
        v = b([4, 6], {})
        w = b([-1, 2], {})
        x = c([0, 1], {})
        y = c([4, 4], {})
        z = d([0, 6], {})
        assert u == [0, 1]
        assert v == [3, 5]
        assert w == [0, 2]
        assert x == [1, 2]
        assert y == [3, 3]
        assert z == [1, 5]
        
    def test_discrete_bounder(self):
        a = inspyred.ec.DiscreteBounder([1, 3, 7, 15])
        b = inspyred.ec.DiscreteBounder([0, 1])
        w = a([7, 3, 1, 1, 15], {})
        x = a([2, 5, 9, 11, 13], {})
        y = a([-2, 16, 10, 1.5], {})
        z = b([-1, 0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1, 2], {})
        assert w == [7, 3, 1, 1, 15]
        assert x == [1, 3, 7, 7, 15]
        assert y == [1, 15, 7, 1]
        assert z == [0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1]


@inspyred.ec.generators.strategize
def strategize_generator(random, args):
    return [random.uniform(-5, 5) for _ in range(3)]
    
@inspyred.ec.generators.diversify
def diversify_generator(random, args):
    return [random.randint(1, 9) for _ in range(2)]
    
class GeneratorTests(unittest.TestCase):
    def setUp(self):
        self.prng = random.Random()
        self.prng.seed(11111)
        
    def test_strategize(self):
        cand = strategize_generator(self.prng, {})
        n = len(cand) // 2
        tests = [-5 <= c <= 5 for c in cand[:n]]
        tests.extend([0 <= c <= 1 for c in cand[n:]])
        assert all(tests)
        
    def test_diversify(self):
        c = []
        for i in range(10):
            c.append(diversify_generator(self.prng, {}))
        assert c == diversify_generator.candidates
        

@inspyred.ec.utilities.memoize
def f(n, a):
    if n[0] <= 1: return [1]
    return [f([n[0]-1], a)[0] + f([n[0]-2], a)[0]]

@inspyred.ec.utilities.memoize(maxlen=2)
def g(c, a):
    if c[0] <= 1: return [1]
    return [g([c[0]-1], a)[0] + g([c[0]-2], a)[0]]

class UtilityTests(unittest.TestCase):
    def test_memoize(self):        
        elements = [60] * 4
        pool = multiprocessing.Pool(processes=4)
        results = [pool.apply_async(f, ([e], 0)) for e in elements]
        pool.close()
        pool.join()
        tests_f = [r.get()[0] == 2504730781961 for r in results]
        elements = [35] * 4
        pool = multiprocessing.Pool(processes=4)
        results = [pool.apply_async(g, ([e], 0)) for e in elements]
        pool.close()
        pool.join()
        tests_g = [r.get()[0] == 14930352 for r in results]
        assert all(tests_f)
        assert all(tests_g)

    def test_objectify(self):
        def my_fun(x, y, args):
            z = x + y + args['key']
            args['key'] = args['key'] * 2
            return z
        d = {'key': 1}
        f = inspyred.ec.utilities.Objectify(my_fun)
        f.key = 7
        g = inspyred.ec.utilities.Objectify(my_fun)
        g.key = 3
        a = f(9, 2, d)
        b = g(2, 5, d)
        c = my_fun(3, 4, d)
        assert a == 18
        assert b == 10
        assert f.key == 14
        assert g.key == 6
        assert c == 8
        assert d['key'] == 2


if __name__ == '__main__':
    unittest.main()
