"""
    ==============================================
    :mod:`variators` -- Solution variation methods
    ==============================================
    
    This module provides pre-defined variators for evolutionary computations.
    
    All variator functions have the following arguments:
    
    - *random* -- the random number generator object
    - *candidates* -- the candidate solutions
    - *args* -- a dictionary of keyword arguments
    
    Each variator function returns the list of modified individuals. In 
    the case of crossover variators, each pair of parents produces a pair
    of offspring. In the case of mutation variators, each candidate
    produces a single mutant.
    
    These variators may make some limited assumptions about the type of
    candidate solutions on which they operate. These assumptions are noted
    in the table below. First, all variators except for ``default_variation`` 
    assume that the candidate solutions are ``Sequence`` types. Those marked
    under "Real" assume that candidates are composed of real numbers. Those
    marked "Binary" assume that candidates are composed entirely of 0's and 1's.
    Those marked "Discrete" assume that candidates are composed of elements
    from a discrete set where the ``DiscreteBounder`` has been used. And 
    those marked "Pickle" assume that candidates can be pickled.
    
    .. tabularcolumns:: |l|c|c|c|c|c|c|c|c|
    
    +------------------------------+----------+------+--------+----------+--------+
    | Variator                     | Sequence | Real | Binary | Discrete | Pickle |
    +==============================+==========+======+========+==========+========+
    | default_variation            |          |      |        |          |        |
    +------------------------------+----------+------+--------+----------+--------+ 
    | arithmetic_crossover         |    X     |   X  |        |          |        |
    +------------------------------+----------+------+--------+----------+--------+    
    | blend_crossover              |    X     |   X  |        |          |        |
    +------------------------------+----------+------+--------+----------+--------+
    | heuristic_crossover          |    X     |   X  |        |          |   X    |
    +------------------------------+----------+------+--------+----------+--------+
    | laplace_crossover            |    X     |   X  |        |          |        |
    +------------------------------+----------+------+--------+----------+--------+
    | n_point_crossover            |    X     |      |        |          |        |
    +------------------------------+----------+------+--------+----------+--------+
    | partially_matched_crossover  |    X     |      |        |    X     |        |
    +------------------------------+----------+------+--------+----------+--------+
    | simulated_binary_crossover   |    X     |   X  |        |          |        |
    +------------------------------+----------+------+--------+----------+--------+
    | uniform_crossover            |    X     |      |        |          |        |
    +------------------------------+----------+------+--------+----------+--------+
    | bit_flip_mutation            |    X     |      |    X   |          |        |
    +------------------------------+----------+------+--------+----------+--------+
    | gaussian_mutation            |    X     |   X  |        |          |        |
    +------------------------------+----------+------+--------+----------+--------+
    | inversion_mutation           |    X     |      |        |          |        |
    +------------------------------+----------+------+--------+----------+--------+
    | nonuniform_mutation          |    X     |   X  |        |          |        |
    +------------------------------+----------+------+--------+----------+--------+
    | random_reset_mutation        |    X     |      |        |    X     |        |
    +------------------------------+----------+------+--------+----------+--------+
    | scramble_mutation            |    X     |      |        |          |        |
    +------------------------------+----------+------+--------+----------+--------+
        
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
        
    .. moduleauthor:: Aaron Garrett <garrett@inspiredintelligence.io>
"""
from inspyred.ec.variators.variators import default_variation
from inspyred.ec.variators.crossovers import crossover
from inspyred.ec.variators.crossovers import arithmetic_crossover
from inspyred.ec.variators.crossovers import blend_crossover
from inspyred.ec.variators.crossovers import heuristic_crossover
from inspyred.ec.variators.crossovers import laplace_crossover
from inspyred.ec.variators.crossovers import n_point_crossover
from inspyred.ec.variators.crossovers import partially_matched_crossover
from inspyred.ec.variators.crossovers import simulated_binary_crossover
from inspyred.ec.variators.crossovers import uniform_crossover
from inspyred.ec.variators.mutators import mutator
from inspyred.ec.variators.mutators import bit_flip_mutation
from inspyred.ec.variators.mutators import gaussian_mutation
from inspyred.ec.variators.mutators import inversion_mutation
from inspyred.ec.variators.mutators import nonuniform_mutation
from inspyred.ec.variators.mutators import random_reset_mutation
from inspyred.ec.variators.mutators import scramble_mutation

__all__ = ['default_variation',
           'crossover', 'arithmetic_crossover', 'blend_crossover', 'heuristic_crossover', 
           'laplace_crossover', 'n_point_crossover', 'partially_matched_crossover', 
           'simulated_binary_crossover', 'uniform_crossover', 
           'mutator', 'bit_flip_mutation', 'gaussian_mutation', 'inversion_mutation',
           'nonuniform_mutation', 'random_reset_mutation', 'scramble_mutation']
