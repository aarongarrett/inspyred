"""
    ================================================
    :mod:`generators` -- Solution generation methods
    ================================================
    
    Generator functions are problem-specific. They are used to create the 
    initial set of candidate solutions needed by the evolutionary computation. 

    All generator functions have the following arguments:
    
    - *random* -- the random number generator object
    - *args* -- a dictionary of keyword arguments
    
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
        
    .. module:: generators
    .. moduleauthor:: Aaron Garrett <garrett@inspiredintelligence.io>
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
