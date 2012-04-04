import random
from inspyred import ec
from inspyred.ec import variators
from inspyred.ec import replacers
from inspyred.ec import terminators
from inspyred.ec import observers

def my_constraint_function(candidate):
    """Return the number of constraints that candidate violates."""
    # In this case, we'll just say that the point has to lie 
    # within a circle centered at (0, 0) of radius 1.
    if candidate[0]**2 + candidate[1]**2 > 1:
        return 1
    else:
        return 0

def my_generator(random, args):
    # Create pairs in the range [-2, 2].
    return [random.uniform(-2.0, 2.0) for i in range(2)]

def my_evaluator(candidates, args):
    # The fitness will be how far the point is from
    # the origin. (We're maximizing, in this case.)
    # Note that the constraint heavily punishes individuals
    # who go beyond the unit circle. Therefore, these
    # two functions combined focus the evolution toward
    # finding individual who lie ON the circle.
    fitness = []
    for c in candidates:
        if my_constraint_function(c) > 0:
            fitness.append(-1)
        else:
            fitness.append(c[0]**2 + c[1]**2)
    return fitness

def constrained_tournament_selection(random, population, args):
    num_selected = args.setdefault('num_selected', 1)
    constraint_func = args.setdefault('constraint_function', None)
    tournament_size = 2
    pop = list(population)
    selected = []
    for _ in range(num_selected):
        tournament = random.sample(pop, tournament_size)
        # If there is not a constraint function,
        # just do regular tournament selection.
        if constraint_func is None:
            selected.append(max(tournament))
        else:
            cons = [constraint_func(t.candidate) for t in tournament]
            # If no constraints are violated, just do 
            # regular tournament selection.
            if max(cons) == 0:
                selected.append(max(tournament))
            # Otherwise, choose the least violator 
            # (which may be a non-violator).
            else:
                selected.append(tournament[cons.index(min(cons))])
    return selected

r = random.Random()
myec = ec.EvolutionaryComputation(r)
myec.selector = constrained_tournament_selection
myec.variator = variators.gaussian_mutation
myec.replacer = replacers.generational_replacement
myec.terminator = terminators.evaluation_termination
myec.observer = observers.stats_observer
pop = myec.evolve(my_generator, my_evaluator, 
                  pop_size=100, 
                  bounder=ec.Bounder(-2, 2),
                  num_selected=100,
                  constraint_func=my_constraint_function, 
                  mutation_rate=0.5,
                  max_evaluations=2000)
                  
import pylab
x = []
y = []
c = []
pop.sort()
num_feasible = len([p for p in pop if p.fitness >= 0])
feasible_count = 0
for i, p in enumerate(pop):
    x.append(p.candidate[0])
    y.append(p.candidate[1])
    if i == len(pop) - 1:
        c.append('r')
    elif p.fitness < 0:
        c.append('0.98')
    else:
        c.append(str(1 - feasible_count / float(num_feasible)))
        feasible_count += 1
angles = pylab.linspace(0, 2*pylab.pi, 100)
pylab.plot(pylab.cos(angles), pylab.sin(angles), color='b')
pylab.scatter(x, y, color=c)
pylab.savefig('constraint_example.pdf', format='pdf')
