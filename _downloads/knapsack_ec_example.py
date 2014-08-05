from random import Random
from time import time
import inspyred


def main(prng=None, display=False):    
    if prng is None:
        prng = Random()
        prng.seed(time()) 
        
    items = [(7,369), (10,346), (11,322), (10,347), (12,348), (13,383), 
             (8,347), (11,364), (8,340), (8,324), (13,365), (12,314), 
             (13,306), (13,394), (7,326), (11,310), (9,400), (13,339), 
             (5,381), (14,353), (6,383), (9,317), (6,349), (11,396), 
             (14,353), (9,322), (5,329), (5,386), (5,382), (4,369), 
             (6,304), (10,392), (8,390), (8,307), (10,318), (13,359), 
             (9,378), (8,376), (11,330), (9,331)]

    problem = inspyred.benchmarks.Knapsack(15, items, duplicates=True)
    ea = inspyred.ec.EvolutionaryComputation(prng)
    ea.selector = inspyred.ec.selectors.tournament_selection
    ea.variator = [inspyred.ec.variators.uniform_crossover, 
                   inspyred.ec.variators.gaussian_mutation]
    ea.replacer = inspyred.ec.replacers.steady_state_replacement
    ea.terminator = inspyred.ec.terminators.evaluation_termination
    final_pop = ea.evolve(generator=problem.generator, 
                          evaluator=problem.evaluator, 
                          bounder=problem.bounder,
                          maximize=problem.maximize, 
                          pop_size=100, 
                          max_evaluations=2500,
                          tournament_size=5,
                          num_selected=2)
    
    if display:
        best = max(ea.population)
        print('Best Solution: {0}: {1}'.format(str(best.candidate), 
                                               best.fitness))
    return ea
            
if __name__ == '__main__':
    main(display=True)
