from random import Random
from time import time
import itertools
import inspyred

def my_terminator(population, num_generations, num_evaluations, args):
    min_ham_dist = args.get('minimum_hamming_distance', 30)
    ham_dist = []
    for x, y in itertools.combinations(population, 2):
        ham_dist.append(sum(a != b for a, b in zip(x.candidate, y.candidate)))
    avg_ham_dist = sum(ham_dist) / float(len(ham_dist))
    return avg_ham_dist <= min_ham_dist
        

if __name__ == '__main__':
    prng = Random()
    prng.seed(time()) 
    
    problem = inspyred.benchmarks.Binary(inspyred.benchmarks.Schwefel(2), 
                                         dimension_bits=30)
    ea = inspyred.ec.GA(prng)
    ea.terminator = my_terminator
    final_pop = ea.evolve(generator=problem.generator,
                          evaluator=problem.evaluator,
                          pop_size=10,
                          maximize=problem.maximize,
                          bounder=problem.bounder,
                          num_elites=1,
                          minimum_hamming_distance=12)
                          
    best = max(final_pop)
    print('Best Solution: \n{0}'.format(str(best)))
