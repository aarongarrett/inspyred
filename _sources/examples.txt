********
Examples
********

For many people, it is easiest to learn a new library by adapting existing examples to 
their purposes. For that reason, many examples are presented in this section in the 
hope that they will prove useful to others using inspyred.

===================
Standard Algorithms
===================

The following examples illustrate how to use the different, built-in, evolutionary computations.
They are (hopefully) simple and self-explanatory. Please note that each one uses an existing
benchmark problem. This is just an expedience; it is not necessary. The full list of existing 
benchmarks can be found in the :doc:`reference`. See the :doc:`tutorial` for examples that 
do not make use of a benchmark problem. 

-----------------
Genetic Algorithm
-----------------

In this example, a GA is used to evolve a solution to the binary version of the Schwefel benchmark. 
[:download:`download <../examples/standard/ga_example.py>`]

.. literalinclude:: ../examples/standard/ga_example.py

------------------
Evolution Strategy
------------------

In this example, an ES is used to evolve a solution to the Rosenbrock benchmark.
[:download:`download <../examples/standard/es_example.py>`]

.. literalinclude:: ../examples/standard/es_example.py

-------------------
Simulated Annealing
-------------------

In this example, an SA is used to evolve a solution to the Sphere benchmark.
[:download:`download <../examples/standard/sa_example.py>`]

.. literalinclude:: ../examples/standard/sa_example.py

--------------------------------
Differential Evolution Algorithm
--------------------------------

In this example, a DEA is used to evolve a solution to the Griewank benchmark.
[:download:`download <../examples/standard/dea_example.py>`]

.. literalinclude:: ../examples/standard/dea_example.py

------------------------------------
Estimation of Distribution Algorithm
------------------------------------

In this example, an EDA is used to evolve a solution to the Rastrigin benchmark.
[:download:`download <../examples/standard/eda_example.py>`]

.. literalinclude:: ../examples/standard/eda_example.py

-----------------------------------------
Pareto Archived Evolution Strategy (PAES)
-----------------------------------------

In this example, a PAES is used to evolve a solution to the Kursawe multiobjective benchmark.
[:download:`download <../examples/standard/paes_example.py>`]

.. literalinclude:: ../examples/standard/paes_example.py

------------------------------------------------
Nondominated Sorting Genetic Algorithm (NSGA-II)
------------------------------------------------

In this example, an NSGA2 is used to evolve a solution to the Kursawe multiobjective benchmark.
[:download:`download <../examples/standard/nsga_example.py>`]

.. literalinclude:: ../examples/standard/nsga_example.py

---------------------------
Particle Swarm Optimization
---------------------------

In this example, a PSO is used to evolve a solution to the Ackley benchmark.
[:download:`download <../examples/standard/pso_example.py>`]

.. literalinclude:: ../examples/standard/pso_example.py

-----------------------
Ant Colony Optimization
-----------------------

In this example, an ACS is used to evolve a solution to the TSP benchmark.
[:download:`download <../examples/standard/acs_example.py>`]

.. literalinclude:: ../examples/standard/acs_example.py

=====================
Customized Algorithms
=====================

The true benefit of the inspyred library is that it allows the programmer to customize
almost every aspect of the algorithm. This is accomplished primarily through the use of 
function (or function-like) callbacks that can be specified by the programmer. The 
following examples show how to customize many different parts of the evolutionary
computation.

-------------------------------
Custom Evolutionary Computation
-------------------------------

In this example, an evolutionary computation is created which uses tournament selection, 
uniform crossover, Gaussian mutation, and steady-state replacement.
[:download:`download <../examples/custom/custom_ec_example.py>`]

.. literalinclude:: ../examples/custom/custom_ec_example.py

---------------
Custom Archiver
---------------

The purpose of the archiver is to provide a mechanism for candidate solutions to be 
maintained without necessarily remaining in the population. This is important for 
most multiobjective evolutionary approaches, but it can also be useful for single-objective
problems, as well. In this example, an archiver is created that maintains the *worst*
individual found. (There is no imaginable reason why one might actually do this. It 
is just for illustration purposes.)
[:download:`download <../examples/custom/custom_archiver_example.py>`]

.. literalinclude:: ../examples/custom/custom_archiver_example.py

---------------
Custom Observer
---------------

Sometimes it is helpful to see certain aspects of the current population as it evolves.
The purpose of the "observer" functions is to provide a function that executes at the
end of each generation so that the process can be monitored accordingly. In this example,
the only information desired at each generation is the current best individual.
[:download:`download <../examples/custom/custom_observer_example.py>`]

.. literalinclude:: ../examples/custom/custom_observer_example.py

---------------
Custom Replacer
---------------

The replacers are used to determine which of the parents, offspring, and current population
should survive into the next generation. In this example, survivors are determined to be top 50% of
individuals from the population along with 50% chosen randomly from the offspring. (Once again, this
is simply an example. There may be no good reason to create such a replacement scheme.)
[:download:`download <../examples/custom/custom_replacer_example.py>`]

.. literalinclude:: ../examples/custom/custom_replacer_example.py

---------------
Custom Selector
---------------

The selectors are used to determine which individuals in the population should become parents. 
In this example, parents are chosen such that 50% of the time the best individual in the population 
is chosen to be a parent and 50% of the time a random individual is chosen. As before, this is an 
example selector that may have little practical value.
[:download:`download <../examples/custom/custom_selector_example.py>`]

.. literalinclude:: ../examples/custom/custom_selector_example.py

-----------------
Custom Terminator
-----------------

The terminators are used to determine when the evolutionary process should end. All terminators
return a Boolean value where True implies that the evolution should end. In this example, the evolution
should continue until the average Hamming distance between all combinations of candidates falls below
a specified minimum.
[:download:`download <../examples/custom/custom_terminator_example.py>`]

.. literalinclude:: ../examples/custom/custom_terminator_example.py

---------------
Custom Variator
---------------

The variators provide what are normally classified as "crossover" and "mutation," however
even more exotic variators can be defined. Remember that a list of variators can be specified 
that will act as a pipeline with the output of the first being used as the input to the second, etc.
In this example, the binary candidate is mutated such that two points are chosen and the bits
between each point are put in reverse order. For example, ``0010100100`` would become ``0010010100`` 
if the third and eighth bits are the chosen points.
[:download:`download <../examples/custom/custom_variator_example.py>`]

.. literalinclude:: ../examples/custom/custom_variator_example.py

==============
Advanced Usage
==============

The examples in this section deal with less commonly used aspects of the library. 
Be aware that these parts may not have received as much testing as the more 
core components exemplified above.

---------------------
Discrete Optimization
---------------------

Discrete optimization problems often present difficulties for naive evolutionary
computation approaches. Special care must be taken to generate and maintain
feasible solutions and/or to sufficiently penalize infeasible solutions.
Ant colony optimization approaches were created to deal with discrete optimization 
problems. In these examples, we consider two of the most famous discrete optimization
benchmark problems -- the Traveling Salesman Problem (TSP) and the Knapsack
problem. The background on these problems is omitted here because it can easily
be found elsewhere. 

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The Traveling Salesman Problem
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Candidate solutions for the TSP can be most easily be represented as permutations
of the list of city numbers (enumerating the order in which cities should be 
visited). For instance, if there are 5 cities, then a candidate solution might 
be ``[4, 1, 0, 2, 3]``. This is how the ``TSP`` benchmark represents solutions. 
However, this simple representation forces us to work harder to ensure that our 
solutions remain feasible during crossover and mutation. Therefore, we need
to use variators suited to the task, as shown in the example below.
[:download:`download <../examples/advanced/tsp_ec_example.py>`]

.. literalinclude:: ../examples/advanced/tsp_ec_example.py

As an alternative, we can use ant colony optimization to solve the TSP. This
example was shown previously, but it is presented again here for completeness.
[:download:`download <../examples/standard/acs_example.py>`]

.. literalinclude:: ../examples/standard/acs_example.py

^^^^^^^^^^^^^^^^^^^^
The Knapsack Problem
^^^^^^^^^^^^^^^^^^^^

Candidate solutions for the Knapsack problem can be represented as either a binary
list (for the 0/1 Knapsack) or as a list of non-negative integers (for the Knapsack
with duplicates). In each case, the list is the same length as the number of items,
and each element of the list corresponds to the quantity of the corresponding item
to place in the knapsack. For the evolutionary computation, we can use 
``uniform_crossover`` *and* ``gaussian_mutation``. The reason we are able to use
Gaussian mutation here, even though the candidates are composed of discrete values,
is because the bounder created by the ``Knapsack`` benchmark is an instance of
``DiscreteBounder``, which automatically moves an illegal component to its nearest
legal value.
[:download:`download <../examples/advanced/knapsack_ec_example.py>`]

.. literalinclude:: ../examples/advanced/knapsack_ec_example.py

Once again, as an alternative we can use ant colony optimization. Just for variety, 
we'll use it to solve the 0/1 Knapsack problem (``duplicates=False``).
[:download:`download <../examples/advanced/knapsack_acs_example.py>`]

.. literalinclude:: ../examples/advanced/knapsack_acs_example.py

-----------------------------------
Evaluating Individuals Concurrently
-----------------------------------

One of the most lauded aspects of many bio-inspired algorithms is their
inherent parallelism. Taking advantage of this parallelism is important in
real-world problems, which are often computationally expensive. There are
two approaches available in inspyred to perform parallel evaluations for
candidate solutions. The first makes use of the ``multiprocessing`` module
that exists in core Python 2.6+. The second makes use of a third-party
library called `Parallel Python <http://www.parallelpython.com>`_ (pp), 
which can be used for either multi-core processing on a single machine or
distributed processing across a network.

^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
The ``multiprocessing`` Module
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Using the ``multiprocessing`` approach to parallel evaluations is probably
the better choice if all evaluations are going to be split among multiple
processors or cores on a single machine. This is because the module is part
of the core Python library (2.6+) and provides a simple, standard interface 
for setting up the parallelism. As shown in the example below, the only 
additional parameter is the name of the "actual" evaluation function and 
the (optional) number of CPUs to use.
[:download:`download <../examples/advanced/parallel_evaluation_mp_example.py>`]

.. literalinclude:: ../examples/advanced/parallel_evaluation_mp_example.py

^^^^^^^^^^^^^^^
Parallel Python
^^^^^^^^^^^^^^^

The Parallel Python approach to multiprocessing is best suited for use across
a network of computers (though it *can* be used on a single machine, as well). 
It takes just a little effort to install and setup pp 
on each machine, but once it's complete, the network becomes a very efficient 
computing cluster. This is a capability that the ``multiprocessing`` approach
simply does not have, and it provides incredible scalability. However, pp 
requires additional, non-standard parameters to be passed in, as illustrated
in the example below.
[:download:`download <../examples/advanced/parallel_evaluation_pp_example.py>`]

.. literalinclude:: ../examples/advanced/parallel_evaluation_pp_example.py

-------------
Island Models
-------------

Along with parallel evaluation of the fitness, it is also possible to create
different populations that evolve independently but are capable of sharing
solutions among themselves. Such approaches are known as "island models" and
can be accomplished within inspyred by making use of the migrator callback.
The following example illustrates a very simple two-island model using the
``inspyred.ec.migrators.MultiprocessingMigrator`` migrator. Remember that
custom migrators can easily be constructed for more specific needs.
[:download:`download <../examples/advanced/islands_example.py>`]

.. literalinclude:: ../examples/advanced/islands_example.py

-----------------------
Replacement via Niching
-----------------------
 
An example of a not-quite-standard replacer is the ``crowding_replacement`` which 
provides a niching capability. An example using this replacer is given below. Here,
the candidates are just single numbers (but created as singleton lists so as to
be ``Sequence`` types for some of the built-in operators) between 0 and 26. Their
fitness values are simply the value of the sine function using the candidate value
as input. Since the sine function is periodic and goes through four periods between
0 and 26, this function is multimodal. So we can use ``crowding_replacement`` to
ensure that all maxima are found.
[:download:`download <../examples/advanced/niche_example.py>`]

.. literalinclude:: ../examples/advanced/niche_example.py




