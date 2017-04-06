"""
    ===================================================
    :mod:`terminators` -- Algorithm termination methods
    ===================================================
    
    This module provides pre-defined terminators for evolutionary computations.
    
    Terminators specify when the evolutionary process should end. All 
    terminators must return a Boolean value where True implies that 
    the evolution should end. 
    
    All terminator functions have the following arguments:
    
    - *population* -- the population of Individuals
    - *num_generations* -- the number of elapsed generations
    - *num_evaluations* -- the number of candidate solution evaluations
    - *args* -- a dictionary of keyword arguments
    
    .. note::
    
       The *population* is really a shallow copy of the actual population of
       the evolutionary computation. This means that any activities like
       sorting will not affect the actual population.    
    
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
        
    .. module:: terminators
    .. moduleauthor:: Aaron Garrett <garrett@inspiredintelligence.io>
"""
import itertools
import math
import sys
import time


def default_termination(population, num_generations, num_evaluations, args):
    """Return True.
    
    This function acts as a default termination criterion for an evolutionary computation.
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
    
    """
    return True
    

def diversity_termination(population, num_generations, num_evaluations, args):
    """Return True if population diversity is less than a minimum diversity.
    
    This function calculates the Euclidean distance between every pair of
    individuals in the population. It then compares the maximum of those
    distances with a specified minimum required diversity. This terminator 
    is really only well-defined for candidate solutions which are list 
    types of numeric values. 
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
    
    Optional keyword arguments in args:
    
    - *min_diversity* -- the minimum population diversity allowed (default 0.001)
    
    """
    min_diversity = args.setdefault('min_diversity', 0.001)
    cart_prod = itertools.product(population, population)
    distance = []
    for (p, q) in cart_prod:
        d = 0
        for x, y in zip(p.candidate, q.candidate):
            d += (x - y)**2
        distance.append(math.sqrt(d))
    return max(distance) < min_diversity

    
def average_fitness_termination(population, num_generations, num_evaluations, args):
    """Return True if the population's average fitness is near its best fitness.
    
    This function calculates the average fitness of the population, as well
    as the best fitness. If the difference between those values is less 
    than a specified tolerance, the function returns True. 
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
    
    Optional keyword arguments in args:
    
    - *tolerance* -- the minimum allowable difference between average 
      and best fitness (default 0.001)
    
    """
    tolerance = args.setdefault('tolerance', 0.001)
    avg_fit = sum([x.fitness for x in population]) / float(len(population))
    best_fit = max([x.fitness for x in population])
    return (best_fit - avg_fit) < tolerance


def evaluation_termination(population, num_generations, num_evaluations, args):
    """Return True if the number of function evaluations meets or exceeds a maximum.
    
    This function compares the number of function evaluations that have been 
    generated with a specified maximum. It returns True if the maximum is met
    or exceeded.
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
    
    Optional keyword arguments in args:
    
    - *max_evaluations* -- the maximum candidate solution evaluations (default 
      len(population)) 
    
    """
    max_evaluations = args.setdefault('max_evaluations', len(population))
    return num_evaluations >= max_evaluations


def generation_termination(population, num_generations, num_evaluations, args):
    """Return True if the number of generations meets or exceeds a maximum.
    
    This function compares the number of generations with a specified 
    maximum. It returns True if the maximum is met or exceeded.
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
    
    Optional keyword arguments in args:
    
    - *max_generations* -- the maximum generations (default 1) 
    
    """
    max_generations = args.setdefault('max_generations', 1)
    return num_generations >= max_generations

    
def time_termination(population, num_generations, num_evaluations, args):
    """Return True if the elapsed time meets or exceeds a duration of time.
    
    This function compares the elapsed time with a specified maximum. 
    It returns True if the maximum is met or exceeded. If the `start_time`
    keyword argument is omitted, it defaults to `None` and will be set to
    the current system time (in seconds). If the `max_time` keyword argument
    is omitted, it will default to `None` and will immediately terminate.
    The `max_time` argument can be specified in seconds as a floating-point
    number, as minutes/seconds as a two-element tuple of floating-point
    numbers, or as hours/minutes/seconds as a three-element tuple of 
    floating-point numbers.
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
    
    Optional keyword arguments in args:
    
    - *start_time* -- the time from which to start measuring (default None)
    - *max_time* -- the maximum time that should elapse (default None)
    
    """
    start_time = args.setdefault('start_time', None)
    max_time = args.setdefault('max_time', None)
    logging = args.get('_ec').logger

    if start_time is None:
        start_time = time.time()
        args['start_time'] = start_time
        logging.debug('time_termination terminator added without setting the start_time argument; setting start_time to current time')
    if max_time is None:
        logging.debug('time_termination terminator added without setting the max_time argument; terminator will immediately terminate')
    else:
        try:
            max_time = max_time[0] * 3600.0 + max_time[1] * 60.00 + max_time[2]
            args['max_time'] = max_time
        except TypeError:
            pass
        except IndexError:
            max_time = max_time[0] * 60 + max_time[1]
            args['max_time'] = max_time
    time_elapsed = time.time() - start_time
    return max_time is None or time_elapsed >= max_time


def user_termination(population, num_generations, num_evaluations, args):
    """Return True if user presses the ESC key when prompted.
    
    This function prompts the user to press the ESC key to terminate the 
    evolution. The prompt persists for a specified number of seconds before
    evolution continues. Additionally, the function can be customized to 
    allow any press of the ESC key to be stored until the next time this 
    function is called. 
    
    .. note::
    
       This function makes use of the ``msvcrt`` (Windows) and ``curses`` 
       (Unix) libraries. Other systems may not be supported.
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
    
    Optional keyword arguments in args:
    
    - *termination_response_timeout* -- the number of seconds to wait for 
      the user to press the ESC key (default 5)
    - *clear_termination_buffer* -- whether the keyboard buffer should be 
      cleared before allowing the user to press a key (default True)
    
    """
    def getch():
        unix = ('darwin', 'linux2')
        if sys.platform not in unix:
            try:
                import msvcrt
            except ImportError:
                return -1
            if msvcrt.kbhit():
                return msvcrt.getch()
            else:
                return -1
        elif sys.platform in unix:
            def _getch(stdscr):
                stdscr.nodelay(1)
                ch = stdscr.getch()
                stdscr.nodelay(0)
                return ch
            import curses
            return curses.wrapper(_getch)
    
    num_secs = args.get('termination_response_timeout', 5)
    clear_buffer = args.get('clear_termination_buffer', True)
    if clear_buffer:
        while getch() > -1:
            pass
    sys.stdout.write('Press ESC to terminate (%d secs):' % num_secs)
    count = 1
    start = time.time()
    while time.time() - start < num_secs:
        ch = getch()
        if ch > -1 and ord(ch) == 27:
            sys.stdout.write('\n\n')
            return True
        elif time.time() - start == count:
            sys.stdout.write('.')
            count += 1
    sys.stdout.write('\n')
    return False    

    
def no_improvement_termination(population, num_generations, num_evaluations, args):
    """Return True if the best fitness does not change for a number of generations.
    
    This function keeps track of the current best fitness and compares it to
    the best fitness in previous generations. Whenever those values are the 
    same, it begins a generation count. If that count exceeds a specified 
    number, the terminator returns True.
    
    .. Arguments:
       population -- the population of Individuals
       num_generations -- the number of elapsed generations
       num_evaluations -- the number of candidate solution evaluations
       args -- a dictionary of keyword arguments
    
    Optional keyword arguments in args:
    
    - *max_generations* -- the number of generations allowed for no change in fitness (default 10)
    
    """
    max_generations = args.setdefault('max_generations', 10)
    previous_best = args.setdefault('previous_best', None)
    current_best = max(population).fitness
    if previous_best is None or previous_best != current_best:
        args['previous_best'] = current_best
        args['generation_count'] = 0
        return False
    else:
        if args['generation_count'] >= max_generations:
            return True
        else:
            args['generation_count'] += 1
            return False
