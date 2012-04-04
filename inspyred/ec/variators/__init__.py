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
       
    .. moduleauthor:: Aaron Garrett <aaron.lee.garrett@gmail.com>
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
