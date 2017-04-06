"""
    ===============
    :mod:`mutators`
    ===============
    
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
        
    .. module:: mutators
    .. moduleauthor:: Aaron Garrett <garrett@inspiredintelligence.io>
"""
import copy
import functools
    
    
def mutator(mutate):
    """Return an inspyred mutator function based on the given function.
    
    This function generator takes a function that operates on only
    one candidate to produce a single mutated candidate. The generator 
    handles the iteration over each candidate in the set to be mutated.

    The given function ``mutate`` must have the following signature::
    
        mutant = mutate(random, candidate, args)
        
    This function is most commonly used as a function decorator with
    the following usage::
    
        @mutator
        def mutate(random, candidate, args):
            # Implementation of mutation
            pass
            
    The generated function also contains an attribute named
    ``single_mutation`` which holds the original mutation function.
    In this way, the original single-candidate function can be
    retrieved if necessary.
    
    """
    @functools.wraps(mutate)
    def inspyred_mutator(random, candidates, args):
        mutants = []
        for i, cs in enumerate(candidates):
            mutants.append(mutate(random, cs, args))
        return mutants
    inspyred_mutator.single_mutation = mutate
    return inspyred_mutator
    

@mutator
def bit_flip_mutation(random, candidate, args):
    """Return the mutants produced by bit-flip mutation on the candidates.

    This function performs bit-flip mutation. If a candidate solution contains
    non-binary values, this function leaves it unchanged.

    .. Arguments:
       random -- the random number generator object
       candidate -- the candidate solution
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
    
    The mutation rate is applied on a bit by bit basis.
    
    """
    rate = args.setdefault('mutation_rate', 0.1)
    mutant = copy.copy(candidate)
    if len(mutant) == len([x for x in mutant if x in [0, 1]]):
        for i, m in enumerate(mutant):
            if random.random() < rate:
                mutant[i] = (m + 1) % 2
    return mutant


@mutator
def random_reset_mutation(random, candidate, args):
    """Return the mutants produced by randomly choosing new values.

    This function performs random-reset mutation. It assumes that 
    candidate solutions are composed of discrete values. This function
    makes use of the bounder function as specified in the EC's 
    ``evolve`` method, and it assumes that the bounder contains
    an attribute called *values* (which is true for instances of
    ``DiscreteBounder``).
    
    The mutation moves through a candidate solution and, with rate
    equal to the *mutation_rate*, randomly chooses a value from the 
    set of allowed values to be used in that location. Note that this
    value may be the same as the original value.

    .. Arguments:
       random -- the random number generator object
       candidate -- the candidate solution
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
    
    The mutation rate is applied on an element by element basis.
    
    """
    bounder = args['_ec'].bounder
    try:
        values = bounder.values
    except AttributeError:
        values = None
    if values is not None:
        rate = args.setdefault('mutation_rate', 0.1)
        mutant = copy.copy(candidate)
        for i, m in enumerate(mutant):
            if random.random() < rate:
                mutant[i] = random.choice(values)
        return mutant
    else:
        return candidate


@mutator
def scramble_mutation(random, candidate, args):
    """Return the mutants created by scramble mutation on the candidates.

    This function performs scramble mutation. It randomly chooses two
    locations along the candidate and scrambles the values within that
    slice. 

    .. Arguments:
       random -- the random number generator object
       candidate -- the candidate solution
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
      
    The mutation rate is applied to the candidate as a whole (i.e., it
    either mutates or it does not, based on the rate).
    
    """
    rate = args.setdefault('mutation_rate', 0.1)
    if random.random() < rate:
        size = len(candidate)
        p = random.randint(0, size-1)
        q = random.randint(0, size-1)
        p, q = min(p, q), max(p, q)
        s = candidate[p:q+1]
        random.shuffle(s)
        return candidate[:p] + s[::-1] + candidate[q+1:]
    else:
        return candidate
    

@mutator
def inversion_mutation(random, candidate, args):
    """Return the mutants created by inversion mutation on the candidates.

    This function performs inversion mutation. It randomly chooses two
    locations along the candidate and reverses the values within that
    slice. 

    .. Arguments:
       random -- the random number generator object
       candidate -- the candidate solution
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
      
    The mutation rate is applied to the candidate as a whole (i.e., it
    either mutates or it does not, based on the rate).
    
    """
    rate = args.setdefault('mutation_rate', 0.1)
    if random.random() < rate:
        size = len(candidate)
        p = random.randint(0, size-1)
        q = random.randint(0, size-1)
        p, q = min(p, q), max(p, q)
        s = candidate[p:q+1]
        return candidate[:p] + s[::-1] + candidate[q+1:]
    else:
        return candidate


@mutator    
def gaussian_mutation(random, candidate, args):
    """Return the mutants created by Gaussian mutation on the candidates.

    This function performs Gaussian mutation. This function  
    makes use of the bounder function as specified in the EC's 
    ``evolve`` method.

    .. Arguments:
       random -- the random number generator object
       candidate -- the candidate solution
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
    - *gaussian_mean* -- the mean used in the Gaussian function (default 0)
    - *gaussian_stdev* -- the standard deviation used in the Gaussian function
      (default 1)
      
    The mutation rate is applied on an element by element basis.
    
    """
    mut_rate = args.setdefault('mutation_rate', 0.1)
    mean = args.setdefault('gaussian_mean', 0.0)
    stdev = args.setdefault('gaussian_stdev', 1.0)
    bounder = args['_ec'].bounder
    mutant = copy.copy(candidate)
    for i, m in enumerate(mutant):
        if random.random() < mut_rate:
            mutant[i] += random.gauss(mean, stdev)
    mutant = bounder(mutant, args)
    return mutant


@mutator
def nonuniform_mutation(random, candidate, args):
    """Return the mutants produced by nonuniform mutation on the candidates.

    The function performs nonuniform mutation as specified in
    (Michalewicz, "Genetic Algorithms + Data Structures = Evolution
    Programs," Springer, 1996). This function also makes use of the 
    bounder function as specified in the EC's ``evolve`` method.
    
    .. note::
    
       This function **requires** that *max_generations* be specified in 
       the *args* dictionary. Therefore, it is best to use this operator 
       in conjunction with the ``generation_termination`` terminator. 

    .. Arguments:
       random -- the random number generator object
       candidate -- the candidate solution
       args -- a dictionary of keyword arguments

    Required keyword arguments in args:
    
    - *max_generations* -- the maximum number of generations for which
      evolution should take place
    
    Optional keyword arguments in args:
    
    - *mutation_strength* -- the strength of the mutation, where higher
      values correspond to greater variation (default 1)
    
    """
    bounder = args['_ec'].bounder
    num_gens = args['_ec'].num_generations
    max_gens = args['max_generations']
    strength = args.setdefault('mutation_strength', 1)
    exponent = (1.0 - num_gens / float(max_gens)) ** strength
    mutant = copy.copy(candidate)
    for i, (c, lo, hi) in enumerate(zip(candidate, bounder.lower_bound, bounder.upper_bound)):
        if random.random() <= 0.5:
            new_value = c + (hi - c) * (1.0 - random.random() ** exponent)
        else:
            new_value = c - (c - lo) * (1.0 - random.random() ** exponent)
        mutant[i] = new_value
    return mutant
