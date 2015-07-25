from random import Random
from time import time
import inspyred

def main(prng=None, display=False):    
    if prng is None:
        prng = Random()
        prng.seed(time()) 
        
    problem = inspyred.benchmarks.Sphere(2)
    ea = inspyred.ec.SA(prng)
    ea.terminator = inspyred.ec.terminators.evaluation_termination
    final_pop = ea.evolve(evaluator=problem.evaluator, 
                          generator=problem.generator, 
                          maximize=problem.maximize,
                          bounder=problem.bounder,
                          max_evaluations=30000)
                          
    if display:
        best = max(final_pop)
        print('Best Solution: \n{0}'.format(str(best)))
    return ea
            
if __name__ == '__main__':
    main(display=True)
