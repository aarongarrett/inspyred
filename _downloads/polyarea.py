#start_imports
from random import Random
from time import time
from time import sleep
import inspyred
from Tkinter import *
import itertools
#end_imports


def area(p):
    return 0.5 * abs(sum([x0*y1 - x1*y0 for ((x0, y0), (x1, y1)) in segments(p)]))

def segments(p):
    return zip(p, p[1:] + [p[0]])

def generate_polygon(random, args):
    size = args.get('num_vertices', 6)
    return [(random.uniform(-1, 1), random.uniform(-1, 1)) for i in range(size)]

def evaluate_polygon(candidates, args):
    fitness = []
    for cs in candidates:
        fit = area(cs)
        fitness.append(fit)
    return fitness

#start_bounder    
def bound_polygon(candidate, args):
    for i, c in enumerate(candidate):
        x = max(min(c[0], 1), -1)
        y = max(min(c[1], 1), -1)
        candidate[i] = (x, y)
    return candidate
bound_polygon.lower_bound = itertools.repeat(-1)
bound_polygon.upper_bound = itertools.repeat(1)
#end_bounder
    
def mutate_polygon(random, candidates, args):
    mut_rate = args.setdefault('mutation_rate', 0.1)
    bounder = args['_ec'].bounder
    for i, cs in enumerate(candidates):
        for j, (c, lo, hi) in enumerate(zip(cs, bounder.lower_bound, bounder.upper_bound)):
            if random.random() < mut_rate:
                x = c[0] + random.gauss(0, 1) * (hi - lo)
                y = c[1] + random.gauss(0, 1) * (hi - lo)
                candidates[i][j] = (x, y)
        candidates[i] = bounder(candidates[i], args)
    return candidates
        
def polygon_observer(population, num_generations, num_evaluations, args):
    try:
        canvas = args['canvas']
    except KeyError:
        canvas = Canvas(Tk(), bg='white', height=400, width=400)
        args['canvas'] = canvas
        
    # Get the best polygon in the population.
    poly = population[0].candidate
    coords = [(100*x + 200, -100*y + 200) for (x, y) in poly]
    old_polys = canvas.find_withtag('poly')
    for p in old_polys:
        canvas.delete(p)
    old_rects = canvas.find_withtag('rect')
    for r in old_rects:
        canvas.delete(r)
    old_verts = canvas.find_withtag('vert')
    for v in old_verts:
        canvas.delete(v)
        
    canvas.create_rectangle(100, 100, 300, 300, fill='', outline='yellow', width=6, tags='rect')
    canvas.create_polygon(coords, fill='', outline='black', width=2, tags='poly')
    vert_radius = 3
    for (x, y) in coords:
        canvas.create_oval(x-vert_radius, y-vert_radius, x+vert_radius, y+vert_radius, fill='blue', tags='vert')
    canvas.pack()
    canvas.update()
    print('{0} evaluations'.format(num_evaluations))
    sleep(0.05)

#start_main
rand = Random()
rand.seed(int(time()))
my_ec = inspyred.ec.EvolutionaryComputation(rand)
my_ec.selector = inspyred.ec.selectors.tournament_selection
my_ec.variator = [inspyred.ec.variators.uniform_crossover, mutate_polygon]
my_ec.replacer = inspyred.ec.replacers.steady_state_replacement
my_ec.observer = polygon_observer
my_ec.terminator = [inspyred.ec.terminators.evaluation_termination, inspyred.ec.terminators.average_fitness_termination]
window = Tk()
window.title('Evolving Polygons')
can = Canvas(window, bg='white', height=400, width=400)
can.pack()

final_pop = my_ec.evolve(generator=generate_polygon,
                         evaluator=evaluate_polygon,
                         pop_size=100,
                         bounder=bound_polygon,
                         max_evaluations=5000,
                         num_selected=2,
                         mutation_rate=0.25,
                         num_vertices=3,
                         canvas=can)
# Sort and print the best individual, who will be at index 0.
final_pop.sort(reverse=True)
print('Terminated due to {0}.'.format(my_ec.termination_cause))
print(final_pop[0])
sleep(5)
#end_main
