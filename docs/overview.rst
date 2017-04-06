********
Overview
********

This chapter presents an overview of the inspyred library. 

========================
Bio-inspired Computation
========================

Biologically-inspired computation encompasses a broad range of algorithms including evolutionary computation, swarm intelligence, and neural networks. These concepts are sometimes grouped together under a similar umbrella term -- "computational intelligence" -- which is a subfield of artificial intelligence. The common theme among all such algorithms is a decentralized, bottom-up approach which often leads to emergent properties or behaviors. 


==================
Design Methodology
==================

The inspyred library grew out of insights from Ken de Jong's book "Evolutionary Computation: A Unified Approach." The goal of the library is to separate problem-specific computation from algorithm-specific computation. Any bio-inspired algorithm has at least two aspects that are entirely problem-specific: what solutions to the problem look like and how such solutions are evaluated. These components will certainly change from problem to problem. For instance, a problem dealing with optimizing the volume of a box might represent solutions as a three-element list of real values for the length, width, and height, respectively. In contrast, a problem dealing with optimizing a set of rules for escaping a maze might represent solutions as a list of pair of elements, where each pair contains the two-dimensional neighborhood and the action to take in such a case.

On the other hand, there are algorithm-specific components that may make no (or only modest) assumptions about the type of solutions upon which they operate. These components include the mechanism by which parents are selected, the way offspring are generated, and the way individuals are replaced in succeeding generations. For example, the ever-popular tournament selection scheme makes no assumptions whatsoever about the type of solutions it is selecting. The *n*-point crossover operator, on the other hand, does make an assumption that the solutions will be linear lists that can be "sliced up," but it makes no assumptions about the contents of such lists. They could be lists of numbers, strings, other lists, or something even more exotic.

The central design principle for inspyred is to separate problem-specific components from algorithm-specific components in a clean way so as to make algorithms as general as possible across a range of different problems.

For instance, the inspyred library views evolutionary computations as being composed of the following parts:

* Problem-specific components

  * A generator that defines how solutions are created
  * An evaluator that defines how fitness values are calculated for solutions

* Algorithm-specific evolutionary operators

  * An observer that defines how the user can monitor the state of the evolution
  * A terminator that determines whether the evolution should end
  * A selector that determines which individuals should become parents
  * A variator that determines how offspring are created from existing individuals
  * A replacer that determines which individuals should survive into the next generation
  * A migrator that defines how solutions are transferred among different populations
  * An archiver that defines how existing solutions are stored outside of the current population

Each of these components is specified by a function (or function-like) callback that the user can supply. The general flow of the ``evolve`` method in inspyred is as follows, where user-supplied callback functions are in ALL-CAPS:

::

    Create the initial population using the specified candidate seeds and the GENERATOR
    Evaluate the initial population using the EVALUATOR
    Set the number of evaluations to the size of the initial population
    Set the number of generations to 0
    Call the OBSERVER on the initial population
    While the TERMINATOR is not true Loop
        Choose parents via the SELECTOR
        Initialize offspring to the parents
        For each VARIATOR Loop
            Set offspring to the output of the VARIATOR on the offspring
        Evaluate offspring using the EVALUATOR
        Update the number of evaluations
        Replace individuals in the current population using the REPLACER
        Migrate individuals in the current population using the MIGRATOR
        Archive individuals in the current population using the ARCHIVER
        Increment the number of generations
        Call the OBSERVER on the current population

The observer, terminator, and variator callbacks may be lists or tuples of functions, rather
than just a single function. In each case, the functions are called sequentially in the order
listed. Unlike the other two, however, the variator behaves like a pipeline, where the output 
from one call is used as the input for the subsequent call.

============
Installation
============

The easiest way to install inspyred is to use `pip <http://www.pip-installer.org/en/latest/index.html>`_ as follows::

   pip install inspyred

The Python Package Index page for inspyred is http://pypi.python.org/pypi/inspyred.

The source code git repository can be found at https://github.com/inspyred/inspyred.

============
Getting Help
============

Any questions about the library and its use can be posted to the inspyred Google group at
https://groups.google.com/forum/#!forum/inspyred. If a forum posting is not appropriate or desired,
questions can also be emailed directly to aaron.lee.garrett@gmail.com. Feedback is always appreciated.
Please let us know how you're using the library and any ideas you might have for enhancements.


