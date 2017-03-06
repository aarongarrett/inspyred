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
import collections
import functools
import multiprocessing
try:
    import cPickle as pickle
except ImportError:
    import pickle


try:
    from collections import OrderedDict as OrderedDict
except ImportError:
    # http://code.activestate.com/recipes/576693/ (r9)
    # Backport of OrderedDict() class that runs on Python 2.4, 2.5, 2.6, 2.7 and pypy.
    # Passes Python2.7's test suite and incorporates all the latest updates.

    try:
        from thread import get_ident as _get_ident
    except ImportError:
        from dummy_thread import get_ident as _get_ident
    try:
        from _abcoll import KeysView, ValuesView, ItemsView
    except ImportError:
        pass

    class OrderedDict(dict):
        def __init__(self, *args, **kwds):
            if len(args) > 1:
                raise TypeError('expected at most 1 arguments, got %d' % len(args))
            try:
                self.__root
            except AttributeError:
                self.__root = root = []                     # sentinel node
                root[:] = [root, root, None]
                self.__map = {}
            self.__update(*args, **kwds)

        def __setitem__(self, key, value, dict_setitem=dict.__setitem__):
            if key not in self:
                root = self.__root
                last = root[0]
                last[1] = root[0] = self.__map[key] = [last, root, key]
            dict_setitem(self, key, value)

        def __delitem__(self, key, dict_delitem=dict.__delitem__):
            dict_delitem(self, key)
            link_prev, link_next, key = self.__map.pop(key)
            link_prev[1] = link_next
            link_next[0] = link_prev

        def __iter__(self):
            root = self.__root
            curr = root[1]
            while curr is not root:
                yield curr[2]
                curr = curr[1]

        def __reversed__(self):
            root = self.__root
            curr = root[0]
            while curr is not root:
                yield curr[2]
                curr = curr[0]

        def clear(self):
            try:
                for node in self.__map.itervalues():
                    del node[:]
                root = self.__root
                root[:] = [root, root, None]
                self.__map.clear()
            except AttributeError:
                pass
            dict.clear(self)

        def popitem(self, last=True):
            if not self:
                raise KeyError('dictionary is empty')
            root = self.__root
            if last:
                link = root[0]
                link_prev = link[0]
                link_prev[1] = root
                root[0] = link_prev
            else:
                link = root[1]
                link_next = link[1]
                root[1] = link_next
                link_next[0] = root
            key = link[2]
            del self.__map[key]
            value = dict.pop(self, key)
            return key, value

        def keys(self):
            return list(self)

        def values(self):
            return [self[key] for key in self]

        def items(self):
            return [(key, self[key]) for key in self]

        def iterkeys(self):
            return iter(self)

        def itervalues(self):
            for k in self:
                yield self[k]

        def iteritems(self):
            for k in self:
                yield (k, self[k])

        def update(*args, **kwds):
            if len(args) > 2:
                raise TypeError('update() takes at most 2 positional '
                                'arguments (%d given)' % (len(args),))
            elif not args:
                raise TypeError('update() takes at least 1 argument (0 given)')
            self = args[0]
            other = ()
            if len(args) == 2:
                other = args[1]
            if isinstance(other, dict):
                for key in other:
                    self[key] = other[key]
            elif hasattr(other, 'keys'):
                for key in other.keys():
                    self[key] = other[key]
            else:
                for key, value in other:
                    self[key] = value
            for key, value in kwds.items():
                self[key] = value

        __update = update
        __marker = object()

        def pop(self, key, default=__marker):
            if key in self:
                result = self[key]
                del self[key]
                return result
            if default is self.__marker:
                raise KeyError(key)
            return default

        def setdefault(self, key, default=None):
            if key in self:
                return self[key]
            self[key] = default
            return default

        def __repr__(self, _repr_running={}):
            call_key = id(self), _get_ident()
            if call_key in _repr_running:
                return '...'
            _repr_running[call_key] = 1
            try:
                if not self:
                    return '%s()' % (self.__class__.__name__,)
                return '%s(%r)' % (self.__class__.__name__, self.items())
            finally:
                del _repr_running[call_key]

        def __reduce__(self):
            items = [[k, self[k]] for k in self]
            inst_dict = vars(self).copy()
            for k in vars(OrderedDict()):
                inst_dict.pop(k, None)
            if inst_dict:
                return (self.__class__, (items,), inst_dict)
            return self.__class__, (items,)

        def copy(self):
            return self.__class__(self)

        @classmethod
        def fromkeys(cls, iterable, value=None):
            d = cls()
            for key in iterable:
                d[key] = value
            return d

        def __eq__(self, other):
            if isinstance(other, OrderedDict):
                return len(self)==len(other) and self.items() == other.items()
            return dict.__eq__(self, other)

        def __ne__(self, other):
            return not self == other

        def viewkeys(self):
            return KeysView(self)

        def viewvalues(self):
            return ValuesView(self)

        def viewitems(self):
            return ItemsView(self)

    
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
