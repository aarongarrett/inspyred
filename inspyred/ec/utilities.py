"""
    ==================================================
    :mod:`utilities` -- Optimization utility functions
    ==================================================

    This module provides utility classes and decorators for evolutionary computations.

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

    .. module:: utilities
    .. moduleauthor:: Aaron Garrett <garrett@inspiredintelligence.io>
"""
import functools
import multiprocessing
from collections import OrderedDict
import pickle


class BoundedOrderedDict(OrderedDict):
    def __init__(self, *args, **kwds):
        self._lock = multiprocessing.Lock()
        self.maxlen = kwds.pop("maxlen", None)
        OrderedDict.__init__(self, *args, **kwds)
        self._checklen()

    def __setitem__(self, key, value):
        with self._lock:
            OrderedDict.__setitem__(self, key, value)
            self._checklen()

    def _checklen(self):
        if self.maxlen is not None:
            while len(self) > self.maxlen:
                self.popitem(last=False)


def memoize(func=None, maxlen=None):
    """Cache a function's return value each time it is called.

    This function serves as a function decorator to provide a caching of
    evaluated fitness values. If called later with the same arguments,
    the cached value is returned instead of being re-evaluated.

    This decorator assumes that candidates are individually pickleable,
    and their pickled values are used for hashing into a dictionary. It
    should be used when evaluating an *expensive* fitness
    function to avoid costly re-evaluation of those fitnesses. The
    typical usage is as follows::

        @memoize
        def expensive_fitness_function(candidates, args):
            # Implementation of expensive fitness calculation
            pass

    It is also possible to provide the named argument *maxlen*, which
    specifies the size of the memoization cache to use. (If *maxlen* is
    ``None``, then an unbounded cache is used.) Once the size of the cache
    has reached *maxlen*, the oldest element is replaced by the newest
    element in order to keep the size constant. This usage is as follows::

        @memoize(maxlen=100)
        def expensive_fitness_function(candidates, args):
            # Implementation of expensive fitness calculation
            pass

    .. warning:: The ``maxlen`` parameter must be passed as a named keyword
       argument, or an ``AttributeError`` will be raised (e.g., saying
       ``@memoize(100)`` will cause an error).

    """
    if func is not None:
        cache = BoundedOrderedDict(maxlen=maxlen)
        @functools.wraps(func)
        def memo_target(candidates, args):
            fitness = []
            for candidate in candidates:
                lookup_value = pickle.dumps(candidate, 1)
                if lookup_value not in cache:
                    cache[lookup_value] = func([candidate], args)[0]
                fitness.append(cache[lookup_value])
            return fitness
        return memo_target
    else:
        def memoize_factory(func):
            return memoize(func, maxlen=maxlen)
        return memoize_factory


class Objectify(object):
    """Create an "objectified" version of a function.

    This function allows an ordinary function passed to it to
    become essentially a callable instance of a class. For inspyred,
    this means that evolutionary operators (selectors, variators,
    replacers, etc.) can be created as normal functions and then
    be given the ability to have attributes *that are specific to
    the object*. Python functions can always have attributes without
    employing any special mechanism, but those attributes exist for the
    function, and there is no way to create a new "object" except
    by implementing a new function with the same functionality.
    This class provides a way to "objectify" the same function
    multiple times in order to provide each "object" with its own
    set of independent attributes.

    The attributes that are created on an objectified function are
    passed into that function via the ubiquitous ``args`` variable
    in inspyred. Any user-specified attributes are added to the
    ``args`` dictionary and replace any existing entry if necessary.
    If the function modifies those entries in the dictionary (e.g.,
    when dynamically modifying parameters), the corresponding
    attributes are modified as well.

    Essentially, a local copy of the ``args`` dictionary is created
    into which the attributes are inserted. This modified local copy
    is then passed to the function. After the function returns, the
    values of the attributes from the dictionary are retrieved and
    are used to update the class attributes.

    The typical usage is as follows::

        def typical_function(*args, **kwargs):
            # Implementation of typical function
            pass

        fun_one = Objectify(typical_function)
        fun_two = Objectify(typical_function)
        fun_one.attribute = value_one
        fun_two.attribute = value_two

    """
    def __init__(self, func):
        self.func = func
        try:
            functools.update_wrapper(self, func)
        except:
            pass

    def __call__(self, *args, **kwargs):
        params = vars(self)
        try:
            orig_args = dict(kwargs['args'])
            orig_args.update(params)
            newkwargs = dict(kwargs)
            newkwargs['args'] = orig_args
            newargs = args
        except KeyError:
            orig_args = dict(args[-1])
            orig_args.update(params)
            newargs = list(args[:-1])
            newargs.append(orig_args)
            newargs = tuple(newargs)
            newkwargs = kwargs
        return_value = self.func(*newargs, **newkwargs)
        try:
            for key in newkwargs['args']:
                if key in params:
                    setattr(self, key, newkwargs['args'][key])
        except KeyError:
            for key in newargs[-1]:
                if key in params:
                    setattr(self, key, newargs[-1][key])
        return return_value
