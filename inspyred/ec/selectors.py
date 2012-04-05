"""
    ============================================
    :mod:`selectors` -- Parent selection methods
    ============================================
    
    This module provides pre-defined selectors for evolutionary computations.

    All selector functions have the following arguments:
    
    - *random* -- the random number generator object
    - *population* -- the population of individuals
    - *args* -- a dictionary of keyword arguments
    
    Each selector function returns the list of selected individuals.

    .. note::
    
       The *population* is really a shallow copy of the actual population of
       the evolutionary computation. This means that any activities like
       sorting will not affect the actual population.
    
    .. Copyright 2012 Inspired Intelligence Initiative

    .. This program is free software: you can redistribute it and/or modify
       it under the terms of the GNU General Public License as published by
       the Free Software Foundation, either version 3 of the License, or
       (at your option) any later version.

    .. This program is distributed in the hope that it will be useful,
       but WITHOUT ANY WARRANTY; without even the implied warranty of
       MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
       GNU General Public License for more details.

    .. You should have received a copy of the GNU General Public License
       along with this program.  If not, see <http://www.gnu.org/licenses/>.
       
    .. module:: selectors
    .. moduleauthor:: Aaron Garrett <aaron.lee.garrett@gmail.com>
"""


def default_selection(random, population, args):
    """Return the population.
    
    This function acts as a default selection scheme for an evolutionary
    computation. It simply returns the entire population as having been 
    selected.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       args -- a dictionary of keyword arguments
    
    """
    return population


def truncation_selection(random, population, args):
    """Selects the best individuals from the population.
    
    This function performs truncation selection, which means that only
    the best individuals from the current population are selected. This
    is a completely deterministic selection mechanism.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *num_selected* -- the number of individuals to be selected 
      (default len(population))
    
    """
    num_selected = args.setdefault('num_selected', len(population))
    population.sort(reverse=True)
    return population[:num_selected]

    
def uniform_selection(random, population, args):
    """Return a uniform sampling of individuals from the population.
    
    This function performs uniform selection by randomly choosing
    members of the population with replacement.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *num_selected* -- the number of individuals to be selected 
      (default 1)
    
    """
    num_selected = args.setdefault('num_selected', 1)
    selected = []
    for _ in range(num_selected):
        selected.append(population[random.randint(0, len(population)-1)])
    return selected


def fitness_proportionate_selection(random, population, args):
    """Return fitness proportionate sampling of individuals from the population.
    
    This function stochastically chooses individuals from the population
    with probability proportional to their fitness. This is often 
    referred to as "roulette wheel" selection. Note that this selection
    is not valid for minimization problems.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *num_selected* -- the number of individuals to be selected (default 1)
    
    """
    num_selected = args.setdefault('num_selected', 1)
    len_pop = len(population)
    psum = [i for i in range(len_pop)]
    pop_max_fit = (max(population)).fitness
    pop_min_fit = (min(population)).fitness
    
    # If we're actually doing minimimization,
    # fitness proportionate selection is not defined.
    if pop_max_fit < pop_min_fit:
        raise ValueError('Fitness proportionate selection is not valid for minimization.')
    
    # Set up the roulette wheel
    if pop_max_fit == pop_min_fit:
        psum = [(index + 1) / float(len_pop) for index in range(len_pop)]
    elif (pop_max_fit > 0 and pop_min_fit >= 0) or (pop_max_fit <= 0 and pop_min_fit < 0):
        population.sort(reverse=True)
        psum[0] = population[0].fitness
        for i in range(1, len_pop):
            psum[i] = population[i].fitness + psum[i-1]
        for i in range(len_pop):
            psum[i] /= float(psum[len_pop-1])
            
    # Select the individuals
    selected = []
    for _ in range(num_selected):
        cutoff = random.random()
        lower = 0
        upper = len_pop - 1
        while(upper >= lower):
            mid = (lower + upper) // 2
            if psum[mid] > cutoff: 
                upper = mid - 1
            else: 
                lower = mid + 1
        lower = max(0, min(len_pop-1, lower))
        selected.append(population[lower])
    return selected


def rank_selection(random, population, args):
    """Return a rank-based sampling of individuals from the population.
    
    This function behaves similarly to fitness proportionate selection,
    except that it uses the individual's rank in the population, rather
    than its raw fitness value, to determine its probability. This
    means that it can be used for both maximization and minimization 
    problems, since higher rank can be defined correctly for both.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *num_selected* -- the number of individuals to be selected (default 1)
    
    """
    num_selected = args.setdefault('num_selected', 1)

    # Set up the roulette wheel
    len_pop = len(population)
    population.sort()
    psum = list(range(len_pop))
    den = (len_pop * (len_pop + 1)) / 2.0
    for i in range(len_pop):
        psum[i] = (i + 1) / den
    for i in range(1, len_pop):
        psum[i] += psum[i-1]
        
    # Select the individuals
    selected = []
    for _ in range(num_selected):
        cutoff = random.random()
        lower = 0
        upper = len_pop - 1
        while(upper >= lower):
            mid = (lower + upper) // 2
            if psum[mid] > cutoff: 
                upper = mid - 1
            else: 
                lower = mid + 1
        lower = max(0, min(len_pop-1, lower))
        selected.append(population[lower])
    return selected


def tournament_selection(random, population, args):
    """Return a tournament sampling of individuals from the population.
    
    This function selects ``num_selected`` individuals from the population. 
    It selects each one by using random sampling without replacement
    to pull ``tournament_size`` individuals and adds the best of the
    tournament as its selection. If ``tournament_size`` is greater than
    the population size, the population size is used instead as the size
    of the tournament.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of individuals
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *num_selected* -- the number of individuals to be selected (default 1)
    - *tournament_size* -- the tournament size (default 2)
    
    """
    num_selected = args.setdefault('num_selected', 1)
    tournament_size = args.setdefault('tournament_size', 2)
    if tournament_size > len(population):
        tournament_size = len(population)
    selected = []
    for _ in range(num_selected):
        tourn = random.sample(population, tournament_size)
        selected.append(max(tourn))
    return selected


