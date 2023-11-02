"""
    ===============================================
    :mod:`ec` -- Evolutionary computation framework
    ===============================================

    This module provides the framework for creating evolutionary computations.

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

    .. module:: ec
    .. moduleauthor:: Aaron Garrett <garrett@inspiredintelligence.io>
"""
import collections
import copy
import functools
from inspyred.ec import archivers
from inspyred.ec import generators
from inspyred.ec import migrators
from inspyred.ec import observers
from inspyred.ec import replacers
from inspyred.ec import selectors
from inspyred.ec import terminators
from inspyred.ec import variators
import itertools
import logging
import math
import time


class Error(Exception):
    """An empty base exception."""
    pass


class EvolutionExit(Error):
    """An exception that may be raised and caught to end the evolution.

    This is an empty exception class that can be raised by the user
    at any point in the code and caught outside of the ``evolve``
    method.

    .. note::

       Be aware that ending the evolution in such a way will almost
       certainly produce an erroneous population (e.g., not all
       individuals will have been reevaluated, etc.). However, this
       approach can be viable if solutions have been archived such
       that the current population is not of critical importance.

    """
    pass


class Bounder(object):
    """Defines a basic bounding function for numeric lists.

    This callable class acts as a function that bounds a
    numeric list between the lower and upper bounds specified.
    These bounds can be single values or lists of values. For
    instance, if the candidate is composed of five values, each
    of which should be bounded between 0 and 1, you can say
    ``Bounder([0, 0, 0, 0, 0], [1, 1, 1, 1, 1])`` or just
    ``Bounder(0, 1)``. If either the ``lower_bound`` or
    ``upper_bound`` argument is ``None``, the Bounder leaves
    the candidate unchanged (which is the default behavior).

    As an example, if the bounder above were used on the candidate
    ``[0.2, -0.1, 0.76, 1.3, 0.4]``, the resulting bounded
    candidate would be ``[0.2, 0, 0.76, 1, 0.4]``.

    A bounding function is necessary to ensure that all
    evolutionary operators respect the legal bounds for
    candidates. If the user is using only custom operators
    (which would be aware of the problem constraints), then
    those can obviously be tailored to enforce the bounds
    on the candidates themselves. But the built-in operators
    make only minimal assumptions about the candidate solutions.
    Therefore, they must rely on an external bounding function
    that can be user-specified (so as to contain problem-specific
    information).

    In general, a user-specified bounding function must accept
    two arguments: the candidate to be bounded and the keyword
    argument dictionary. Typically, the signature of such a
    function would be the following::

        bounded_candidate = bounding_function(candidate, args)

    This function should return the resulting candidate after
    bounding has been performed.

    Public Attributes:

    - *lower_bound* -- the lower bound for a candidate
    - *upper_bound* -- the upper bound for a candidate

    """
    def __init__(self, lower_bound=None, upper_bound=None):
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        if self.lower_bound is not None and self.upper_bound is not None:
            if not isinstance(self.lower_bound, collections.abc.Iterable):
                self.lower_bound = itertools.repeat(self.lower_bound)
            if not isinstance(self.upper_bound, collections.abc.Iterable):
                self.upper_bound = itertools.repeat(self.upper_bound)

    def __call__(self, candidate, args):
        # The default would be to leave the candidate alone
        # unless both bounds are specified.
        if self.lower_bound is None or self.upper_bound is None:
            return candidate
        else:
            if not isinstance(self.lower_bound, collections.abc.Iterable):
                self.lower_bound = [self.lower_bound] * len(candidate)
            if not isinstance(self.upper_bound, collections.abc.Iterable):
                self.upper_bound = [self.upper_bound] * len(candidate)
            bounded_candidate = candidate
            for i, (c, lo, hi) in enumerate(zip(candidate, self.lower_bound,
                                                self.upper_bound)):
                bounded_candidate[i] = max(min(c, hi), lo)
            return bounded_candidate


class DiscreteBounder(object):
    """Defines a basic bounding function for numeric lists of discrete values.

    This callable class acts as a function that bounds a
    numeric list to a set of legitimate values. It does this by
    resolving a given candidate value to the nearest legitimate
    value that can be attained. In the event that a candidate value
    is the same distance to multiple legitimate values, the legitimate
    value appearing earliest in the list will be used.

    For instance, if ``[1, 4, 8, 16]`` was used as the *values* parameter,
    then the candidate ``[6, 10, 13, 3, 4, 0, 1, 12, 2]`` would be
    bounded to ``[4, 8, 16, 4, 4, 1, 1, 8, 1]``.

    Public Attributes:

    - *values* -- the set of attainable values
    - *lower_bound* -- the smallest attainable value
    - *upper_bound* -- the largest attainable value

    """
    def __init__(self, values):
        self.values = values
        self.lower_bound = itertools.repeat(min(self.values))
        self.upper_bound = itertools.repeat(max(self.values))

    def __call__(self, candidate, args):
        if not isinstance(self.lower_bound, collections.abc.Iterable):
            self.lower_bound = [min(self.values)] * len(candidate)
        if not isinstance(self.upper_bound, collections.abc.Iterable):
            self.upper_bound = [max(self.values)] * len(candidate)
        closest = lambda target: min(self.values, key=lambda x: abs(x-target))
        bounded_candidate = candidate
        for i, c in enumerate(bounded_candidate):
            bounded_candidate[i] = closest(c)
        return bounded_candidate


class Individual(object):
    """Represents an individual in an evolutionary computation.

    An individual is defined by its candidate solution and the
    fitness (or value) of that candidate solution. Individuals
    can be compared with one another by using <, <=, >, and >=.
    In all cases, such comparisons are made using the individuals'
    fitness values. The ``maximize`` attribute is respected in all
    cases, so it is better to think of, for example, < (less-than)
    to really mean "worse than" and > (greater-than) to mean
    "better than". For instance, if individuals a and b have fitness
    values 2 and 4, respectively, and if ``maximize`` were ``True``,
    then a < b would be true. If ``maximize`` were ``False``, then
    a < b would be false (because a is "better than" b in terms of
    the fitness evaluation, since we're minimizing).

    .. note::

       ``Individual`` objects are almost always created by the EC,
       rather than the user. The ``evolve`` method of the EC also
       has a ``maximize`` argument, whose value is passed directly
       to all created individuals.

    Public Attributes:

    - *candidate* -- the candidate solution
    - *fitness* -- the value of the candidate solution
    - *birthdate* -- the system time at which the individual was created
    - *maximize* -- Boolean value stating use of maximization

    """
    def __init__(self, candidate=None, maximize=True):
        self._candidate = candidate
        self.fitness = None
        self.birthdate = time.time()
        self.maximize = maximize

    @property
    def candidate(self):
        return self._candidate

    @candidate.setter
    def candidate(self, value):
        self._candidate = value
        self.fitness = None

    def __str__(self):
        return '{0} : {1}'.format(str(self.candidate), str(self.fitness))

    def __repr__(self):
        return '<Individual: candidate = {0}, fitness = {1}, birthdate = {2}>'.format(str(self.candidate), str(self.fitness), self.birthdate)

    def __lt__(self, other):
        if self.fitness is not None and other.fitness is not None:
            if self.maximize:
                return self.fitness < other.fitness
            else:
                return self.fitness > other.fitness
        else:
            raise Error('fitness cannot be None when comparing Individuals')

    def __le__(self, other):
        return self < other or not other < self

    def __gt__(self, other):
        if self.fitness is not None and other.fitness is not None:
            return other < self
        else:
            raise Error('fitness cannot be None when comparing Individuals')

    def __ge__(self, other):
        return other < self or not self < other

    def __eq__(self, other):
        return ((self._candidate, self.fitness, self.maximize) ==
                (other._candidate, other.fitness, other.maximize))

    def __ne__(self, other):
        return not (self == other)



class EvolutionaryComputation(object):
    """Represents a basic evolutionary computation.

    This class encapsulates the components of a generic evolutionary
    computation. These components are the selection mechanism, the
    variation operators, the replacement mechanism, the migration
    scheme, the archival mechanism, the terminators, and the observers.

    The ``observer``, ``terminator``, and ``variator`` attributes may be
    specified as lists of such operators. In the case of the ``observer``,
    all elements of the list will be called in sequence during the
    observation phase. In the case of the ``terminator``, all elements of
    the list will be combined via logical ``or`` and, thus, the evolution will
    terminate if any of the terminators return True. Finally, in the case
    of the ``variator``, the elements of the list will be applied one
    after another in pipeline fashion, where the output of one variator
    is used as the input to the next.

    Public Attributes:

    - *selector* -- the selection operator (defaults to ``default_selection``)
    - *variator* -- the (possibly list of) variation operator(s) (defaults to
      ``default_variation``)
    - *replacer* -- the replacement operator (defaults to
      ``default_replacement``)
    - *migrator* -- the migration operator (defaults to ``default_migration``)
    - *archiver* -- the archival operator (defaults to ``default_archiver``)
    - *observer* -- the (possibly list of) observer(s) (defaults to
      ``default_observer``)
    - *terminator* -- the (possibly list of) terminator(s) (defaults to
      ``default_termination``)
    - *logger* -- the logger to use (defaults to the logger 'inspyred.ec')

    The following attributes do not have legitimate values until after
    the ``evolve`` method executes:

    - *termination_cause* -- the name of the function causing
      ``evolve`` to terminate, in the event that multiple terminators are used
    - *generator* -- the generator function passed to ``evolve``
    - *evaluator* -- the evaluator function passed to ``evolve``
    - *bounder* -- the bounding function passed to ``evolve``
    - *maximize* -- Boolean stating use of maximization passed to ``evolve``
    - *archive* -- the archive of individuals
    - *population* -- the population of individuals
    - *num_evaluations* -- the number of fitness evaluations used
    - *num_generations* -- the number of generations processed

    Note that the attributes above are, in general, not intended to
    be modified by the user. (They are intended for the user to query
    during or after the ``evolve`` method's execution.) However,
    there may be instances where it is necessary to modify them
    within other functions. This is possible to do, but it should be the
    exception, rather than the rule.

    If logging is desired, the following basic code segment can be
    used in the ``main`` or calling scope to accomplish that::

        import logging
        logger = logging.getLogger('inspyred.ec')
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler('inspyred.log', mode='w')
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    Protected Attributes:

    - *_random* -- the random number generator object
    - *_kwargs* -- the dictionary of keyword arguments initialized
      from the *args* parameter in the *evolve* method

    """
    def __init__(self, random):
        self.selector = selectors.default_selection
        self.variator = variators.default_variation
        self.replacer = replacers.default_replacement
        self.migrator = migrators.default_migration
        self.observer = observers.default_observer
        self.archiver = archivers.default_archiver
        self.terminator = terminators.default_termination
        self.termination_cause = None
        self.generator = None
        self.evaluator = None
        self.bounder = None
        self.maximize = True
        self.archive = None
        self.population = None
        self.num_evaluations = 0
        self.num_generations = 0
        self.logger = logging.getLogger('inspyred.ec')
        try:
            self.logger.addHandler(logging.NullHandler())
        except AttributeError:
            # If Python < 2.7, then NullHandler doesn't exist.
            pass
        self._random = random
        self._kwargs = dict()

    def _should_terminate(self, pop, ng, ne):
        terminate = False
        fname = ''
        if isinstance(self.terminator, collections.abc.Iterable):
            terminators = self.terminator
        else:
            terminators = [self.terminator]

        for clause in terminators:
            self.logger.debug('termination test using {0} at generation {1} and evaluation {2}'.format(clause.__name__, ng, ne))
            terminate = terminate or clause(population=pop, num_generations=ng, num_evaluations=ne, args=self._kwargs)
            if terminate:
                fname = clause.__name__
                break

        if terminate:
            self.termination_cause = fname
            self.logger.debug('termination from {0} at generation {1} and evaluation {2}'.format(self.termination_cause, ng, ne))
        return terminate

    def evolve(self, generator, evaluator, pop_size=100, seeds=None, maximize=True, bounder=None, **args):
        """Perform the evolution.

        This function creates a population and then runs it through a series
        of evolutionary epochs until the terminator is satisfied. The general
        outline of an epoch is selection, variation, evaluation, replacement,
        migration, archival, and observation. The function returns a list of
        elements of type ``Individual`` representing the individuals contained
        in the final population.

        Arguments:

        - *generator* -- the function to be used to generate candidate solutions
        - *evaluator* -- the function to be used to evaluate candidate solutions
        - *pop_size* -- the number of Individuals in the population (default 100)
        - *seeds* -- an iterable collection of candidate solutions to include
          in the initial population (default None)
        - *maximize* -- Boolean value stating use of maximization (default True)
        - *bounder* -- a function used to bound candidate solutions (default None)
        - *args* -- a dictionary of keyword arguments

        The *bounder* parameter, if left as ``None``, will be initialized to a
        default ``Bounder`` object that performs no bounding on candidates.
        Note that the *_kwargs* class variable will be initialized to the *args*
        parameter here. It will also be modified to include the following 'built-in'
        keyword argument:

        - *_ec* -- the evolutionary computation (this object)

        """
        self._kwargs = args
        self._kwargs['_ec'] = self

        if seeds is None:
            seeds = []
        if bounder is None:
            bounder = Bounder()

        self.termination_cause = None
        self.generator = generator
        self.evaluator = evaluator
        self.bounder = bounder
        self.maximize = maximize
        self.population = []
        self.archive = []

        # Create the initial population.
        if not isinstance(seeds, collections.abc.Sequence):
            seeds = [seeds]
        initial_cs = copy.copy(seeds)
        num_generated = max(pop_size - len(seeds), 0)
        i = 0
        self.logger.debug('generating initial population')
        while i < num_generated:
            cs = generator(random=self._random, args=self._kwargs)
            initial_cs.append(cs)
            i += 1
        self.logger.debug('evaluating initial population')
        initial_fit = evaluator(candidates=initial_cs, args=self._kwargs)

        for cs, fit in zip(initial_cs, initial_fit):
            if fit is not None:
                ind = Individual(cs, maximize=maximize)
                ind.fitness = fit
                self.population.append(ind)
            else:
                self.logger.warning('excluding candidate {0} because fitness received as None'.format(cs))
        self.logger.debug('population size is now {0}'.format(len(self.population)))

        self.num_evaluations = len(initial_fit)
        self.num_generations = 0

        self.logger.debug('archiving initial population')
        self.archive = self.archiver(random=self._random, population=list(self.population), archive=list(self.archive), args=self._kwargs)
        self.logger.debug('archive size is now {0}'.format(len(self.archive)))
        self.logger.debug('population size is now {0}'.format(len(self.population)))

        # Turn observers and variators into lists if not already
        if isinstance(self.observer, collections.abc.Iterable):
            observers = self.observer
        else:
            observers = [self.observer]
        if isinstance(self.variator, collections.abc.Iterable):
            variators = self.variator
        else:
            variators = [self.variator]

        for obs in observers:
            self.logger.debug('observation using {0} at generation {1} and evaluation {2}'.format(obs.__name__, self.num_generations, self.num_evaluations))
            obs(population=list(self.population), num_generations=self.num_generations, num_evaluations=self.num_evaluations, args=self._kwargs)

        while not self._should_terminate(list(self.population), self.num_generations, self.num_evaluations):
            # Select individuals.
            self.logger.debug('selection using {0} at generation {1} and evaluation {2}'.format(self.selector.__name__, self.num_generations, self.num_evaluations))
            parents = self.selector(random=self._random, population=list(self.population), args=self._kwargs)
            self.logger.debug('selected {0} candidates'.format(len(parents)))
            offspring_cs = [copy.deepcopy(i.candidate) for i in parents]

            for op in variators:
                self.logger.debug('variation using {0} at generation {1} and evaluation {2}'.format(op.__name__, self.num_generations, self.num_evaluations))
                offspring_cs = op(random=self._random, candidates=offspring_cs, args=self._kwargs)
            self.logger.debug('created {0} offspring'.format(len(offspring_cs)))

            # Evaluate offspring.
            self.logger.debug('evaluation using {0} at generation {1} and evaluation {2}'.format(evaluator.__name__, self.num_generations, self.num_evaluations))
            offspring_fit = evaluator(candidates=offspring_cs, args=self._kwargs)
            offspring = []
            for cs, fit in zip(offspring_cs, offspring_fit):
                if fit is not None:
                    off = Individual(cs, maximize=maximize)
                    off.fitness = fit
                    offspring.append(off)
                else:
                    self.logger.warning('excluding candidate {0} because fitness received as None'.format(cs))
            self.num_evaluations += len(offspring_fit)

            # Replace individuals.
            self.logger.debug('replacement using {0} at generation {1} and evaluation {2}'.format(self.replacer.__name__, self.num_generations, self.num_evaluations))
            self.population = self.replacer(random=self._random, population=self.population, parents=parents, offspring=offspring, args=self._kwargs)
            self.logger.debug('population size is now {0}'.format(len(self.population)))

            # Migrate individuals.
            self.logger.debug('migration using {0} at generation {1} and evaluation {2}'.format(self.migrator.__name__, self.num_generations, self.num_evaluations))
            self.population = self.migrator(random=self._random, population=self.population, args=self._kwargs)
            self.logger.debug('population size is now {0}'.format(len(self.population)))

            # Archive individuals.
            self.logger.debug('archival using {0} at generation {1} and evaluation {2}'.format(self.archiver.__name__, self.num_generations, self.num_evaluations))
            self.archive = self.archiver(random=self._random, archive=self.archive, population=list(self.population), args=self._kwargs)
            self.logger.debug('archive size is now {0}'.format(len(self.archive)))
            self.logger.debug('population size is now {0}'.format(len(self.population)))

            self.num_generations += 1
            for obs in observers:
                self.logger.debug('observation using {0} at generation {1} and evaluation {2}'.format(obs.__name__, self.num_generations, self.num_evaluations))
                obs(population=list(self.population), num_generations=self.num_generations, num_evaluations=self.num_evaluations, args=self._kwargs)

        return self.population


class GA(EvolutionaryComputation):
    """Evolutionary computation representing a canonical genetic algorithm.

    This class represents a genetic algorithm which uses, by
    default, rank selection, `n`-point crossover, bit-flip mutation,
    and generational replacement. In the case of bit-flip mutation,
    it is expected that each candidate solution is a ``Sequence``
    of binary values.

    Optional keyword arguments in ``evolve`` args parameter:

    - *num_selected* -- the number of individuals to be selected
      (default len(population))
    - *crossover_rate* -- the rate at which crossover is performed
      (default 1.0)
    - *num_crossover_points* -- the `n` crossover points used (default 1)
    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
    - *num_elites* -- number of elites to consider (default 0)

    """
    def __init__(self, random):
        EvolutionaryComputation.__init__(self, random)
        self.selector = selectors.rank_selection
        self.variator = [variators.n_point_crossover, variators.bit_flip_mutation]
        self.replacer = replacers.generational_replacement

    def evolve(self, generator, evaluator, pop_size=100, seeds=None, maximize=True, bounder=None, **args):
        args.setdefault('num_selected', pop_size)
        return EvolutionaryComputation.evolve(self, generator, evaluator, pop_size, seeds, maximize, bounder, **args)


class ES(EvolutionaryComputation):
    """Evolutionary computation representing a canonical evolution strategy.

    This class represents an evolution strategy which uses, by
    default, the default selection (i.e., all individuals are selected),
    an internal adaptive mutation using strategy parameters, and 'plus'
    replacement. It is expected that each candidate solution is a ``Sequence``
    of real values.

    The candidate solutions to an ES are augmented by strategy parameters of
    the same length (using ``inspyred.ec.generators.strategize``). These
    strategy parameters are evolved along with the candidates and are used as
    the mutation rates for each element of the candidates. The evaluator is
    modified internally to use only the actual candidate elements (rather than
    also the strategy parameters), so normal evaluator functions may be used
    seamlessly.

    Optional keyword arguments in ``evolve`` args parameter:

    - *tau* -- a proportionality constant (default None)
    - *tau_prime* -- a proportionality constant (default None)
    - *epsilon* -- the minimum allowed strategy parameter (default 0.00001)

    If *tau* is ``None``, it will be set to ``1 / sqrt(2 * sqrt(n))``, where
    ``n`` is the length of a candidate. If *tau_prime* is ``None``, it will be
    set to ``1 / sqrt(2 * n)``. The strategy parameters are updated as follows:

    .. math::

        \\sigma_i^\\prime = \\sigma_i * e^{\\tau \\cdot N(0, 1) + \\tau^\\prime \\cdot N(0, 1)}

        \\sigma_i^\\prime = max(\\sigma_i^\\prime, \\epsilon)

    """
    def __init__(self, random):
        EvolutionaryComputation.__init__(self, random)
        self.selector = selectors.default_selection
        self.variator = self._internal_variation
        self.replacer = replacers.plus_replacement

    def _internal_variation(self, random, candidates, args):
        tau = args.setdefault('tau', None)
        tau_prime = args.setdefault('tau_prime', None)
        epsilon = args.setdefault('epsilon', 0.00001)
        mutants = []
        n = len(candidates[0]) // 2
        if tau is None:
            tau = 1 / math.sqrt(2 * math.sqrt(n))
        if tau_prime is None:
            tau_prime = 1 / math.sqrt(2 * n)
        for candidate in candidates:
            cand = candidate[:n]
            strat = candidate[n:]
            for i, s in enumerate(strat):
                strat[i] = s * math.exp(tau_prime * random.gauss(0, 1) + tau * random.gauss(0, 1))
                strat[i] = max(strat[i], epsilon)
            for i, (c, s) in enumerate(zip(cand, strat)):
                cand[i] = c + random.gauss(0, s)
            cand = self.bounder(cand, args)
            cand.extend(strat)
            mutants.append(cand)
        return mutants

    def _internal_evaluator(self, func):
        @functools.wraps(func)
        def evaluator(candidates, args):
            cands = []
            for candidate in candidates:
                n = len(candidate) // 2
                cands.append(candidate[:n])
            return func(cands, args)
        return evaluator

    def evolve(self, generator, evaluator, pop_size=100, seeds=None, maximize=True, bounder=None, **args):
        generator = generators.strategize(generator)
        evaluator = self._internal_evaluator(evaluator)
        # Strategize any seeds that are passed.
        strategy_seeds = None
        if seeds is not None:
            strategy_seeds = []
            for candidate in seeds:
                n = len(candidate)
                c = copy.copy(candidate)
                c.extend([self._random.random() for _ in range(n)])
                strategy_seeds.append(c)
        return EvolutionaryComputation.evolve(self, generator, evaluator, pop_size, strategy_seeds, maximize, bounder, **args)


class EDA(EvolutionaryComputation):
    """Evolutionary computation representing a canonical estimation of distribution algorithm.

    This class represents an estimation of distribution algorithm which
    uses, by default, truncation selection, an internal estimation of
    distribution variation, and generational replacement. It is expected
    that each candidate solution is a ``Sequence`` of real values.

    The variation used here creates a statistical model based on the set
    of candidates. The offspring are then generated from this model. This
    function also makes use of the bounder function as specified in the EC's
    ``evolve`` method.

    Optional keyword arguments in ``evolve`` args parameter:

    - *num_selected* -- the number of individuals to be selected
      (default len(population)/2)
    - *num_offspring* -- the number of offspring to create (default len(population))
    - *num_elites* -- number of elites to consider (default 0)

    """
    def __init__(self, random):
        EvolutionaryComputation.__init__(self, random)
        self.selector = selectors.truncation_selection
        self.variator = self._internal_variation
        self.replacer = replacers.generational_replacement

    def _internal_variation(self, random, candidates, args):
        num_offspring = args.setdefault('num_offspring', 1)
        bounder = args['_ec'].bounder
        num_genes = max([len(x) for x in candidates])
        genes = [[x[i] for x in candidates] for i in range(num_genes)]
        mean = [float(sum(x)) / float(len(x)) for x in genes]
        stdev = [sum([(x - m)**2 for x in g]) / float(len(g) - 1) for g, m in zip(genes, mean)]
        offspring = []
        for _ in range(num_offspring):
            child = copy.copy(candidates[0])
            for i, (m, s) in enumerate(zip(mean, stdev)):
                child[i] = m + random.gauss(0, s)
            child = bounder(child, args)
            offspring.append(child)
        return offspring

    def evolve(self, generator, evaluator, pop_size=100, seeds=None, maximize=True, bounder=None, **args):
        args.setdefault('num_selected', pop_size // 2)
        args.setdefault('num_offspring', pop_size)
        return EvolutionaryComputation.evolve(self, generator, evaluator, pop_size, seeds, maximize, bounder, **args)


class DEA(EvolutionaryComputation):
    """Evolutionary computation representing a differential evolutionary algorithm.

    This class represents a differential evolutionary algorithm which uses, by
    default, tournament selection, heuristic crossover, Gaussian mutation,
    and steady-state replacement. It is expected that each candidate solution
    is a ``Sequence`` of real values.

    Optional keyword arguments in ``evolve`` args parameter:

    - *num_selected* -- the number of individuals to be selected (default 2)
    - *tournament_size* -- the tournament size (default 2)
    - *crossover_rate* -- the rate at which crossover is performed
      (default 1.0)
    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
    - *gaussian_mean* -- the mean used in the Gaussian function (default 0)
    - *gaussian_stdev* -- the standard deviation used in the Gaussian function
      (default 1)

    """
    def __init__(self, random):
        EvolutionaryComputation.__init__(self, random)
        self.selector = selectors.tournament_selection
        self.variator = [variators.heuristic_crossover, variators.gaussian_mutation]
        self.replacer = replacers.steady_state_replacement

    def evolve(self, generator, evaluator, pop_size=100, seeds=None, maximize=True, bounder=None, **args):
        args.setdefault('num_selected', 2)
        return EvolutionaryComputation.evolve(self, generator, evaluator, pop_size, seeds, maximize, bounder, **args)


class SA(EvolutionaryComputation):
    """Evolutionary computation representing simulated annealing.

    This class represents a simulated annealing algorithm. It accomplishes this
    by using default selection (i.e., all individuals are parents), Gaussian
    mutation, and simulated annealing replacement. It is expected that each
    candidate solution is a ``Sequence`` of real values. Consult the
    documentation for the ``simulated_annealing_replacement`` for more
    details on the keyword arguments listed below.

    .. note::

       The ``pop_size`` parameter to ``evolve`` will always be set to 1,
       even if a different value is passed.

    Optional keyword arguments in ``evolve`` args parameter:

    - *temperature* -- the initial temperature
    - *cooling_rate* -- a real-valued coefficient in the range (0, 1)
      by which the temperature should be reduced
    - *mutation_rate* -- the rate at which mutation is performed (default 0.1)
    - *gaussian_mean* -- the mean used in the Gaussian function (default 0)
    - *gaussian_stdev* -- the standard deviation used in the Gaussian function
      (default 1)

    """
    def __init__(self, random):
        EvolutionaryComputation.__init__(self, random)
        self.selector = selectors.default_selection
        self.variator = variators.gaussian_mutation
        self.replacer = replacers.simulated_annealing_replacement

    def evolve(self, generator, evaluator, pop_size=1, seeds=None, maximize=True, bounder=None, **args):
        pop_size = 1
        return EvolutionaryComputation.evolve(self, generator, evaluator, pop_size, seeds, maximize, bounder, **args)
