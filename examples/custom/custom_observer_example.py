from random import Random
from time import time
import inspyred

def my_observer(population, num_generations, num_evaluations, args):
    best = max(population)
    print('{0:6} -- {1} : {2}'.format(num_generations, 
                                      best.fitness, 
                                      str(best.candidate)))

if __name__ == '__main__':
    prng = Random()
    prng.seed(time()) 
    
    problem = inspyred.benchmarks.Rastrigin(2)
    ea = inspyred.ec.ES(prng)
    ea.observer = my_observer
    ea.terminator = inspyred.ec.terminators.evaluation_termination
    final_pop = ea.evolve(generator=problem.generator, 
                          evaluator=problem.evaluator, 
                          pop_size=100, 
                          bounder=problem.bounder,
                          maximize=problem.maximize,
                          max_evaluations=30000)
    best = max(final_pop)
    print('Best Solution: \n{0}'.format(str(best)))
