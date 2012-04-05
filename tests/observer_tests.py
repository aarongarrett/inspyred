import unittest
import random
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

class ObserverTests(unittest.TestCase):
    def setUp(self):
        self.prng, self.candidates, self.fitnesses, self.population, self.parents, self.offspring = test_set_up(test_generator, test_evaluator)
        self.ec = DummyEC()
        self.ec.bounder = inspyred.ec.Bounder(0, 1)
        self.ec.population = list(self.population)
        self.ec.archive = [["The", "archive", "observer", "works"]]
        
    def test_all_observers(self):
        inspyred.ec.observers.default_observer(self.population, 0, 0, {})
        inspyred.ec.observers.best_observer(self.population, 0, 0, {})
        inspyred.ec.observers.stats_observer(self.population, 0, 0, {})
        inspyred.ec.observers.population_observer(self.population, 0, 0, {})
        inspyred.ec.observers.file_observer(self.population, 0, 0, {})
        inspyred.ec.observers.archive_observer(self.population, 0, 0, {'_ec': self.ec})
        inspyred.ec.observers.plot_observer(self.population, 0, 0, {})
        # Cannot test the email observer without putting in a username and password.
        # We'll leave it out for now.
        assert True
 
if __name__ == '__main__':
    unittest.main()
