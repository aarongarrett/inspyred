"""
    =================
    :mod:`crossovers`
    =================

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

    .. module:: crossovers
    .. moduleauthor:: Aaron Garrett <garrett@inspiredintelligence.io>
"""
import copy
import functools
import math
import pickle


def crossover(cross):
    """Return an inspyred crossover function based on the given function.

    This function generator takes a function that operates on only
    two parent candidates to produce an iterable sequence of offspring
    (typically two). The generator handles the pairing of selected
    parents and collecting of all offspring.

    The generated function chooses every odd candidate as a 'mom' and
    every even as a 'dad' (discounting the last candidate if there is
    an odd number). For each mom-dad pair, offspring are produced via
    the `cross` function.

    The given function ``cross`` must have the following signature::

        offspring = cross(random, mom, dad, args)

    This function is most commonly used as a function decorator with
    the following usage::

        @crossover
        def cross(random, mom, dad, args):
            # Implementation of paired crossing
            pass

    The generated function also contains an attribute named
    ``single_crossover`` which holds the original crossover function.
    In this way, the original single-set-of-parents function can be
    retrieved if necessary.

    """
    @functools.wraps(cross)
    def inspyred_crossover(random, candidates, args):
        if len(candidates) % 2 == 1:
            candidates = candidates[:-1]
        moms = candidates[::2]
        dads = candidates[1::2]
        children = []
        for i, (mom, dad) in enumerate(zip(moms, dads)):
            cross.index = i
            offspring = cross(random, mom, dad, args)
            for o in offspring:
                children.append(o)
        return children
    inspyred_crossover.single_crossover = cross
    return inspyred_crossover


@crossover
def n_point_crossover(random, mom, dad, args):
    """Return the offspring of n-point crossover on the candidates.

    This function performs n-point crossover (NPX). It selects *n*
    random points without replacement at which to 'cut' the candidate
    solutions and recombine them.

    .. Arguments:
       random -- the random number generator object
       mom -- the first parent candidate
       dad -- the second parent candidate
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:

    - *crossover_rate* -- the rate at which crossover is performed
      (default 1.0)
    - *num_crossover_points* -- the number of crossover points used (default 1)

    """
    crossover_rate = args.setdefault('crossover_rate', 1.0)
    num_crossover_points = args.setdefault('num_crossover_points', 1)
    children = []
    if random.random() < crossover_rate:
        num_cuts = min(len(mom)-1, num_crossover_points)
        cut_points = random.sample(list(range(1, len(mom))), num_cuts)
        cut_points.sort()
        bro = copy.copy(dad)
        sis = copy.copy(mom)
        normal = True
        for i, (m, d) in enumerate(zip(mom, dad)):
            if i in cut_points:
                normal = not normal
            if not normal:
                bro[i] = m
                sis[i] = d
                normal = not normal
        children.append(bro)
        children.append(sis)
    else:
        children.append(mom)
        children.append(dad)
    return children


@crossover
def uniform_crossover(random, mom, dad, args):
    """Return the offspring of uniform crossover on the candidates.

    This function performs uniform crossover (UX). For each element
    of the parents, a biased coin is flipped to determine whether
    the first offspring gets the 'mom' or the 'dad' element. An
    optional keyword argument in args, ``ux_bias``, determines the bias.

    .. Arguments:
       random -- the random number generator object
       mom -- the first parent candidate
       dad -- the second parent candidate
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:

    - *crossover_rate* -- the rate at which crossover is performed
      (default 1.0)
    - *ux_bias* -- the bias toward the first candidate in the crossover
      (default 0.5)

    """
    ux_bias = args.setdefault('ux_bias', 0.5)
    crossover_rate = args.setdefault('crossover_rate', 1.0)
    children = []
    if random.random() < crossover_rate:
        bro = copy.copy(dad)
        sis = copy.copy(mom)
        for i, (m, d) in enumerate(zip(mom, dad)):
            if random.random() < ux_bias:
                bro[i] = m
                sis[i] = d
        children.append(bro)
        children.append(sis)
    else:
        children.append(mom)
        children.append(dad)
    return children


@crossover
def partially_matched_crossover(random, mom, dad, args):
    """Return the offspring of partially matched crossover on the candidates.

    This function performs partially matched crossover (PMX). This type of
    crossover assumes that candidates are composed of discrete values that
    are permutations of a given set (typically integers). It produces offspring
    that are themselves permutations of the set.

    .. Arguments:
       random -- the random number generator object
       mom -- the first parent candidate
       dad -- the second parent candidate
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:

    - *crossover_rate* -- the rate at which crossover is performed
      (default 1.0)

    """
    crossover_rate = args.setdefault('crossover_rate', 1.0)
    if random.random() < crossover_rate:
        size = len(mom)
        points = random.sample(list(range(size)), 2)
        x, y = min(points), max(points)
        bro = copy.copy(dad)
        bro[x:y+1] = mom[x:y+1]
        sis = copy.copy(mom)
        sis[x:y+1] = dad[x:y+1]
        for parent, child in zip([dad, mom], [bro, sis]):
            for i in range(x, y+1):
                if parent[i] not in child[x:y+1]:
                    spot = i
                    while x <= spot <= y:
                        spot = parent.index(child[spot])
                    child[spot] = parent[i]
        return [bro, sis]
    else:
        return [mom, dad]


@crossover
def arithmetic_crossover(random, mom, dad, args):
    """Return the offspring of arithmetic crossover on the candidates.

    This function performs arithmetic crossover (AX), which is similar to a
    generalized weighted averaging of the candidate elements. The allele
    of each parent is weighted by the *ax_alpha* keyword argument, and
    the allele of the complement parent is weighted by 1 - *ax_alpha*.
    This averaging is only done on the alleles listed in the *ax_points*
    keyword argument. If this argument is ``None``, then all alleles
    are used. This means that if this function is used with all default
    values, then offspring are simple averages of their parents.
    This function also makes use of the bounder function as specified
    in the EC's ``evolve`` method.

    .. Arguments:
       random -- the random number generator object
       mom -- the first parent candidate
       dad -- the second parent candidate
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:

    - *crossover_rate* -- the rate at which crossover is performed
      (default 1.0)
    - *ax_alpha* -- the weight for the averaging (default 0.5)
    - *ax_points* -- a list of points specifying the alleles to
      recombine (default None)

    """
    ax_alpha = args.setdefault('ax_alpha', 0.5)
    ax_points = args.setdefault('ax_points', None)
    crossover_rate = args.setdefault('crossover_rate', 1.0)
    bounder = args['_ec'].bounder
    children = []
    if random.random() < crossover_rate:
        bro = copy.copy(dad)
        sis = copy.copy(mom)
        if ax_points is None:
            ax_points = list(range(min(len(bro), len(sis))))
        for i in ax_points:
            bro[i] = ax_alpha * mom[i] + (1 - ax_alpha) * dad[i]
            sis[i] = ax_alpha * dad[i] + (1 - ax_alpha) * mom[i]
        bro = bounder(bro, args)
        sis = bounder(sis, args)
        children.append(bro)
        children.append(sis)
    else:
        children.append(mom)
        children.append(dad)
    return children


@crossover
def blend_crossover(random, mom, dad, args):
    """Return the offspring of blend crossover on the candidates.

    This function performs blend crossover (BLX), which is similar to
    arithmetic crossover with a bit of mutation. It creates offspring
    whose values are chosen randomly from a range bounded by the
    parent alleles but that is also extended by some amount proportional
    to the *blx_alpha* keyword argument. It is this extension of the
    range that provides the additional exploration. This averaging is
    only done on the alleles listed in the *blx_points* keyword argument.
    If this argument is ``None``, then all alleles are used. This function
    also makes use of the bounder function as specified in the EC's
    ``evolve`` method.

    .. Arguments:
       random -- the random number generator object
       mom -- the first parent candidate
       dad -- the second parent candidate
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:

    - *crossover_rate* -- the rate at which crossover is performed
      (default 1.0)
    - *blx_alpha* -- the blending rate (default 0.1)
    - *blx_points* -- a list of points specifying the alleles to
      recombine (default None)

    """
    blx_alpha = args.setdefault('blx_alpha', 0.1)
    blx_points = args.setdefault('blx_points', None)
    crossover_rate = args.setdefault('crossover_rate', 1.0)
    bounder = args['_ec'].bounder
    children = []
    if random.random() < crossover_rate:
        bro = copy.copy(dad)
        sis = copy.copy(mom)
        if blx_points is None:
            blx_points = list(range(min(len(bro), len(sis))))
        for i in blx_points:
            smallest, largest = min(mom[i], dad[i]), max(mom[i], dad[i])
            delta = blx_alpha * (largest - smallest)
            bro[i] = smallest - delta + random.random() * (largest - smallest + 2 * delta)
            sis[i] = smallest - delta + random.random() * (largest - smallest + 2 * delta)
        bro = bounder(bro, args)
        sis = bounder(sis, args)
        children.append(bro)
        children.append(sis)
    else:
        children.append(mom)
        children.append(dad)
    return children


def heuristic_crossover(random, candidates, args):
    """Return the offspring of heuristic crossover on the candidates.

    It performs heuristic crossover (HX), which is similar to the
    update rule used in particle swarm optimization. This function
    also makes use of the bounder function as specified in the EC's
    ``evolve`` method.

    .. note::

       This function assumes that candidates can be pickled (for hashing
       as keys to a dictionary).

    .. Arguments:
       random -- the random number generator object
       candidates -- the candidate solutions
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:

    - *crossover_rate* -- the rate at which crossover is performed
      (default 1.0)

    """
    crossover_rate = args.setdefault('crossover_rate', 1.0)
    bounder = args['_ec'].bounder

    if len(candidates) % 2 == 1:
        candidates = candidates[:-1]

    # Since we don't have fitness information in the candidates, we need
    # to make a dictionary containing the candidate and its corresponding
    # individual in the population.
    population = list(args['_ec'].population)
    lookup = dict(list(zip([pickle.dumps(p.candidate, 1) for p in population], population)))

    moms = candidates[::2]
    dads = candidates[1::2]
    children = []
    for mom, dad in zip(moms, dads):
        if random.random() < crossover_rate:
            bro = copy.copy(dad)
            sis = copy.copy(mom)
            mom_is_better = lookup[pickle.dumps(mom, 1)] > lookup[pickle.dumps(dad, 1)]
            for i, (m, d) in enumerate(zip(mom, dad)):
                negpos = 1 if mom_is_better else -1
                val = d if mom_is_better else m
                bro[i] = val + random.random() * negpos * (m - d)
                sis[i] = val + random.random() * negpos * (m - d)
            bro = bounder(bro, args)
            sis = bounder(sis, args)
            children.append(bro)
            children.append(sis)
        else:
            children.append(mom)
            children.append(dad)
    return children


@crossover
def simulated_binary_crossover(random, mom, dad, args):
    """Return the offspring of simulated binary crossover on the candidates.

    This function performs simulated binary crossover (SBX), following the
    implementation in NSGA-II
    `(Deb et al., ICANNGA 1999) <http://vision.ucsd.edu/~sagarwal/icannga.pdf>`_.

    .. Arguments:
       random -- the random number generator object
       mom -- the first parent candidate
       dad -- the second parent candidate
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:

    - *crossover_rate* -- the rate at which crossover is performed
      (default 1.0)
    - *sbx_distribution_index* -- the non-negative distribution index
      (default 10)

    A small value of the `sbx_distribution_index` optional argument allows
    solutions far away from parents to be created as child solutions,
    while a large value restricts only near-parent solutions to be created as
    child solutions.

    """
    crossover_rate = args.setdefault('crossover_rate', 1.0)
    if random.random() < crossover_rate:
        di = args.setdefault('sbx_distribution_index', 10)
        bounder = args['_ec'].bounder
        bro = copy.copy(dad)
        sis = copy.copy(mom)
        for i, (m, d, lb, ub) in enumerate(zip(mom, dad, bounder.lower_bound, bounder.upper_bound)):
            try:
                if m > d:
                    m, d = d, m
                beta = 1.0 + 2 * min(m - lb, ub - d) / float(d - m)
                alpha = 2.0 - 1.0 / beta**(di + 1.0)
                u = random.random()
                if u <= (1.0 / alpha):
                    beta_q = (u * alpha)**(1.0 / float(di + 1.0))
                else:
                    beta_q = (1.0 / (2.0 - u * alpha))**(1.0 / float(di + 1.0))
                bro_val = 0.5 * ((m + d) - beta_q * (d - m))
                bro_val = max(min(bro_val, ub), lb)
                sis_val = 0.5 * ((m + d) + beta_q * (d - m))
                sis_val = max(min(sis_val, ub), lb)
                if random.random() > 0.5:
                    bro_val, sis_val = sis_val, bro_val
                bro[i] = bro_val
                sis[i] = sis_val
            except ZeroDivisionError:
                # The offspring already have legitimate values for every element,
                # so no need to take any special action here.
                pass
        return [bro, sis]
    else:
        return [mom, dad]


@crossover
def laplace_crossover(random, mom, dad, args):
    """Return the offspring of Laplace crossover on the candidates.

    This function performs Laplace crosssover (LX), following the
    implementation specified in (Deep and Thakur, "A new crossover
    operator for real coded genetic algorithms," Applied Mathematics
    and Computation, Volume 188, Issue 1, May 2007, pp. 895--911).
    This function also makes use of the bounder function as specified
    in the EC's ``evolve`` method.

    .. Arguments:
       random -- the random number generator object
       mom -- the first parent candidate
       dad -- the second parent candidate
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:

    - *crossover_rate* -- the rate at which crossover is performed
      (default 1.0)
    - *lx_location* -- the location parameter (default 0)
    - *lx_scale* -- the scale parameter (default 0.5)

    In some sense, the *lx_location* and *lx_scale* parameters can be thought
    of as analogs in a Laplace distribution to the mean and standard
    deviation of a Gaussian distribution. If *lx_scale* is near zero, offspring
    will be produced near the parents. If *lx_scale* is farther from zero,
    offspring will be produced far from the parents.

    """
    crossover_rate = args.setdefault('crossover_rate', 1.0)
    if random.random() < crossover_rate:
        bounder = args['_ec'].bounder
        a = args.setdefault('lx_location', 0)
        b = args.setdefault('lx_scale', 0.5)
        bro = copy.copy(dad)
        sis = copy.copy(mom)
        for i, (m, d) in enumerate(zip(mom, dad)):
            u = random.random()
            if random.random() <= 0.5:
                beta = a - b * math.log(u)
            else:
                beta = a + b * math.log(u)
            bro[i] = m + beta * abs(m - d)
            sis[i] = d + beta * abs(m - d)
        bro = bounder(bro, args)
        sis = bounder(sis, args)
        return [bro, sis]
    else:
        return [mom, dad]







