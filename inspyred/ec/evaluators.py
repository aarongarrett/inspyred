"""
    ===============================================
    :mod:`evaluators` -- Fitness evaluation methods
    ===============================================

    Evaluator functions are problem-specific. This module provides pre-defined
    evaluators for evolutionary computations.

    All evaluator functions have the following arguments:

    - *candidates* -- the candidate solutions
    - *args* -- a dictionary of keyword arguments

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

    .. module:: evaluators
    .. moduleauthor:: Aaron Garrett <garrett@inspiredintelligence.io>
    .. moduleauthor:: Jelle Feringa <jelleferinga@gmail.com>
"""
import functools
import pickle


def evaluator(evaluate):
    """Return an inspyred evaluator function based on the given function.

    This function generator takes a function that evaluates only one
    candidate. The generator handles the iteration over each candidate
    to be evaluated.

    The given function ``evaluate`` must have the following signature::

        fitness = evaluate(candidate, args)

    This function is most commonly used as a function decorator with
    the following usage::

        @evaluator
        def evaluate(candidate, args):
            # Implementation of evaluation
            pass

    The generated function also contains an attribute named
    ``single_evaluation`` which holds the original evaluation function.
    In this way, the original single-candidate function can be
    retrieved if necessary.

    """
    @functools.wraps(evaluate)
    def inspyred_evaluator(candidates, args):
        fitness = []
        for candidate in candidates:
            fitness.append(evaluate(candidate, args))
        return fitness
    inspyred_evaluator.single_evaluation = evaluate
    return inspyred_evaluator


def parallel_evaluation_pp(candidates, args):
    """Evaluate the candidates in parallel using Parallel Python.

    This function allows parallel evaluation of candidate solutions.
    It uses the `Parallel Python <http://www.parallelpython.com>`_  (pp)
    library to accomplish the parallelization. This library must already
    be installed in order to use this function. The function assigns the
    evaluation of each candidate to its own job, all of which are then
    distributed to the available processing units.

    .. note::

       All arguments to the evaluation function must be pickleable.
       Those that are not will not be sent through the ``args`` variable
       and will be unavailable to your function.

    .. Arguments:
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments

    Required keyword arguments in args:

    - *pp_evaluator* -- actual evaluation function to be used (This function
      should have the same signature as any other inspyred evaluation function.)

    Optional keyword arguments in args:

    - *pp_dependencies* -- tuple of functional dependencies of the serial
      evaluator (default ())
    - *pp_modules* -- tuple of modules that must be imported for the
      functional dependencies (default ())
    - *pp_servers* -- tuple of servers (on a cluster) that will be used
      for parallel processing (default ("*",))
    - *pp_secret* -- string representing the secret key needed to authenticate
      on a worker node (default "inspyred")
    - *pp_nprocs* -- integer representing the number of worker processes to
      start on the local machine (default "autodetect", which sets it to the
      number of processors in the system)

    For more information about these arguments, please consult the
    documentation for `Parallel Python <http://www.parallelpython.com>`_.

    """
    import ppft as pp
    logger = args['_ec'].logger

    try:
        evaluator = args['pp_evaluator']
    except KeyError:
        logger.error('parallel_evaluation_pp requires \'pp_evaluator\' be defined in the keyword arguments list')
        raise
    secret_key = args.setdefault('pp_secret', 'inspyred')
    try:
        job_server = args['_pp_job_server']
    except KeyError:
        pp_servers = args.get('pp_servers', ("*",))
        pp_nprocs = args.get('pp_nprocs', 'autodetect')
        job_server = pp.Server(ncpus=pp_nprocs, ppservers=pp_servers, secret=secret_key)
        args['_pp_job_server'] = job_server
    pp_depends = args.setdefault('pp_dependencies', ())
    pp_modules = args.setdefault('pp_modules', ())

    pickled_args = {}
    for key in args:
        try:
            pickle.dumps(args[key])
            pickled_args[key] = args[key]
        except (TypeError, pickle.PickleError, pickle.PicklingError):
            logger.debug('unable to pickle args parameter {0} in parallel_evaluation_pp'.format(key))
            pass

    func_template = pp.Template(job_server, evaluator, pp_depends, pp_modules)
    jobs = [func_template.submit([c], pickled_args) for c in candidates]

    fitness = []
    for i, job in enumerate(jobs):
        r = job()
        try:
            fitness.append(r[0])
        except TypeError:
            logger.warning('parallel_evaluation_pp generated an invalid fitness for candidate {0}'.format(candidates[i]))
            fitness.append(None)
    return fitness


def parallel_evaluation_mp(candidates, args):
    """Evaluate the candidates in parallel using ``multiprocessing``.

    This function allows parallel evaluation of candidate solutions.
    It uses the standard multiprocessing library to accomplish the
    parallelization. The function assigns the evaluation of each
    candidate to its own job, all of which are then distributed to the
    available processing units.

    .. note::

       All arguments to the evaluation function must be pickleable.
       Those that are not will not be sent through the ``args`` variable
       and will be unavailable to your function.

    .. Arguments:
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments

    Required keyword arguments in args:

    - *mp_evaluator* -- actual evaluation function to be used (This function
      should have the same signature as any other inspyred evaluation function.)

    Optional keyword arguments in args:

    - *mp_nprocs* -- number of processors that will be used (default machine
      cpu count)

    """
    import time
    import multiprocessing
    logger = args['_ec'].logger

    try:
        evaluator = args['mp_evaluator']
    except KeyError:
        logger.error('parallel_evaluation_mp requires \'mp_evaluator\' be defined in the keyword arguments list')
        raise
    try:
        nprocs = args['mp_nprocs']
    except KeyError:
        nprocs = multiprocessing.cpu_count()

    pickled_args = {}
    for key in args:
        try:
            pickle.dumps(args[key])
            pickled_args[key] = args[key]
        except (TypeError, pickle.PickleError, pickle.PicklingError):
            logger.debug('unable to pickle args parameter {0} in parallel_evaluation_mp'.format(key))
            pass

    start = time.time()
    try:
        pool = multiprocessing.Pool(processes=nprocs)
        results = [pool.apply_async(evaluator, ([c], pickled_args)) for c in candidates]
        pool.close()
        pool.join()
        return [r.get()[0] for r in results]
    except (OSError, RuntimeError) as e:
        logger.error('failed parallel_evaluation_mp: {0}'.format(str(e)))
        raise
    else:
        end = time.time()
        logger.debug('completed parallel_evaluation_mp in {0} seconds'.format(end - start))

