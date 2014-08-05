*******
Recipes
*******

This section provides a set of recipes that can be used to add additional functionality to inspyred. 
These recipes are not a part of the core library, but they have proven to be useful in the past for
real-world programs. If they continue to be useful, they may be incorporated into inspyred in a 
future version.

======================
Lexicographic Ordering
======================

In multiobjective optimization problems, alternatives to Pareto preference include linear weighting of the
objectives and prioritizing the objectives from most to least important. Both of these methods essentially
reduce the problem to a single objective optimization. Obviously, the weighting of the objectives would be
handled entirely in the evaluator for the problem, so no special recipe is needed. But the prioritizing
of the objectives, which is also known as lexicographic ordering, requires some additional effort. 

The fitness values for two individuals, *x* and *y*, should be compared such that, if the first objective
for *x* is "better" (i.e., lower when minimizing or higher when maximizing) than the first objective for
*y*, then *x* is considered "better" than *y*. If they are equal in that objective, then the second 
objective is considered in the same way. This process is repeated for all objectives.

The following recipe provides a class to deal with such comparisons that is intended to function much like
the ``inspyred.ec.emo.Pareto`` class.
[:download:`download <../recipes/lexicographic.py>`]

.. literalinclude:: ../recipes/lexicographic.py


====================
Constraint Selection
====================

Optimization problems often have to deal with constraints and constraint violations. The following recipe 
provides one example of how to handle such a thing with inspyred. Here, candidates represent ordered pairs
and their fitness is simply their distance from the origin. However, we provide a constraint that punishes
candidates that lie outside of the unit circle. Such a scenario should produce a candidate that lies on the
unit circle. Note also that ``crowding_replacement`` or some other fitness sharing or niching scheme could
be used to generate many such points on the circle.
[:download:`download <../recipes/constraint_selection.py>`]

.. literalinclude:: ../recipes/constraint_selection.py

=============================
Meta-Evolutionary Computation
=============================

The following recipe shows how an evolutionary computation can be used to evolve near-optimal operators and
parameters for another evolutionary computation. In the EC literature, such a thing is generally referred
to as a "meta-EC".
[:download:`download <../recipes/meta_ec.py>`]

.. literalinclude:: ../recipes/meta_ec.py

==============================
Micro-Evolutionary Computation
==============================

Another approach that has been successfully applied to some difficult problems is to use many small-population EC's
for small numbers of evaluations in succession. Each succeeding EC is seeded with the best solution from the 
previous run. This is somewhat akin to a random-restart hill-climbing approach, except that information about the 
best solution so far is passed along during each restart.
[:download:`download <../recipes/micro_ec.py>`]

.. literalinclude:: ../recipes/micro_ec.py

================
Network Migrator
================

The following custom migrator is a callable class (because the migrator must behave like a callback function)
that allows solutions to migrate from one network machine to another. It is assumed that the EC islands are 
running on the given IP:port combinations.
[:download:`download <../recipes/network_migrator.py>`]

.. literalinclude:: ../recipes/network_migrator.py



