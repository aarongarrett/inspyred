***************
Troubleshooting
***************

Given the flexibility of the inspyred library, along with the inherent stochasticity of the algorithms, it can be difficult to track down errors that will inevitably arise. This chapter provides some suggestions that may make the process easier. 

=====================
Always Store the Seed
=====================

Every inspyred algorithm requires that a pseudo-random number generator (PRNG) object be passed to it. This allows users to make use of different PRNGs if more sophisticated random number generation is desired (as long as it implements the relevant methods of Python's ``Random`` class). This also means that the PRNG must be seeded prior to its passing to an inspyred algorithm. This seed should always be printed (preferably to a file) in case the exact run of the algorithm needs to be duplicated. If an error occurs in a given run, it can be restarted by providing the same seed. The following code provides an example::

   import random
   import time
   my_seed = int(time.time())
   seedfile = open('randomseed.txt', 'w')
   seedfile.write('{0}'.format(my_seed))
   seedfile.close()
   prng = random.Random()
   prng.seed(my_seed)

========================
Use and Consult the Logs
========================

All inspyred algorithms provide detailed debugging data using Python's core ``logging`` module. This can be enabled by adding the following code to the ``main`` or calling scope::

   import logging
   logger = logging.getLogger('inspyred.ec')
   logger.setLevel(logging.DEBUG)
   file_handler = logging.FileHandler('inspyred.log', mode='w')
   file_handler.setLevel(logging.DEBUG)
   formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
   file_handler.setFormatter(formatter)
   logger.addHandler(file_handler)

Consulting the log file will often reveal which component is misbehaving or behaving unexpectedly.

===================================
Choose Operators that Work Together
===================================

The inspyred library gives users freedom to combine operators in almost any way they choose. However, this freedom means that the library will be unable to alert the user when a particular combination of operators produces a nonsensical algorithm. Remember that the operators must work together. For example, tournament selection may be employed to select 20 individuals from a population of 100. Then Gaussian mutation may be used to create 20 offspring. Finally, generational replacement may create the next generation from those offspring. The library will allow this, even though it means that, for at least the first generation, the population size is not constant. (It drops from 100 to 20.) The reason such a thing is allowed is because there may be a need for an algorithm that requires a non-constant population size. The inspyred library does not restrict any such algorithm. It is up to the user to ensure that all components work together to achieve the desired ends. (As stated previously, consulting the log file can help determine whether operators are combined correctly.)

=====================
Converting from ecspy
=====================

Users of the ecspy library, the precursor to inspyred, may want to modify their code to use the new library instead. The best advice in such a case would be to find a similar example from the inspyred documentation and use it as a basis for the existing code. The problem-specific generator and evaluator functions will probably not need to be changed (depending on their level of separation from the library itself), but the library functionality will probably change around them. Custom operators will similarly probably need only minor changes, if any. 

However, the pre-defined operators have been both modified and expanded. Existing keyword arguments should be checked carefully against the inspyred documentation to ensure that they are correct. An incorrectly named keyword argument will pass through unnoticed by the algorithm, and the default value will be used. For instance, in ecspy, a keyword argument for ``tournament_selection`` was *tourn_size*. In inspyred, it has been more clearly named *tournament_size*. If code from ecspy is used without modification, then the tournament selection will use 2 (the default) as the tournament size, regardless of the setting for *tourn_size*. In all cases, consult the documentation to ensure that the appropriate keyword arguments are used.








