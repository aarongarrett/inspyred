from random import Random
from time import time
import inspyred

def main(prng=None, display=False):
    if prng is None:
        prng = Random()
        prng.seed(time()) 
    
    problem = inspyred.benchmarks.Rastrigin(2)
    ea = inspyred.ec.EDA(prng)
    ea.terminator = inspyred.ec.terminators.evaluation_termination
    final_pop = ea.evolve(evaluator=problem.evaluator, 
                          generator=problem.generator, 
                          pop_size=1000, 
                          bounder=problem.bounder,
                          maximize=problem.maximize,
                          max_evaluations=30000,
                          num_selected=500,
                          num_offspring=1000,
                          num_elites=1)
    
    if display:
        best = max(final_pop) 
        print('Best Solution: \n{0}'.format(str(best)))
    return ea
            
if __name__ == '__main__':
    main(display=True)
