from random import Random
from time import time
import inspyred

def my_archiver(random, population, archive, args):
    worst_in_pop = min(population)
    if len(archive) > 0:
        worst_in_arc = min(archive)
        if worst_in_pop < worst_in_arc:
            return [worst_in_pop]
        else:
            return archive
    else:
        return [worst_in_pop]

if __name__ == '__main__':
    prng = Random()
    prng.seed(time()) 
    
    problem = inspyred.benchmarks.Rosenbrock(2)
    ea = inspyred.ec.ES(prng)
    ea.observer = [inspyred.ec.observers.stats_observer, 
                   inspyred.ec.observers.archive_observer]
    ea.archiver = my_archiver
    ea.terminator = inspyred.ec.terminators.evaluation_termination
    final_pop = ea.evolve(generator=problem.generator, 
                          evaluator=problem.evaluator, 
                          pop_size=100, 
                          bounder=problem.bounder,
                          maximize=problem.maximize,
                          max_evaluations=30000)
    best = max(final_pop)
    print('Best Solution: \n{0}'.format(str(best)))
    print(ea.archive)
