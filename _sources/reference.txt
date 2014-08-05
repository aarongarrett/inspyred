*****************
Library Reference
*****************

This chapter provides a complete reference to all of the functionality included in inspyred.

========================
Evolutionary Computation
========================

.. automodule:: inspyred.ec
   :members:

.. automodule:: inspyred.ec.emo
   :members:
   
.. automodule:: inspyred.ec.analysis
   :members:
   
.. automodule:: inspyred.ec.utilities
   :members:

---------
Operators
---------

An evolutionary computation is composed of many parts:

- an archiver -- stores solutions separate from the population (e.g., in a multiobjective EC)
- an evaluator -- measures the fitness of candidate solutions; problem-dependent
- a generator -- creates new candidate solutions; problem-dependent
- a migrator -- moves individuals to other populations (in the case of distributed ECs) 
- observers -- view the progress of an EC in operation; may be a list of observers
- a replacer -- determines the survivors of a generation
- a selector -- determines the parents of a generation
- terminators -- determine whether the evolution should stop; may be a list of terminators
- variators -- modify candidate solutions; may be a list of variators

Each of these parts may be specified to create custom ECs to suit particular problems.

.. automodule:: inspyred.ec.archivers
   :members:
   
.. automodule:: inspyred.ec.evaluators
   :members:
   
.. automodule:: inspyred.ec.generators
   :members:
   
.. automodule:: inspyred.ec.migrators
   :members:
   
.. automodule:: inspyred.ec.observers
   :members:
   
.. automodule:: inspyred.ec.replacers
   :members:
   
.. automodule:: inspyred.ec.selectors
   :members:
   
.. automodule:: inspyred.ec.terminators
   :members:
   
.. automodule:: inspyred.ec.variators
   :members:

==================
Swarm Intelligence
==================

.. automodule:: inspyred.swarm
   :members:
   
.. automodule:: inspyred.swarm.topologies
   :members:

==================
Benchmark Problems
==================

.. automodule:: inspyred.benchmarks

.. autoclass:: inspyred.benchmarks.Benchmark
   :members:
   
.. autoclass:: inspyred.benchmarks.Binary
   :members:
   
---------------------------
Single-Objective Benchmarks
---------------------------

.. autoclass:: inspyred.benchmarks.Ackley
   :members:
   
.. autoclass:: inspyred.benchmarks.Griewank
   :members:
   
.. autoclass:: inspyred.benchmarks.Rastrigin
   :members:
   
.. autoclass:: inspyred.benchmarks.Rosenbrock
   :members:
   
.. autoclass:: inspyred.benchmarks.Schwefel
   :members:
   
.. autoclass:: inspyred.benchmarks.Sphere
   :members:
   
--------------------------
Multi-Objective Benchmarks
--------------------------

.. autoclass:: inspyred.benchmarks.Kursawe
   :members:
   
.. autoclass:: inspyred.benchmarks.DTLZ1
   :members:
   
.. autoclass:: inspyred.benchmarks.DTLZ2
   :members:
   
.. autoclass:: inspyred.benchmarks.DTLZ3
   :members:
   
.. autoclass:: inspyred.benchmarks.DTLZ4
   :members:
   
.. autoclass:: inspyred.benchmarks.DTLZ5
   :members:
   
.. autoclass:: inspyred.benchmarks.DTLZ6
   :members:
   
.. autoclass:: inspyred.benchmarks.DTLZ7
   :members:
   
--------------------------------
Discrete Optimization Benchmarks
--------------------------------

.. autoclass:: inspyred.benchmarks.Knapsack
   :members:

.. autoclass:: inspyred.benchmarks.TSP
   :members:



