"""
    ================================================
    :mod:`replacers` -- Survivor replacement methods
    ================================================
    
    This module provides pre-defined replacers for evolutionary computations.
    
    All replacer functions have the following arguments:
    
    - *random* -- the random number generator object
    - *population* -- the population of individuals
    - *parents* -- the list of parent individuals
    - *offspring* -- the list of offspring individuals
    - *args* -- a dictionary of keyword arguments
    
    Each replacer function returns the list of surviving individuals.

    .. Copyright 2012 Aaron Garrett

    .. Permission is hereby granted, free of charge, to any person obtaining a copy
       of this software and associated documentation files (the "Software"), to deal
       in the Software without restriction, including without limitation the rights
       to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
       copies of the Software, and to permit persons to whom the Software is
       furnished to do so, subject to the following conditions:

    .. The above copyright notice and this permission notice shall be included in
       all copies or substantial portions of the Software.

    .. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
       IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
       FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
       AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
       LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
       OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
       THE SOFTWARE.       
        
    .. module:: replacers
    .. moduleauthor:: Aaron Garrett <garrett@inspiredintelligence.io>
"""
import math


def default_replacement(random, population, parents, offspring, args):
    """Performs no replacement, returning the original population.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       parents -- the list of parent individuals
       offspring -- the list of offspring individuals
       args -- a dictionary of keyword arguments
    
    """
    return population

    
def truncation_replacement(random, population, parents, offspring, args):
    """Replaces population with the best of the population and offspring.
    
    This function performs truncation replacement, which means that
    the entire existing population is replaced by the best from among
    the current population and offspring, keeping the existing population
    size fixed. This is similar to so-called "plus" replacement in the 
    evolution strategies literature, except that "plus" replacement 
    considers only parents and offspring for survival. However, if the
    entire population are parents (which is often the case in evolution 
    strategies), then truncation replacement and plus-replacement are 
    equivalent approaches.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       parents -- the list of parent individuals
       offspring -- the list of offspring individuals
       args -- a dictionary of keyword arguments
    
    """
    psize = len(population)
    population.extend(list(offspring))
    population.sort(reverse=True)
    return population[:psize]

    
def steady_state_replacement(random, population, parents, offspring, args):
    """Performs steady-state replacement for the offspring.
    
    This function performs steady-state replacement, which means that
    the offspring replace the least fit individuals in the existing
    population, even if those offspring are less fit than the individuals
    that they replace.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       parents -- the list of parent individuals
       offspring -- the list of offspring individuals
       args -- a dictionary of keyword arguments
    
    """
    population.sort()
    num_to_replace = min(len(offspring), len(population))
    population[:num_to_replace] = offspring[:num_to_replace]
    return population


def generational_replacement(random, population, parents, offspring, args):
    """Performs generational replacement with optional weak elitism.
    
    This function performs generational replacement, which means that
    the entire existing population is replaced by the offspring,
    truncating to the population size if the number of offspring is 
    larger. Weak elitism may also be specified through the `num_elites`
    keyword argument in args. If this is used, the best `num_elites`
    individuals in the current population are allowed to survive if
    they are better than the worst `num_elites` offspring.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       parents -- the list of parent individuals
       offspring -- the list of offspring individuals
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *num_elites* -- number of elites to consider (default 0)
    
    """
    num_elites = args.setdefault('num_elites', 0)
    population.sort(reverse=True)
    offspring.extend(population[:num_elites])
    offspring.sort(reverse=True)
    survivors = offspring[:len(population)]
    return survivors


def random_replacement(random, population, parents, offspring, args):
    """Performs random replacement with optional weak elitism.
    
    This function performs random replacement, which means that
    the offspring replace random members of the population, keeping
    the population size constant. Weak elitism may also be specified 
    through the `num_elites` keyword argument in args. If this is used, 
    the best `num_elites` individuals in the current population are 
    allowed to survive if they are better than the worst `num_elites`
    offspring.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       parents -- the list of parent individuals
       offspring -- the list of offspring individuals
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *num_elites* -- number of elites to consider (default 0)
    
    """
    num_elites = args.setdefault('num_elites', 0)
    population.sort(reverse=True)
    num_to_replace = min(len(offspring), len(population) - num_elites) 
    valid_indices = list(range(num_elites, len(population)))
    rep_index = random.sample(valid_indices, num_to_replace)
    for i, repind in enumerate(rep_index):
        population[repind] = offspring[i]
    return population


def plus_replacement(random, population, parents, offspring, args):
    """Performs "plus" replacement.
    
    This function performs "plus" replacement, which means that
    the entire existing population is replaced by the best
    population-many elements from the combined set of parents and 
    offspring. 
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       parents -- the list of parent individuals
       offspring -- the list of offspring individuals
       args -- a dictionary of keyword arguments

    """
    pool = list(offspring)
    pool.extend(population)
    pool.sort(reverse=True)
    survivors = pool[:len(population)]
    return survivors


def comma_replacement(random, population, parents, offspring, args):
    """Performs "comma" replacement.
    
    This function performs "comma" replacement, which means that
    the entire existing population is replaced by the best
    population-many elements from the offspring. This function
    makes the assumption that the size of the offspring is at 
    least as large as the original population. Otherwise, the
    population size will not be constant.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       parents -- the list of parent individuals
       offspring -- the list of offspring individuals
       args -- a dictionary of keyword arguments
       
    """
    offspring.sort(reverse=True)
    survivors = offspring[:len(population)]
    return survivors


def crowding_replacement(random, population, parents, offspring, args):
    """Performs crowding replacement as a form of niching.
    
    This function performs crowding replacement, which means that
    the members of the population are replaced one-at-a-time with
    each of the offspring. A random sample of `crowding_distance`
    individuals is pulled from the current population, and the
    closest individual to the current offspring (where "closest"
    is determined by the `distance_function`) is replaced by that
    offspring, if the offspring is better. It is possible for one 
    offspring to replace an earlier offspring in the same generation, 
    given the random sample that is taken of the current survivors 
    for each offspring.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       parents -- the list of parent individuals
       offspring -- the list of offspring individuals
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:    
    
    - *distance_function* -- a function that accepts two candidate 
      solutions and returns the distance between them (default 
      Euclidean L2 distance)
    - *crowding_distance* -- a positive integer representing the 
      number of closest solutions to consider as a "crowd" (default 2)
       
    """
    def distance(x, y):
        return math.sqrt(sum([(a - b)**2 for a, b in zip(x, y)]))
    try:
        distance_function = args['distance_function']
    except KeyError:
        distance_function = distance
        args['distance_function'] = distance_function
    crowding_distance = args.setdefault('crowding_distance', 2)
    survivors = population
    for o in offspring:
        pool = random.sample(survivors, crowding_distance)
        closest = min(pool, key=lambda x: distance_function(o.candidate, x.candidate))
        if o > closest:
            survivors.remove(closest)
            survivors.append(o)
    return survivors



    
#-------------------------------------------
# Algorithm-specific Replacement Strategies
#-------------------------------------------
    
def simulated_annealing_replacement(random, population, parents, offspring, args):
    """Replaces population using the simulated annealing schedule.
    
    This function performs simulated annealing replacement based
    on a temperature and a cooling rate. These can be specified
    by the keyword arguments `temperature`, which should be the
    initial temperature, and `cooling_rate`, which should be the
    coefficient by which the temperature is reduced. If these
    keyword arguments are not present, then the function will
    attempt to base the cooling schedule either on the ratio of 
    evaluations to the maximum allowed evaluations or on the 
    ratio of generations to the maximum allowed generations. 
    Each of these ratios is of the form ``(max - current)/max``
    so that the cooling schedule moves smoothly from 1 to 0.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       parents -- the list of parent individuals
       offspring -- the list of offspring individuals
       args -- a dictionary of keyword arguments
    
    Optional keyword arguments in args:    
    
    - *temperature* -- the initial temperature
    - *cooling_rate* -- a real-valued coefficient in the range (0, 1) 
      by which the temperature should be reduced 
    
    """
    try:
        temp = args['temperature']
        cooling_rate = args['cooling_rate']
        temp = temp * cooling_rate
        args['temperature'] = temp
    except KeyError:
        try:
            num_evals = args['_ec'].num_evaluations
            max_evals = args['max_evaluations']
            temp = float(max_evals - num_evals) / float(max_evals)
        except KeyError:
            num_gens = args['_ec'].num_generations
            max_gens = args['max_generations']
            temp = 1 - float(max_gens - num_gens) / float(max_gens)
        
    new_pop = []
    for p, o in zip(parents, offspring):
        if o >= p:
            new_pop.append(o)
        elif temp > 0 and random.random() < math.exp(-abs(p.fitness - o.fitness) / float(temp)):
            new_pop.append(o)
        else:
            new_pop.append(p)
            
    return new_pop

    
def nsga_replacement(random, population, parents, offspring, args):
    """Replaces population using the non-dominated sorting technique from NSGA-II.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       parents -- the list of parent individuals
       offspring -- the list of offspring individuals
       args -- a dictionary of keyword arguments
    
    """
    survivors = []
    combined = list(population)
    combined.extend(offspring)
    
    # Perform the non-dominated sorting to determine the fronts.
    fronts = []
    pop = set(range(len(combined)))
    while len(pop) > 0:
        front = []
        for p in pop:
            dominated = False
            for q in pop:
                if combined[p] < combined[q]:
                    dominated = True
                    break
            if not dominated:
                front.append(p)
        fronts.append([dict(individual=combined[f], index=f) for f in front])
        pop = pop - set(front)
    
    # Go through each front and add all the elements until doing so
    # would put you above the population limit. At that point, fall
    # back to the crowding distance to determine who to put into the
    # next population. Individuals with higher crowding distances
    # (i.e., more distance between neighbors) are preferred.
    for i, front in enumerate(fronts):
        if len(survivors) + len(front) > len(population):
            # Determine the crowding distance.
            distance = [0 for _ in range(len(combined))]
            individuals = list(front)
            num_individuals = len(individuals)
            num_objectives = len(individuals[0]['individual'].fitness)
            for obj in range(num_objectives):
                individuals.sort(key=lambda x: x['individual'].fitness[obj])
                distance[individuals[0]['index']] = float('inf')
                distance[individuals[-1]['index']] = float('inf')
                for i in range(1, num_individuals-1):
                    distance[individuals[i]['index']] = (distance[individuals[i]['index']] + 
                                                         (individuals[i+1]['individual'].fitness[obj] - 
                                                          individuals[i-1]['individual'].fitness[obj]))
                
            crowd = [dict(dist=distance[f['index']], index=f['index']) for f in front]
            crowd.sort(key=lambda x: x['dist'], reverse=True)
            last_rank = [combined[c['index']] for c in crowd]
            r = 0
            num_added = 0
            num_left_to_add = len(population) - len(survivors)
            while r < len(last_rank) and num_added < num_left_to_add:
                if last_rank[r] not in survivors:
                    survivors.append(last_rank[r])
                    num_added += 1
                r += 1
            # If we've filled out our survivor list, then stop.
            # Otherwise, process the next front in the list.
            if len(survivors) == len(population):
                break
        else:
            for f in front:
                if f['individual'] not in survivors:
                    survivors.append(f['individual'])
    return survivors

    
def paes_replacement(random, population, parents, offspring, args):
    """Replaces population using the Pareto Archived Evolution Strategy method.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       parents -- the list of parent individuals
       offspring -- the list of offspring individuals
       args -- a dictionary of keyword arguments
    
    """
    archive = args['_ec'].archive
    archiver = args['_ec'].archiver
        
    survivors = []
    for p, o in zip(parents, offspring):
        if o == p:
            survivors.append(p)
        elif o in archive:
            survivors.append(p)
        elif o > p:
            archive = archiver(random, [o], archive, args)
            survivors.append(o)
        elif o >= p:
            for a in archive:
                if o > a or o < a:
                    break
            if o >= a:
                archive = archiver(random, [o], archive, args)
                if o > a or archiver.grid_population[o.grid_location] <= archiver.grid_population[p.grid_location]:
                    survivors.append(o)
                else:
                    survivors.append(p)
            else:
                survivors.append(p)
        else:
            survivors.append(p)
    return survivors
