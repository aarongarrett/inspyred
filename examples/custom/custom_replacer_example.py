from random import Random
from time import time
import inspyred

def my_replacer(random, population, parents, offspring, args):
    psize = len(population)
    population.sort(reverse=True)
    survivors = population[:psize // 2]
    num_remaining = psize - len(survivors)
    for i in range(num_remaining):
        survivors.append(random.choice(offspring))
    return survivors

if __name__ == '__main__':
    prng = Random()
    prng.seed(time()) 
    
    problem = inspyred.benchmarks.Ackley(2)
    ea = inspyred.ec.ES(prng)
    ea.replacer = my_replacer
    ea.terminator = inspyred.ec.terminators.evaluation_termination
    final_pop = ea.evolve(generator=problem.generator, 
                          evaluator=problem.evaluator, 
                          pop_size=100, 
                          bounder=problem.bounder,
                          maximize=problem.maximize,
                          max_evaluations=30000)
    best = max(final_pop)
    print('Best Solution: \n{0}'.format(str(best)))
