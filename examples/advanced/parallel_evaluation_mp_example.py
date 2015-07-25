from random import Random
from time import time
import inspyred
import math

def generate_rastrigin(random, args):
    size = args.get('num_inputs', 10)
    return [random.uniform(-5.12, 5.12) for i in range(size)]

def evaluate_rastrigin(candidates, args):
    fitness = []
    for cs in candidates:
        fit = 10 * len(cs) + sum([((x - 1)**2 - 10 * 
                                   math.cos(2 * math.pi * (x - 1))) 
                                   for x in cs])
        fitness.append(fit)
    return fitness
    
def main(prng=None, display=False):    
    if prng is None:
        prng = Random()
        prng.seed(time()) 

    ea = inspyred.ec.DEA(prng)
    if display:
        ea.observer = inspyred.ec.observers.stats_observer 
    ea.terminator = inspyred.ec.terminators.evaluation_termination
    final_pop = ea.evolve(generator=generate_rastrigin, 
                          evaluator=inspyred.ec.evaluators.parallel_evaluation_mp,
                          mp_evaluator=evaluate_rastrigin, 
                          mp_nprocs=8,
                          pop_size=8, 
                          bounder=inspyred.ec.Bounder(-5.12, 5.12),
                          maximize=False,
                          max_evaluations=256,
                          num_inputs=3)
                          
    if display:
        best = max(final_pop) 
        print('Best Solution: \n{0}'.format(str(best)))
    return ea
            
if __name__ == '__main__':
    main(display=True)
