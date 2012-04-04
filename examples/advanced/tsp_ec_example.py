from random import Random
from time import time
import math
import inspyred


def main(prng=None, display=False):    
    if prng is None:
        prng = Random()
        prng.seed(time()) 
        
    points = [(110.0, 225.0), (161.0, 280.0), (325.0, 554.0), (490.0, 285.0), 
              (157.0, 443.0), (283.0, 379.0), (397.0, 566.0), (306.0, 360.0), 
              (343.0, 110.0), (552.0, 199.0)]
    weights = [[0 for _ in range(len(points))] for _ in range(len(points))]
    for i, p in enumerate(points):
        for j, q in enumerate(points):
            weights[i][j] = math.sqrt((p[0] - q[0])**2 + (p[1] - q[1])**2)
              
    problem = inspyred.benchmarks.TSP(weights)
    ea = inspyred.ec.EvolutionaryComputation(prng)
    ea.selector = inspyred.ec.selectors.tournament_selection
    ea.variator = [inspyred.ec.variators.partially_matched_crossover, 
                   inspyred.ec.variators.inversion_mutation]
    ea.replacer = inspyred.ec.replacers.generational_replacement
    ea.terminator = inspyred.ec.terminators.generation_termination
    final_pop = ea.evolve(generator=problem.generator, 
                          evaluator=problem.evaluator, 
                          bounder=problem.bounder,
                          maximize=problem.maximize, 
                          pop_size=100, 
                          max_generations=50,
                          tournament_size=5,
                          num_selected=100,
                          num_elites=1)
    
    if display:
        best = max(ea.population)
        print('Best Solution: {0}: {1}'.format(str(best.candidate), 1/best.fitness))
    return ea
            
if __name__ == '__main__':
    main(display=True)
