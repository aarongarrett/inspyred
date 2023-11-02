import unittest
import random
import logging
import itertools
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

def test_process(random, population, migrator, output_queue):
    for i in range(9999):
        population = migrator(random, population, {})
    output_queue.put(population)


class ArchiverTests(unittest.TestCase):
    def setUp(self):
        self.prng, self.candidates, self.fitnesses, self.population, self.parents, self.offspring = test_set_up(test_generator, test_evaluator_mo)

    def test_default_archiver(self):
        new_archive = inspyred.ec.archivers.default_archiver(self.prng, list(self.population), [], {})
        assert not new_archive

    def test_best_archiver(self):
        new_archive = inspyred.ec.archivers.best_archiver(self.prng, list(self.population), [], {})
        assert new_archive == [max(self.population)]

    def test_adaptive_grid_archiver(self):
        new_archive = inspyred.ec.archivers.adaptive_grid_archiver(self.prng, list(self.population), [], {})
        assert len(new_archive) == 1

class MigratorTests(unittest.TestCase):
    def setUp(self):
        self.prng, self.candidates, self.fitnesses, self.population, self.parents, self.offspring = test_set_up(test_generator, test_evaluator)

    def test_default_migration(self):
        migrants = inspyred.ec.migrators.default_migration(self.prng, list(self.population), {})
        assert migrants == self.population

    # Multiprocessing migration test may fail simply due to randomness of the migration.
    # It is recommended to run the test multiple times to make sure that it consistently
    # fails before spending time looking for errors.
    def test_multiprocessing_migration(self):
        queue = multiprocessing.Queue()
        migrator = inspyred.ec.migrators.MultiprocessingMigrator()
        populations = [["red", "orange", "yellow", "green", "blue", "indigo", "violet"],
                       [1, 2, 3, 4, 5, 6, 7],
                       ["bashful", "doc", "dopey", "grumpy", "happy", "sleepy", "sneezy"]]

        jobs = []
        for pop in populations:
            p = multiprocessing.Process(target=test_process, args=(self.prng, list(pop), migrator, queue))
            p.start()
            jobs.append(p)
        for j in jobs:
            j.join()

        final_pops = []
        while queue.qsize() > 0:
            final_pops.append(set(queue.get()))
        for p in final_pops:
            a = p & set(populations[0])
            b = p & set(populations[1])
            c = p & set(populations[2])
            assert (len(a) > 0 and len(b) > 0 and len(c) > 0)


class ReplacerTests(unittest.TestCase):
    def setUp(self):
        self.prng, self.candidates, self.fitnesses, self.population, self.parents, self.offspring = test_set_up(test_generator, test_evaluator)
        self.prng_mo, self.candidates_mo, self.fitnesses_mo, self.population_mo, self.parents_mo, self.offspring_mo = test_set_up(test_generator, test_evaluator_mo)
        self.ec = DummyEC()
        self.ec.num_evaluations = 10
        self.ec.archive = []
        self.ec.archiver = inspyred.ec.archivers.adaptive_grid_archiver

    def test_default_replacement(self):
        survivors = inspyred.ec.replacers.default_replacement(self.prng, list(self.population), list(self.parents), list(self.offspring), {})
        assert survivors == self.population

    def test_truncation_replacement(self):
        survivors = inspyred.ec.replacers.truncation_replacement(self.prng, list(self.population), list(self.parents), list(self.offspring), {})
        assert (len(survivors) == len(self.population) and max(max(self.population), max(self.offspring)) == max(survivors))

    def test_steady_state_replacement(self):
        survivors = inspyred.ec.replacers.steady_state_replacement(self.prng, list(self.population), list(self.parents), list(self.offspring), {})
        assert (len(survivors) == len(self.population) and all([o in survivors for o in self.offspring]))

    def test_generational_replacement(self):
        survivors = inspyred.ec.replacers.generational_replacement(self.prng, list(self.population), list(self.parents), list(self.offspring), {})
        assert all([s in self.offspring for s in survivors])

    def test_random_replacement(self):
        survivors = inspyred.ec.replacers.random_replacement(self.prng, list(self.population), list(self.parents), list(self.offspring), {})
        assert (len(survivors) == len(self.population) and all([o in survivors for o in self.offspring]))

    def test_plus_replacement(self):
        survivors = inspyred.ec.replacers.plus_replacement(self.prng, list(self.population), list(self.parents), list(self.offspring), {})
        assert (len(survivors) == len(self.population) and max(max(self.parents), max(self.offspring)) == max(survivors))

    def test_comma_replacement(self):
        survivors = inspyred.ec.replacers.comma_replacement(self.prng, list(self.population), list(self.parents), list(self.offspring), {})
        assert (len(survivors) == min(len(self.population), len(self.offspring)) and all([s in self.offspring for s in survivors]))

    def test_crowding_replacement(self):
        survivors = inspyred.ec.replacers.crowding_replacement(self.prng, list(self.population), list(self.parents), list(self.offspring), {})
        assert (len(survivors) == len(self.population) and max(max(self.population), max(self.offspring)) == max(survivors))

    def test_simulated_annealing_replacement(self):
        survivors = inspyred.ec.replacers.simulated_annealing_replacement(self.prng, list(self.population), list(self.parents), list(self.offspring),
                                                                    {'_ec':self.ec, 'max_evaluations':100})
        assert (len(survivors) == len(self.parents) and max(max(self.parents), max(self.offspring)) == max(survivors))

    def test_nsga_replacement(self):
        survivors = inspyred.ec.replacers.nsga_replacement(self.prng_mo, list(self.population_mo), list(self.parents_mo), list(self.offspring_mo), {})
        assert (len(survivors) == len(self.population_mo) and max(max(self.population_mo), max(self.offspring_mo)) == max(survivors))

    def test_paes_replacement(self):
        survivors = inspyred.ec.replacers.paes_replacement(self.prng_mo, list(self.population_mo), list(self.parents_mo), list(self.offspring_mo), {'_ec':self.ec})
        assert (len(survivors) == min(len(self.parents_mo), len(self.offspring_mo)) and max(survivors) == max(max(self.parents_mo), max(self.offspring_mo)))

class SelectorTests(unittest.TestCase):
    def setUp(self):
        self.prng, self.candidates, self.fitnesses, self.population, self.parents, self.offspring = test_set_up(test_generator, test_evaluator)

    def test_default_selection(self):
        parents = inspyred.ec.selectors.default_selection(self.prng, list(self.population), {})
        assert parents == self.population

    def test_truncation_selection(self):
        parents = inspyred.ec.selectors.truncation_selection(self.prng, list(self.population), {})
        assert all([p in parents for p in self.population])

    def test_uniform_selection(self):
        parents = inspyred.ec.selectors.uniform_selection(self.prng, list(self.population), {})
        assert (len(parents) == 1 and all([p in self.population for p in parents]))

    def test_fitness_proportionate_selection(self):
        parents = inspyred.ec.selectors.fitness_proportionate_selection(self.prng, list(self.population), {})
        assert (len(parents) == 1 and all([p in self.population for p in parents]))

    def test_rank_selection(self):
        parents = inspyred.ec.selectors.rank_selection(self.prng, list(self.population), {})
        assert (len(parents) == 1 and all([p in self.population for p in parents]))

    def test_tournament_selection(self):
        parents = inspyred.ec.selectors.tournament_selection(self.prng, list(self.population), {'tournament_size':len(self.population)})
        assert (len(parents) == 1 and max(parents) == max(self.population))

class TerminatorTests(unittest.TestCase):
    def setUp(self):
        self.prng, self.candidates, self.fitnesses, self.population, self.parents, self.offspring = test_set_up(test_generator, test_evaluator)
        self.ec = DummyEC()
        self.ec.logger = logging.getLogger('inspyred.test')

    def test_default_termination(self):
        t = inspyred.ec.terminators.default_termination(list(self.population), 1, 1, {})
        assert t is True

    def test_diversity_termination(self):
        p = [inspyred.ec.Individual(candidate=[1, 1, 1]) for _ in range(10)]
        t = inspyred.ec.terminators.diversity_termination(list(p), 1, 1, {})
        assert t is True

    def test_average_fitness_termination(self):
        p = [inspyred.ec.Individual(candidate=i.candidate) for i in self.population]
        for x in p:
            x.fitness = 1
        t = inspyred.ec.terminators.average_fitness_termination(list(p), 1, 1, {})
        assert t is True

    def test_evaluation_termination(self):
        t = inspyred.ec.terminators.evaluation_termination(list(self.population), 1, len(self.population), {})
        assert t is True

    def test_generation_termination(self):
        t = inspyred.ec.terminators.generation_termination(list(self.population), 1, 1, {})
        assert t is True

    def test_time_termination(self):
        t = inspyred.ec.terminators.time_termination(list(self.population), 1, 1, {'_ec':self.ec, 'max_time':0})
        assert t is True

class VariatorTests(unittest.TestCase):
    def setUp(self):
        self.prng, self.candidates, self.fitnesses, self.population, self.parents, self.offspring = test_set_up(test_generator, test_evaluator)
        self.ec = DummyEC()
        self.ec.bounder = inspyred.ec.Bounder(0, 1)
        self.ec.population = list(self.population)

    def test_default_variation(self):
        offspring = inspyred.ec.variators.default_variation(self.prng, list(self.candidates), {})
        assert offspring == self.candidates

    def test_n_point_crossover(self):
        offspring = inspyred.ec.variators.n_point_crossover(self.prng, list(self.candidates), {'num_crossover_points':3})
        moms = self.candidates[::2]
        dads = self.candidates[1::2]
        dmoms = itertools.chain.from_iterable([[t, t] for t in moms])
        ddads = itertools.chain.from_iterable([[t, t] for t in dads])
        offs = [(offspring[i], offspring[i+1]) for i in range(0, len(offspring), 2)]
        assert (all([x in m or x in d for m, d, o in zip(dmoms, ddads, offspring) for x in o]) and
                all([(x in o[0] or x in o[1]) and (y in o[0] or y in o[1]) for m, d, o in zip(moms, dads, offs) for x in m for y in m]))

    def test_uniform_crossover(self):
        offspring = inspyred.ec.variators.uniform_crossover(self.prng, list(self.candidates), {})
        moms = self.candidates[::2]
        dads = self.candidates[1::2]
        dmoms = itertools.chain.from_iterable([[t, t] for t in moms])
        ddads = itertools.chain.from_iterable([[t, t] for t in dads])
        offs = [(offspring[i], offspring[i+1]) for i in range(0, len(offspring), 2)]
        assert (all([x in m or x in d for m, d, o in zip(dmoms, ddads, offspring) for x in o]) and
                all([(x in o[0] or x in o[1]) and (y in o[0] or y in o[1]) for m, d, o in zip(moms, dads, offs) for x in m for y in m]))

    def test_blend_crossover(self):
        alpha = 0.1
        offspring = inspyred.ec.variators.blend_crossover(self.prng, list(self.candidates), {'_ec':self.ec, 'blx_alpha':alpha})
        moms = itertools.chain.from_iterable([[t, t] for t in self.candidates[::2]])
        dads = itertools.chain.from_iterable([[t, t] for t in self.candidates[1::2]])
        tests = []
        for mom, dad, off in zip(moms, dads, offspring):
            for m, d, x in zip(mom, dad, off):
                tol = alpha * (max(m, d) - min(m, d))
                tests.append(x >= (min(m, d) - tol) and x <= (max(m, d) + tol))
        assert all(tests)

    def test_arithmetic_crossover(self):
        alpha = 0.5
        cands = [[0, 0, 0], [1, 1, 1]]
        offspring = inspyred.ec.variators.arithmetic_crossover(self.prng, list(cands), {'_ec':self.ec, 'ax_alpha':alpha})
        for off in offspring:
            for o in off:
                assert o == 0.5

    def test_heuristic_crossover(self):
        offspring = inspyred.ec.variators.heuristic_crossover(self.prng, list(self.candidates), {'_ec':self.ec})
        moms = itertools.chain.from_iterable([[t, t] for t in self.candidates[::2]])
        dads = itertools.chain.from_iterable([[t, t] for t in self.candidates[1::2]])
        tests = []
        for mom, dad, off in zip(moms, dads, offspring):
            for m, d, x in zip(mom, dad, off):
                tests.append(x >= min(m, d) and x <= max(m, d))
        assert all(tests)

    def test_simulated_binary_crossover(self):
        alpha = 0.2
        offspring = inspyred.ec.variators.simulated_binary_crossover(self.prng, list(self.candidates), {'_ec':self.ec})
        moms = itertools.chain.from_iterable([[t, t] for t in self.candidates[::2]])
        dads = itertools.chain.from_iterable([[t, t] for t in self.candidates[1::2]])
        tests = []
        for mom, dad, off in zip(moms, dads, offspring):
            for m, d, x in zip(mom, dad, off):
                tol = alpha * (max(m, d) - min(m, d))
                tests.append(x >= (min(m, d) - tol) and x <= (max(m, d) + tol))
        assert all(tests)

    def test_laplace_crossover(self):
        alpha = 0.1
        offspring = inspyred.ec.variators.laplace_crossover(self.prng, list(self.candidates), {'_ec':self.ec, 'lx_scale': 0.01})
        moms = itertools.chain.from_iterable([[t, t] for t in self.candidates[::2]])
        dads = itertools.chain.from_iterable([[t, t] for t in self.candidates[1::2]])
        tests = []
        for mom, dad, off in zip(moms, dads, offspring):
            for m, d, x in zip(mom, dad, off):
                tol = alpha * (max(m, d) - min(m, d))
                tests.append(x >= (min(m, d) - tol) and x <= (max(m, d) + tol))
        assert all(tests)

    def test_gaussian_mutation(self):
        offspring = inspyred.ec.variators.gaussian_mutation(self.prng, list(self.candidates), {'_ec':self.ec})
        assert(all([x >= 0 and x <= 1 for o in offspring for x in o]))

    def test_bit_flip_mutation(self):
        class my_random(object):
            def random(self):
                return 0
        r = my_random()
        my_candidate = [1, 0, 1, 0, 1, 1, 0, 0, 0, 1]
        offspring = inspyred.ec.variators.bit_flip_mutation(r, list([my_candidate]), {})
        assert(all([c != o for c, o in zip(my_candidate, offspring[0])]))

    def test_random_reset_mutation(self):
        class my_random(object):
            def random(self):
                return 0
            def choice(self, v):
                return v[0]
        r = my_random()
        b = inspyred.ec.DiscreteBounder([1, 2, 3])
        self.ec.bounder = b
        offspring = inspyred.ec.variators.random_reset_mutation(r, list([[1, 3, 2, 2, 1]]), {'_ec': self.ec})
        assert all([o == 1 for o in offspring[0]])

    def test_nonuniform_mutation(self):
        self.ec.num_generations = 0
        offspring = inspyred.ec.variators.nonuniform_mutation(self.prng, list(self.candidates), {'_ec':self.ec, 'max_generations': 10})
        assert(all([x >= 0 and x <= 1 for o in offspring for x in o]))

if __name__ == '__main__':
    unittest.main()

