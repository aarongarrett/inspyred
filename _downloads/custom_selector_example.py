from random import Random
from time import time
import inspyred

def my_selector(random, population, args):
    n = args.get('num_selected', 2)
    best = max(population)
    selected = []
    for i in range(n):
        if random.random() <= 0.5:
            selected.append(best)
        else:
            selected.append(random.choice(population))
    return selected

if __name__ == '__main__':
    prng = Random()
    prng.seed(time()) 
    
    problem = inspyred.benchmarks.Griewank(2)
    ea = inspyred.ec.DEA(prng)
    ea.selector = my_selector
    ea.terminator = inspyred.ec.terminators.evaluation_termination
    final_pop = ea.evolve(generator=problem.generator, 
                          evaluator=problem.evaluator, 
                          pop_size=100, 
                          bounder=problem.bounder,
                          maximize=problem.maximize,
                          max_evaluations=30000)
                          
    best = max(final_pop)
    print('Best Solution: \n{0}'.format(str(best)))
