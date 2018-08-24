======================================================================================================
``inspyred`` -- A framework for creating bio-inspired computational intelligence algorithms in Python.
======================================================================================================


.. image:: https://img.shields.io/pypi/v/inspyred.svg
        :target: https://pypi.python.org/pypi/inspyred

.. image:: https://img.shields.io/travis/aarongarrett/inspyred.svg
        :target: https://travis-ci.org/aarongarrett/inspyred

.. image:: https://readthedocs.org/projects/inspyred/badge/?version=latest
        :target: https://inspyred.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/aarongarrett/inspyred/shield.svg
     :target: https://pyup.io/repos/github/aarongarrett/inspyred/
     :alt: Updates


inspyred is a free, open source framework for creating biologically-inspired 
computational intelligence algorithms in Python, including evolutionary 
computation, swarm intelligence, and immunocomputing. Additionally, inspyred 
provides easy-to-use canonical versions of many bio-inspired algorithms for 
users who do not need much customization.


Example
-------

The following example illustrates the basics of the inspyred package. In this 
example, candidate solutions are 10-bit binary strings whose decimal values 
should be maximized::

    import random 
    import time 
    import inspyred
    
    def generate_binary(random, args):
        bits = args.get('num_bits', 8)
        return [random.choice([0, 1]) for i in range(bits)]
    
    @inspyred.ec.evaluators.evaluator
    def evaluate_binary(candidate, args):
        return int("".join([str(c) for c in candidate]), 2)
    
    rand = random.Random()
    rand.seed(int(time.time()))
    ga = inspyred.ec.GA(rand)
    ga.observer = inspyred.ec.observers.stats_observer
    ga.terminator = inspyred.ec.terminators.evaluation_termination
    final_pop = ga.evolve(evaluator=evaluate_binary,
                          generator=generate_binary,
                          max_evaluations=1000,
                          num_elites=1,
                          pop_size=100,
                          num_bits=10)
    final_pop.sort(reverse=True)
    for ind in final_pop:
        print(str(ind))


Requirements
------------

  * Requires at least Python 2.6+ or 3+.
  * Numpy and Pylab are required for several functions in ``ec.observers``.
  * Pylab and Matplotlib are required for several functions in ``ec.analysis``.
  * Parallel Python (pp) is required if ``ec.evaluators.parallel_evaluation_pp`` is used.


License
-------

This package is distributed under the MIT License. This license can be found 
online at http://www.opensource.org/licenses/MIT.
  

Resources
---------

  * Homepage: http://aarongarrett.github.io/inspyred
  * Email: garrett@inspiredintelligence.io
  * Documentation: https://inspyred.readthedocs.io.

Citing
------
Garrett, A. (2012). inspyred (Version 1.0.1) [software]. Inspired Intelligence. Retrieved from https://github.com/aarongarrett/inspyred [accessed CURRENT DATE].

Features
--------

* TODO

Credits
---------

This package was created with Cookiecutter_ and the `audreyr/cookiecutter-pypackage`_ project template.

.. _Cookiecutter: https://github.com/audreyr/cookiecutter
.. _`audreyr/cookiecutter-pypackage`: https://github.com/audreyr/cookiecutter-pypackage

