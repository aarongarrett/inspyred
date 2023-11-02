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

    .. module:: migrators
    .. moduleauthor:: Aaron Garrett <garrett@inspiredintelligence.io>
"""
import multiprocessing
import queue


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

    The migration takes the current individual *I* out of the queue, if
    one exists. It then randomly chooses an individual *E* from the population
    to insert into the queue. Finally, if *I* exists, it replaces *E* in the
    population (re-evaluating fitness if necessary). Otherwise, *E* remains in
    the population and also exists in the queue as a migrant.

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
            except queue.Empty:
                pass
            try:
                self.migrants.put(old_migrant, block=False)
            except queue.Full:
                pass
            return population




