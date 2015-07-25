import random
import time
import math
import itertools
import inspyred

def my_distance(x, y):
    return sum([abs(a - b) for a, b in zip(x, y)])

def generate(random, args):
    return [random.uniform(0, 26)]
    
def evaluate(candidates, args):
    fitness = []
    for cand in candidates:
        fit = sum([math.sin(c) for c in cand])
        fitness.append(fit)
    return fitness

def main(prng=None, display=False):
    if prng is None:
        prng = random.Random()
        prng.seed(time.time()) 
    
    ea = inspyred.ec.EvolutionaryComputation(prng)
    ea.selector = inspyred.ec.selectors.tournament_selection
    ea.replacer = inspyred.ec.replacers.crowding_replacement
    ea.variator = inspyred.ec.variators.gaussian_mutation
    ea.terminator = inspyred.ec.terminators.evaluation_termination

    final_pop = ea.evolve(generate, evaluate, pop_size=30, 
                          bounder=inspyred.ec.Bounder(0, 26),
                          max_evaluations=10000,
                          num_selected=30,
                          mutation_rate=1.0,
                          crowding_distance=10,
                          distance_function=my_distance)
                          
    if display:
        import matplotlib.pyplot as plt
        x = []
        y = []
        for p in final_pop:
            x.append(p.candidate[0])
            y.append(math.sin(p.candidate[0]))
        t = [(i / 1000.0) * 26.0 for i in range(1000)]
        s = [math.sin(a) for a in t]
        plt.plot(t, s, color='b')
        plt.scatter(x, y, color='r')
        plt.axis([0, 26, 0, 1.1])
        plt.savefig('niche_example.pdf', format='pdf')
        plt.show()
    return ea

if __name__ == '__main__':
    main(display=True)
