"""
    ==============================================
    :mod:`migrators` -- Solution migration methods
    ==============================================
    
    This module provides pre-defined migrators for evolutionary computations.

    All migrator functions have the following arguments:
    
    - *random* -- the random number generator object
    - *population* -- the population of Individuals
    - *args* -- a dictionary of keyword arguments
    
    Each migrator function returns the updated population.
    
    Migrator functions would typically be used for multi-population approaches,
    such as island-model evolutionary computations. They provide a means for
    individuals to be transferred from one population to another during the
    evolutionary process.
    
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
       
    .. module:: migrators
    .. moduleauthor:: Aaron Garrett <aaron.lee.garrett@gmail.com>
"""
import multiprocessing
try:
    import Queue
except ImportError:
    import queue as Queue


def default_migration(random, population, args):
    """Do nothing.
    
    This function just returns the existing population with no changes.
    
    """
    return population


class MultiprocessingMigrator(object):
    """Migrate among processes on the same machine.
    
    This callable class allows individuals to migrate from one process 
    to another on the same machine. It maintains a queue of migrants
    whose maximum length can be fixed via the ``max_migrants``
    parameter in the constructor. If the number of migrants in the queue
    reaches this value, new migrants are not added until earlier ones
    are consumed. The unreliability of a multiprocessing environment
    makes it difficult to provide guarantees. However, migrants are 
    theoretically added and consumed at the same rate, so this value
    should determine the "freshness" of individuals, where smaller
    queue sizes provide more recency.
    
    An optional keyword argument in ``args`` requires the migrant to be
    evaluated by the current evolutionary computation before being inserted 
    into the population. This can be important when different populations 
    use different evaluation functions and you need to be able to compare 
    "apples with apples," so to speak.
    
    Optional keyword arguments in args:
    
    - *evaluate_migrant* -- should new migrants be evaluated before 
      adding them to the population (default False)
    
    """
    def __init__(self, max_migrants=1):
        self.max_migrants = max_migrants
        self.migrants = multiprocessing.Queue(self.max_migrants)
        self._lock = multiprocessing.Lock()
        self.__name__ = self.__class__.__name__

    def __call__(self, random, population, args):
        with self._lock:
            evaluate_migrant = args.setdefault('evaluate_migrant', False)
            migrant_index = random.randint(0, len(population) - 1)
            old_migrant = population[migrant_index]
            try:
                migrant = self.migrants.get(block=False)
                if evaluate_migrant:
                    fit = args["_ec"].evaluator([migrant.candidate], args)
                    migrant.fitness = fit[0]
                    args["_ec"].num_evaluations += 1                    
                population[migrant_index] = migrant
            except Queue.Empty:
                pass
            try:
                self.migrants.put(old_migrant, block=False)
            except Queue.Full:
                pass
            return population




