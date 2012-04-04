"""
    ===============================================
    :mod:`evaluators` -- Fitness evaluation methods
    ===============================================
    
    Evaluator functions are problem-specific. This module provides pre-defined 
    evaluators for evolutionary computations.

    All evaluator functions have the following arguments:
    
    - *candidates* -- the candidate solutions
    - *args* -- a dictionary of keyword arguments
    
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
       
    .. module:: evaluators
    .. moduleauthor:: Aaron Garrett <aaron.lee.garrett@gmail.com>
    .. moduleauthor:: Jelle Feringa <jelleferinga@gmail.com>
"""
import functools
try:
    import cPickle as pickle
except ImportError:
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
    def ecspy_evaluator(candidates, args):
        fitness = []
        for candidate in candidates:
            fitness.append(evaluate(candidate, args))
        return fitness
    ecspy_evaluator.single_evaluation = evaluate
    return ecspy_evaluator
    

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
    import pp
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
        
