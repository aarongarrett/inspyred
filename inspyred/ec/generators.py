"""
    ================================================
    :mod:`generators` -- Solution generation methods
    ================================================
    
    Generator functions are problem-specific. They are used to create the 
    initial set of candidate solutions needed by the evolutionary computation. 

    All generator functions have the following arguments:
    
    - *random* -- the random number generator object
    - *args* -- a dictionary of keyword arguments
    
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
       
    .. module:: generators
    .. moduleauthor:: Aaron Garrett <aaron.lee.garrett@gmail.com>
"""
import functools


def strategize(generator):
    """Add strategy parameters to candidates created by a generator.
    
    This function decorator is used to provide a means of adding strategy 
    parameters to candidates created by a generator. The generator function 
    is modifed to extend the candidate with ``len(candidate)`` strategy 
    parameters (one per candidate element). Each strategy parameter is 
    initialized to a random value in the range [0, 1]. The typical usage is 
    as follows::
    
        @strategize
        def generator_function(random, args):
            # Normal generator function
            pass
            
    """
    @functools.wraps(generator)
    def strategy_generator(random, args):
        candidate = generator(random, args)
        n = len(candidate)
        candidate.extend([random.random() for _ in range(n)])
        return candidate
    return strategy_generator


class diversify(object):
    """Ensure uniqueness of candidates created by a generator.
    
    This function decorator is used to enforce uniqueness of candidates 
    created by a generator. The decorator maintains a list of previously
    created candidates, and it ensures that new candidates are unique by
    checking a generated candidate against that list, regenerating if a
    duplicate is found. The typical usage is as follows::
    
        @diversify
        def generator_function(random, args):
            # Normal generator function
            pass
            
    If a list of seeds is used, then these can be specified prior to the
    generator's use by saying the following::
    
        @diversify
        def generator_function(random, args):
            # Normal generator function
            pass
        generator_function.candidates = seeds
            
    """
    def __init__ (self, generator):
        self.candidates = []
        self.generator = generator
        try:
            functools.update_wrapper(self, generator)
        except:
            pass

    def __call__ (self, random, args):
        c = self.generator(random, args)
        while c in self.candidates:
            c = self.generator(random, args)
        self.candidates.append(c)
        return c
