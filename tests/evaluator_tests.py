import unittest
import random
import logging
import multiprocessing
import inspyred

class DummyEC(object):
    pass

def test_generator(random, args):
    return [random.random() for _ in range(6)]
    
def test_evaluator(candidates, args):
    fitness = []
    for c in candidates:
        fitness.append(sum(c))
    return fitness

def test_evaluator_mo(candidates, args):
    fitness = []
    for c in candidates:
        fitness.append(inspyred.ec.emo.Pareto([sum(c), sum(c)]))
    return fitness
    
def test_set_up(generator, evaluator):
    pop_size = 12
    prng = random.Random()
    prng.seed(111111)
    candidates = [generator(prng, {}) for _ in range(pop_size)]
    fitnesses = evaluator(candidates, {})
    population = [inspyred.ec.Individual(candidate=c) for c in candidates]
    for i, f in zip(population, fitnesses):
        i.fitness = f
    parents = population[:pop_size//2]
    offspring = population[pop_size//2:]
    return (prng, candidates, fitnesses, population, parents, offspring)


class EvaluatorTests(unittest.TestCase):
    def setUp(self):
        self.prng, self.candidates, self.fitnesses, self.population, self.parents, self.offspring = test_set_up(test_generator, test_evaluator)
        self.evaluator = test_evaluator
        self.ec = inspyred.ec.EvolutionaryComputation(None)
    
    def test_parallel_evaluation_pp(self):
        fitnesses = inspyred.ec.evaluators.parallel_evaluation_pp(self.candidates, {'_ec':self.ec, 'pp_evaluator':self.evaluator})
        assert fitnesses == self.fitnesses
        
    def test_parallel_evaluation_mp(self):
        fitnesses = inspyred.ec.evaluators.parallel_evaluation_mp(self.candidates, {'_ec':self.ec, 'mp_evaluator':self.evaluator})
        assert fitnesses == self.fitnesses
        
if __name__ == '__main__':
    unittest.main()
