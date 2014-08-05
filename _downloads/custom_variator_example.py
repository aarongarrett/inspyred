from random import Random
from time import time
import inspyred

# Note that we could have used the @inspyred.ec.variators.mutator
# decorator here and simplified our custom variator to 
#
#     def my_variator(random, candidate, args)
#
# where candidate is a single candidate. Such a function would
# just return the single mutant.
def my_variator(random, candidates, args):
    mutants = []
    for c in candidates:
        points = random.sample(range(len(c)), 2)
        x, y = min(points), max(points)
        if x == 0:
            mutants.append(c[y::-1] + c[y+1:])
        else:
            mutants.append(c[:x] + c[y:x-1:-1] + c[y+1:])
    return mutants

if __name__ == '__main__':
    prng = Random()
    prng.seed(time()) 
    
    problem = inspyred.benchmarks.Binary(inspyred.benchmarks.Schwefel(2), 
                                         dimension_bits=30)
    ea = inspyred.ec.GA(prng)
    ea.variator = my_variator
    ea.terminator = inspyred.ec.terminators.evaluation_termination
    final_pop = ea.evolve(generator=problem.generator,
                          evaluator=problem.evaluator,
                          pop_size=10,
                          maximize=problem.maximize,
                          bounder=problem.bounder,
                          num_elites=1,
                          max_evaluations=20000)
                          
    best = max(final_pop)
    print('Best Solution: \n{0}'.format(str(best)))
