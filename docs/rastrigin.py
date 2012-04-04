#start_imports
from random import Random
from time import time
from math import cos
from math import pi
from inspyred import ec
from inspyred.ec import terminators
#end_imports


def generate_rastrigin(random, args):
    size = args.get('num_inputs', 10)
    return [random.uniform(-5.12, 5.12) for i in range(size)]

def evaluate_rastrigin(candidates, args):
    fitness = []
    for cs in candidates:
        fit = 10 * len(cs) + sum([((x - 1)**2 - 10 * cos(2 * pi * (x - 1))) for x in cs])
        fitness.append(fit)
    return fitness

#start_main
rand = Random()
rand.seed(int(time()))
es = ec.ES(rand)
es.terminator = terminators.evaluation_termination
final_pop = es.evolve(generator=generate_rastrigin,
                      evaluator=evaluate_rastrigin,
                      pop_size=100,
                      maximize=False,
                      bounder=ec.Bounder(-5.12, 5.12),
                      max_evaluations=20000,
                      mutation_rate=0.25,
                      num_inputs=3)
# Sort and print the best individual, who will be at index 0.
final_pop.sort(reverse=True)
print(final_pop[0])
#end_main
