"""
    =====================================================
    :mod:`benchmarks` -- Benchmark optimization functions
    =====================================================

    This module provides a set of benchmark problems for global optimization.

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

    .. module:: benchmarks
    .. moduleauthor:: Aaron Garrett <garrett@inspiredintelligence.io>
"""
import warnings
import copy
from inspyred import ec
from inspyred.ec import emo
from inspyred.ec import selectors
from inspyred import swarm
import itertools
import math
import random
from functools import reduce


class Benchmark(object):
    """Defines a global optimization benchmark problem.

    This abstract class defines the basic structure of a global
    optimization problem. Subclasses should implement the ``generator``
    and ``evaluator`` methods for a particular optimization problem,
    which can be used with inspyred's evolutionary computations.

    In addition to being used with evolutionary computations, subclasses
    of this class are also callable. The arguments passed to such a call
    are combined into a list and passed as the single candidate to the
    evaluator method. The single calculated fitness is returned. What
    this means is that a given benchmark can act as a mathematical function
    that takes arguments and returns the value of the function, like the
    following example.::

        my_function = benchmarks.Ackley(2)
        output = my_function(-1.5, 4.2)

    Public Attributes:

    - *dimensions* -- the number of inputs to the problem
    - *objectives* -- the number of outputs of the problem (default 1)
    - *bounder* -- the bounding function for the problem (default None)
    - *maximize* -- whether the problem is one of maximization (default
      True)

    """
    def __init__(self, dimensions, objectives=1):
        self.dimensions = dimensions
        self.objectives = objectives
        self.bounder = None
        self.maximize = True

    def __str__(self):
        if self.objectives > 1:
            return '{0} ({1} dimensions, {2} objectives)'.format(self.__class__.__name__, self.dimensions, self.objectives)
        else:
            return '{0} ({1} dimensions)'.format(self.__class__.__name__, self.dimensions)

    def __repr__(self):
        return self.__class__.__name__

    def generator(self, random, args):
        """The generator function for the benchmark problem."""
        raise NotImplementedError

    def evaluator(self, candidates, args):
        """The evaluator function for the benchmark problem."""
        raise NotImplementedError

    def __call__(self, *args, **kwargs):
        candidate = [a for a in args]
        fit = self.evaluator([candidate], kwargs)
        return fit[0]

class Binary(Benchmark):
    """Defines a binary problem based on an existing benchmark problem.

    This class can be used to modify an existing benchmark problem to
    allow it to use a binary representation. The generator creates
    a list of binary values of size `dimensions`-by-`dimension_bits`.
    The evaluator accepts a candidate represented by such a binary list
    and transforms that candidate into a real-valued list as follows:

    1. Each set of `dimension_bits` bits is converted to its positive
       integer representation.
    2. Next, that integer value is divided by the maximum integer that
       can be represented by `dimension_bits` bits to produce a real
       number in the range [0, 1].
    3. That real number is then scaled to the range [lower_bound,
       upper_bound] for that dimension (which should be defined by
       the bounder).

    Public Attributes:

    - *benchmark* -- the original benchmark problem
    - *dimension_bits* -- the number of bits to use to represent each dimension
    - *bounder* -- a bounder that restricts elements of candidate solutions to
      the range [0, 1]
    - *maximize* -- whether the underlying benchmark problem is one of maximization

    """
    def __init__(self, benchmark, dimension_bits):
        Benchmark.__init__(self, benchmark.dimensions, benchmark.objectives)
        self.benchmark = benchmark
        self.dimension_bits = dimension_bits
        self.bounder = ec.DiscreteBounder([0, 1])
        self.maximize = self.benchmark.maximize
        self.__class__.__name__ = self.__class__.__name__ + ' ' + self.benchmark.__class__.__name__

    def _binary_to_real(self, binary):
        real = []
        for d, lo, hi in zip(list(range(self.dimensions)), self.benchmark.bounder.lower_bound, self.benchmark.bounder.upper_bound):
            b = binary[d*self.dimension_bits:(d+1)*self.dimension_bits]
            real_val = float(int(''.join([str(i) for i in b]), 2))
            value = real_val / (2**(self.dimension_bits)-1) * (hi - lo) + lo
            real.append(value)
        return real

    def generator(self, random, args):
        return [random.choice([0, 1]) for _ in range(self.dimensions * self.dimension_bits)]

    def evaluator(self, candidates, args):
        real_candidates = []
        for c in candidates:
            real_candidates.append(self._binary_to_real(c))
        return self.benchmark.evaluator(real_candidates, args)



#-----------------------------------------------------------------------
#                     SINGLE-OBJECTIVE PROBLEMS
#-----------------------------------------------------------------------

class Ackley(Benchmark):
    """Defines the Ackley benchmark problem.

    This class defines the Ackley global optimization problem. This
    is a multimodal minimization problem defined as follows:

    .. math::

        f(x) = -20e^{-0.2\\sqrt{\\frac{1}{n} \\sum_{i=1}^n x_i^2}} - e^{\\frac{1}{n} \\sum_{i=1}^n \\cos(2 \\pi x_i)} + 20 + e

    Here, :math:`n` represents the number of dimensions and :math:`x_i \\in [-32, 32]` for :math:`i=1,...,n`.

    .. figure:: _static/image6011.jpg
        :alt: Ackley function
        :align: center

        Two-dimensional Ackley function
        (`image source <http://www-optima.amp.i.kyoto-u.ac.jp/member/student/hedar/Hedar_files/TestGO_files/Page295.htm>`__)

    Public Attributes:

    - *global_optimum* -- the problem input that produces the optimum output.
      Here, this corresponds to [0, 0, ..., 0].

    """
    def __init__(self, dimensions=2):
        Benchmark.__init__(self, dimensions)
        self.bounder = ec.Bounder([-32.0] * self.dimensions, [32.0] * self.dimensions)
        self.maximize = False
        self.global_optimum = [0 for _ in range(self.dimensions)]

    def generator(self, random, args):
        return [random.uniform(-32.0, 32.0) for _ in range(self.dimensions)]

    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            fitness.append(-20 * math.exp(-0.2 * math.sqrt(1.0 / self.dimensions * sum([x**2 for x in c]))) -
                           math.exp(1.0 / self.dimensions * sum([math.cos(2 * math.pi * x) for x in c])) + 20 + math.e)
        return fitness

class Griewank(Benchmark):
    """Defines the Griewank benchmark problem.

    This class defines the Griewank global optimization problem. This
    is a highly multimodal minimization problem with numerous, wide-spread,
    regularly distributed local minima. It is defined as follows:

    .. math::

        f(x) = \\frac{1}{4000} \\sum_{i=1}^n x_i^2 - \\prod_{i=1}^n \\cos(\\frac{x_i}{\\sqrt{i}}) + 1

    Here, :math:`n` represents the number of dimensions and :math:`x_i \\in [-600, 600]` for :math:`i=1,...,n`.

    .. figure:: _static/image8891.jpg
        :alt: Griewank function
        :align: center

        Two-dimensional Griewank function
        (`image source <http://www-optima.amp.i.kyoto-u.ac.jp/member/student/hedar/Hedar_files/TestGO_files/Page1905.htm>`__)

    Public Attributes:

    - *global_optimum* -- the problem input that produces the optimum output.
      Here, this corresponds to [0, 0, ..., 0].

    """
    def __init__(self, dimensions=2):
        Benchmark.__init__(self, dimensions)
        self.bounder = ec.Bounder([-600.0] * self.dimensions, [600.0] * self.dimensions)
        self.maximize = False
        self.global_optimum = [0 for _ in range(self.dimensions)]

    def generator(self, random, args):
        return [random.uniform(-600.0, 600.0) for _ in range(self.dimensions)]

    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            prod = 1
            for i, x in enumerate(c):
                prod *= math.cos(x / math.sqrt(i+1))
            fitness.append(1.0 / 4000.0 * sum([x**2 for x in c]) - prod + 1)
        return fitness

class Rastrigin(Benchmark):
    """Defines the Rastrigin benchmark problem.

    This class defines the Rastrigin global optimization problem. This
    is a highly multimodal minimization problem where the local minima
    are regularly distributed. It is defined as follows:

    .. math::

        f(x) = \\sum_{i=1}^n (x_i^2 - 10\\cos(2\\pi x_i) + 10)

    Here, :math:`n` represents the number of dimensions and :math:`x_i \\in [-5.12, 5.12]` for :math:`i=1,...,n`.

    .. figure:: _static/image12271.jpg
        :alt: Rastrigin function
        :align: center

        Two-dimensional Rastrigin function
        (`image source <http://www-optima.amp.i.kyoto-u.ac.jp/member/student/hedar/Hedar_files/TestGO_files/Page2607.htm>`__)

    Public Attributes:

    - *global_optimum* -- the problem input that produces the optimum output.
      Here, this corresponds to [0, 0, ..., 0].

    """
    def __init__(self, dimensions=2):
        Benchmark.__init__(self, dimensions)
        self.bounder = ec.Bounder([-5.12] * self.dimensions, [5.12] * self.dimensions)
        self.maximize = False
        self.global_optimum = [0 for _ in range(self.dimensions)]

    def generator(self, random, args):
        return [random.uniform(-5.12, 5.12) for _ in range(self.dimensions)]

    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            fitness.append(sum([x**2 - 10 * math.cos(2 * math.pi * x) + 10 for x in c]))
        return fitness

class Rosenbrock(Benchmark):
    """Defines the Rosenbrock benchmark problem.

    This class defines the Rosenbrock global optimization problem,
    also known as the "banana function." The global optimum sits
    within a narrow, parabolic-shaped flattened valley. It is
    defined as follows:

    .. math::

        f(x) = \\sum_{i=1}^{n-1} [100(x_i^2 - x_{i+1})^2 + (x_i - 1)^2]

    Here, :math:`n` represents the number of dimensions and :math:`x_i \\in [-5, 10]` for :math:`i=1,...,n`.

    .. figure:: _static/image12371.jpg
        :alt: Rosenbrock function
        :align: center

        Two-dimensional Rosenbrock function
        (`image source <http://www-optima.amp.i.kyoto-u.ac.jp/member/student/hedar/Hedar_files/TestGO_files/Page2537.htm>`__)

    Public Attributes:

    - *global_optimum* -- the problem input that produces the optimum output.
      Here, this corresponds to [1, 1, ..., 1].

    """
    def __init__(self, dimensions=2):
        Benchmark.__init__(self, dimensions)
        self.bounder = ec.Bounder([-5.0] * self.dimensions, [10.0] * self.dimensions)
        self.maximize = False
        self.global_optimum = [1 for _ in range(self.dimensions)]

    def generator(self, random, args):
        return [random.uniform(-5.0, 10.0) for _ in range(self.dimensions)]

    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            total = 0
            for i in range(len(c) - 1):
                total += 100 * (c[i]**2 - c[i+1])**2 + (c[i] - 1)**2
            fitness.append(total)
        return fitness

class Schwefel(Benchmark):
    """Defines the Schwefel benchmark problem.

    This class defines the Schwefel global optimization problem.
    It is defined as follows:

    .. math::

        f(x) = 418.9829n - \\sum_{i=1}^n \\left[-x_i \\sin(\\sqrt{|x_i|})\\right]

    Here, :math:`n` represents the number of dimensions and :math:`x_i \\in [-500, 500]` for :math:`i=1,...,n`.

    .. figure:: _static/image12721.jpg
        :alt: Schwefel function
        :align: center

        Two-dimensional Schwefel function
        (`image source <http://www-optima.amp.i.kyoto-u.ac.jp/member/student/hedar/Hedar_files/TestGO_files/Page2530.htm>`__)

    Public Attributes:

    - *global_optimum* -- the problem input that produces the optimum output.
      Here, this corresponds to [420.9687, 420.9687, ..., 420.9687].

    """
    def __init__(self, dimensions=2):
        Benchmark.__init__(self, dimensions)
        self.bounder = ec.Bounder([-500.0] * self.dimensions, [500.0] * self.dimensions)
        self.maximize = False
        self.global_optimum = [420.9687 for _ in range(self.dimensions)]

    def generator(self, random, args):
        return [random.uniform(-500.0, 500.0) for _ in range(self.dimensions)]

    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            fitness.append(418.9829 * self.dimensions - sum([x * math.sin(math.sqrt(abs(x))) for x in c]))
        return fitness

class Sphere(Benchmark):
    """Defines the Sphere benchmark problem.

    This class defines the Sphere global optimization problem, also called
    the "first function of De Jong's" or "De Jong's F1." It is continuous,
    convex, and unimodal, and it is defined as follows:

    .. math::

        f(x) = \\sum_{i=1}^n x_i^2

    Here, :math:`n` represents the number of dimensions and :math:`x_i \\in [-5.12, 5.12]` for :math:`i=1,...,n`.

    .. figure:: _static/image11981.jpg
        :alt: Sphere function
        :align: center

        Two-dimensional Sphere function
        (`image source <http://www-optima.amp.i.kyoto-u.ac.jp/member/student/hedar/Hedar_files/TestGO_files/Page1113.htm>`__)

    Public Attributes:

    - *global_optimum* -- the problem input that produces the optimum output.
      Here, this corresponds to [0, 0, ..., 0].

    """
    def __init__(self, dimensions=2):
        Benchmark.__init__(self, dimensions)
        self.bounder = ec.Bounder([-5.12] * self.dimensions, [5.12] * self.dimensions)
        self.maximize = False
        self.global_optimum = [0 for _ in range(self.dimensions)]

    def generator(self, random, args):
        return [random.uniform(-5.12, 5.12) for _ in range(self.dimensions)]

    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            fitness.append(sum([x**2 for x in c]))
        return fitness


#-----------------------------------------------------------------------
#                      MULTI-OBJECTIVE PROBLEMS
#-----------------------------------------------------------------------

class Kursawe(Benchmark):
    """Defines the Kursawe multiobjective benchmark problem.

    This class defines the Kursawe multiobjective minimization problem.
    This function accepts an n-dimensional input and produces a
    two-dimensional output. It is defined as follows:

    .. math::

        f_1(x) &= \\sum_{i=1}^{n-1} \\left[-10e^{-0.2\\sqrt{x_i^2 + x_{i+1}^2}}\\right] \\\\
        f_2(x) &= \\sum_{i=1}^n \\left[|x_i|^{0.8} + 5\\sin(x_i)^3\\right] \\\\

    Here, :math:`n` represents the number of dimensions and :math:`x_i \\in [-5, 5]` for :math:`i=1,...,n`.

    .. figure:: _static/kursawefun.jpg
        :alt: Kursawe Pareto front
        :width: 700 px
        :align: center

        Three-dimensional Kursawe Pareto front
        (`image source <http://delta.cs.cinvestav.mx/~ccoello/EMOO/testfuncs/>`__)

    """
    def __init__(self, dimensions=2):
        Benchmark.__init__(self, dimensions, 2)
        self.bounder = ec.Bounder([-5.0] * self.dimensions, [5.0] * self.dimensions)
        self.maximize = False

    def generator(self, random, args):
        return [random.uniform(-5.0, 5.0) for _ in range(self.dimensions)]

    def evaluator(self, candidates, args):
        fitness = []
        for c in candidates:
            f1 = sum([-10 * math.exp(-0.2 * math.sqrt(c[i]**2 + c[i+1]**2)) for i in range(len(c) - 1)])
            f2 = sum([math.pow(abs(x), 0.8) + 5 * math.sin(x**3) for x in c])
            fitness.append(emo.Pareto([f1, f2]))
        return fitness

class DTLZ1(Benchmark):
    """Defines the DTLZ1 multiobjective benchmark problem.

    This class defines the DTLZ1 multiobjective minimization problem
    taken from `(Deb et al., "Scalable Multi-Objective Optimization Test Problems."
    CEC 2002, pp. 825--830) <http://www.tik.ee.ethz.ch/sop/download/supplementary/testproblems/dtlz1/index.php>`__.
    This function accepts an n-dimensional input and produces an m-dimensional output.
    It is defined as follows:

    .. math::

        f_1(\\vec{x}) &= \\frac{1}{2} x_1 \\dots x_{m-1}(1 + g(\\vec{x_m})) \\\\
        f_i(\\vec{x}) &= \\frac{1}{2} x_1 \\dots x_{m-i}(1 + g(\\vec{x_m})) \\\\
        f_m(\\vec{x}) &= \\frac{1}{2} (1 - x_1)(1 + g(\\vec{x_m})) \\\\
        g(\\vec{x_m}) &= 100\\left[|\\vec{x_m}| + \\sum_{x_i \\in \\vec{x_m}}\\left((x_i - 0.5)^2 - \\cos(20\\pi(x_i - 0.5))\\right)\\right] \\\\

    Here, :math:`n` represents the number of dimensions, :math:`m` represents the
    number of objectives, :math:`x_i \\in [0, 1]` for :math:`i=1,...,n`, and
    :math:`\\vec{x_m} = x_m x_{m+1} \\dots x_{n}.`

    The recommendation given in the paper mentioned above is to provide 4 more
    dimensions than objectives. For instance, if we want to use 2 objectives, we
    should use 6 dimensions.

    .. figure:: _static/dtlz1funb.jpg
        :alt: DTLZ1 Pareto front
        :width: 700 px
        :align: center

        Three-dimensional DTLZ1 Pareto front
        (`image source <http://delta.cs.cinvestav.mx/~ccoello/EMOO/testfuncs/>`__)

    """
    def __init__(self, dimensions=2, objectives=2):
        Benchmark.__init__(self, dimensions, objectives)
        if dimensions < objectives:
            raise ValueError('dimensions ({0}) must be greater than or equal to objectives ({1})'.format(dimensions, objectives))
        self.bounder = ec.Bounder([0.0] * self.dimensions, [1.0] * self.dimensions)
        self.maximize = False

    def global_optimum(self):
        """Return a globally optimal solution to this problem.

        This function returns a globally optimal solution (i.e., a
        solution that lives on the Pareto front). Since there are many
        solutions that are Pareto-optimal, this function randomly
        chooses one to return.

        """
        x = [random.uniform(0, 1) for _ in range(self.objectives - 1)]
        x.extend([0 for _ in range(self.dimensions - self.objectives + 1)])
        return x

    def generator(self, random, args):
        return [random.uniform(0.0, 1.0) for _ in range(self.dimensions)]

    def evaluator(self, candidates, args):
        fitness = []
        g = lambda x: 100 * (len(x) + sum([(a - 0.5)**2 - math.cos(20 * math.pi * (a - 0.5)) for a in x]))
        for c in candidates:
            gval = g(c[self.objectives-1:])
            fit = [0.5 * reduce(lambda x,y: x*y, c[:self.objectives-1]) * (1 + gval)]
            for m in reversed(list(range(1, self.objectives))):
                fit.append(0.5 * reduce(lambda x,y: x*y, c[:m-1], 1) * (1 - c[m-1]) * (1 + gval))
            fitness.append(emo.Pareto(fit))
        return fitness

class DTLZ2(Benchmark):
    """Defines the DTLZ2 multiobjective benchmark problem.

    This class defines the DTLZ2 multiobjective minimization problem
    taken from `(Deb et al., "Scalable Multi-Objective Optimization Test Problems."
    CEC 2002, pp. 825--830) <http://www.tik.ee.ethz.ch/sop/download/supplementary/testproblems/dtlz1/index.php>`__.
    This function accepts an n-dimensional input and produces an m-dimensional output.
    It is defined as follows:

    .. math::

        f_1(\\vec{x}) &= (1 + g(\\vec{x_m}))\\cos(x_1 \\pi/2)\\cos(x_2 \\pi/2)\\dots\\cos(x_{m-2} \\pi/2)\\cos(x_{m-1} \\pi/2) \\\\
        f_i(\\vec{x}) &= (1 + g(\\vec{x_m}))\\cos(x_1 \\pi/2)\\cos(x_2 \\pi/2)\\dots\\cos(x_{m-i} \\pi/2)\\sin(x_{m-i+1} \\pi/2) \\\\
        f_m(\\vec{x}) &= (1 + g(\\vec{x_m}))\\sin(x_1 \\pi/2) \\\\
        g(\\vec{x_m}) &= \\sum_{x_i \\in \\vec{x_m}}(x_i - 0.5)^2 \\\\

    Here, :math:`n` represents the number of dimensions, :math:`m` represents the
    number of objectives, :math:`x_i \\in [0, 1]` for :math:`i=1,...,n`, and
    :math:`\\vec{x_m} = x_m x_{m+1} \\dots x_{n}.`

    The recommendation given in the paper mentioned above is to provide 9 more
    dimensions than objectives. For instance, if we want to use 2 objectives, we
    should use 11 dimensions.

    """
    def __init__(self, dimensions=2, objectives=2):
        Benchmark.__init__(self, dimensions, objectives)
        if dimensions < objectives:
            raise ValueError('dimensions ({0}) must be greater than or equal to objectives ({1})'.format(dimensions, objectives))
        self.bounder = ec.Bounder([0.0] * self.dimensions, [1.0] * self.dimensions)
        self.maximize = False

    def global_optimum(self):
        """Return a globally optimal solution to this problem.

        This function returns a globally optimal solution (i.e., a
        solution that lives on the Pareto front). Since there are many
        solutions that are Pareto-optimal, this function randomly
        chooses one to return.

        """
        x = [random.uniform(0, 1) for _ in range(self.objectives - 1)]
        x.extend([0.5 for _ in range(self.dimensions - self.objectives + 1)])
        return x

    def generator(self, random, args):
        return [random.uniform(0.0, 1.0) for _ in range(self.dimensions)]

    def evaluator(self, candidates, args):
        fitness = []
        g = lambda x: sum([(a - 0.5)**2 for a in x])
        for c in candidates:
            gval = g(c[self.objectives-1:])
            fit = [(1 + gval) *
                   reduce(lambda x,y: x*y, [math.cos(a * math.pi / 2.0) for a in c[:self.objectives-1]])]
            for m in reversed(list(range(1, self.objectives))):
                fit.append((1 + gval) *
                           reduce(lambda x,y: x*y, [math.cos(a * math.pi / 2.0) for a in c[:m-1]], 1) *
                           math.sin(c[m-1] * math.pi / 2.0))
            fitness.append(emo.Pareto(fit))
        return fitness

class DTLZ3(Benchmark):
    """Defines the DTLZ3 multiobjective benchmark problem.

    This class defines the DTLZ3 multiobjective minimization problem
    taken from `(Deb et al., "Scalable Multi-Objective Optimization Test Problems."
    CEC 2002, pp. 825--830) <http://www.tik.ee.ethz.ch/sop/download/supplementary/testproblems/dtlz1/index.php>`__.
    This function accepts an n-dimensional input and produces an m-dimensional output.
    It is defined as follows:

    .. math::

        f_1(\\vec{x}) &= (1 + g(\\vec{x_m}))\\cos(x_1 \\pi/2)\\cos(x_2 \\pi/2)\\dots\\cos(x_{m-2} \\pi/2)\\cos(x_{m-1} \\pi/2) \\\\
        f_i(\\vec{x}) &= (1 + g(\\vec{x_m}))\\cos(x_1 \\pi/2)\\cos(x_2 \\pi/2)\\dots\\cos(x_{m-i} \\pi/2)\\sin(x_{m-i+1} \\pi/2) \\\\
        f_m(\\vec{x}) &= (1 + g(\\vec{x_m}))\\sin(x_1 \\pi/2) \\\\
        g(\\vec{x_m}) &= 100\\left[|\\vec{x_m}| + \\sum_{x_i \\in \\vec{x_m}}\\left((x_i - 0.5)^2 - \\cos(20\\pi(x_i - 0.5))\\right)\\right] \\\\

    Here, :math:`n` represents the number of dimensions, :math:`m` represents the
    number of objectives, :math:`x_i \\in [0, 1]` for :math:`i=1,...,n`, and
    :math:`\\vec{x_m} = x_m x_{m+1} \\dots x_{n}.`

    The recommendation given in the paper mentioned above is to provide 9 more
    dimensions than objectives. For instance, if we want to use 2 objectives, we
    should use 11 dimensions.

    """
    def __init__(self, dimensions=2, objectives=2):
        Benchmark.__init__(self, dimensions, objectives)
        if dimensions < objectives:
            raise ValueError('dimensions ({0}) must be greater than or equal to objectives ({1})'.format(dimensions, objectives))
        self.bounder = ec.Bounder([0.0] * self.dimensions, [1.0] * self.dimensions)
        self.maximize = False

    def global_optimum(self):
        """Return a globally optimal solution to this problem.

        This function returns a globally optimal solution (i.e., a
        solution that lives on the Pareto front). Since there are many
        solutions that are Pareto-optimal, this function randomly
        chooses one to return.

        """
        x = [random.uniform(0, 1) for _ in range(self.objectives - 1)]
        x.extend([0.5 for _ in range(self.dimensions - self.objectives + 1)])
        return x

    def generator(self, random, args):
        return [random.uniform(0.0, 1.0) for _ in range(self.dimensions)]

    def evaluator(self, candidates, args):
        fitness = []
        g = lambda x: 100 * (len(x) + sum([(a - 0.5)**2 - math.cos(20 * math.pi * (a - 0.5)) for a in x]))
        for c in candidates:
            gval = g(c[self.objectives-1:])
            fit = [(1 + gval) * reduce(lambda x,y: x*y, [math.cos(a * math.pi / 2.0) for a in c[:self.objectives-1]])]
            for m in reversed(list(range(1, self.objectives))):
                fit.append((1 + gval) *
                           reduce(lambda x,y: x*y, [math.cos(a * math.pi / 2.0) for a in c[:m-1]], 1) *
                           math.sin(c[m-1] * math.pi / 2.0))
            fitness.append(emo.Pareto(fit))
        return fitness

class DTLZ4(Benchmark):
    """Defines the DTLZ4 multiobjective benchmark problem.

    This class defines the DTLZ4 multiobjective minimization problem
    taken from `(Deb et al., "Scalable Multi-Objective Optimization Test Problems."
    CEC 2002, pp. 825--830) <http://www.tik.ee.ethz.ch/sop/download/supplementary/testproblems/dtlz1/index.php>`__.
    This function accepts an n-dimensional input and produces an m-dimensional output.
    It is defined as follows:

    .. math::

        f_1(\\vec{x}) &= (1 + g(\\vec{x_m}))\\cos(x_1^\\alpha \\pi/2)\\cos(x_2^\\alpha \\pi/2)\\dots\\cos(x_{m-2}^\\alpha \\pi/2)\\cos(x_{m-1}^\\alpha \\pi/2) \\\\
        f_i(\\vec{x}) &= (1 + g(\\vec{x_m}))\\cos(x_1^\\alpha \\pi/2)\\cos(x_2^\\alpha \\pi/2)\\dots\\cos(x_{m-i}^\\alpha \\pi/2)\\sin(x_{m-i+1}^\\alpha \\pi/2) \\\\
        f_m(\\vec{x}) &= (1 + g(\\vec{x_m}))\\sin(x_1^\\alpha \\pi/2) \\\\
        g(\\vec{x_m}) &= \\sum_{x_i \\in \\vec{x_m}}(x_i - 0.5)^2 \\\\

    Here, :math:`n` represents the number of dimensions, :math:`m` represents the
    number of objectives, :math:`x_i \\in [0, 1]` for :math:`i=1,...,n`,
    :math:`\\vec{x_m} = x_m x_{m+1} \\dots x_{n},` and :math:`\\alpha=100.`

    The recommendation given in the paper mentioned above is to provide 9 more
    dimensions than objectives. For instance, if we want to use 2 objectives, we
    should use 11 dimensions.

    """
    def __init__(self, dimensions=2, objectives=2, alpha=100):
        Benchmark.__init__(self, dimensions, objectives)
        if dimensions < objectives:
            raise ValueError('dimensions ({0}) must be greater than or equal to objectives ({1})'.format(dimensions, objectives))
        self.bounder = ec.Bounder([0.0] * self.dimensions, [1.0] * self.dimensions)
        self.maximize = False
        self.alpha = alpha

    def global_optimum(self):
        """Return a globally optimal solution to this problem.

        This function returns a globally optimal solution (i.e., a
        solution that lives on the Pareto front). Since there are many
        solutions that are Pareto-optimal, this function randomly
        chooses one to return.

        """
        x = [random.uniform(0, 1) for _ in range(self.objectives - 1)]
        x.extend([0.5 for _ in range(self.dimensions - self.objectives + 1)])
        return x

    def generator(self, random, args):
        return [random.uniform(0.0, 1.0) for _ in range(self.dimensions)]

    def evaluator(self, candidates, args):
        fitness = []
        g = lambda x: sum([(a - 0.5)**2 for a in x])
        for c in candidates:
            gval = g(c[self.objectives-1:])
            fit = [(1 + gval) *
                   reduce(lambda x,y: x*y, [math.cos(a**self.alpha * math.pi / 2.0) for a in c[:self.objectives-1]])]
            for m in reversed(list(range(1, self.objectives))):
                fit.append((1 + gval) *
                           reduce(lambda x,y: x*y, [math.cos(a**self.alpha * math.pi / 2.0) for a in c[:m-1]], 1) *
                           math.sin(c[m-1]**self.alpha * math.pi / 2.0))
            fitness.append(emo.Pareto(fit))
        return fitness

class DTLZ5(Benchmark):
    """Defines the DTLZ5 multiobjective benchmark problem.

    .. warning::

        For 4 or more objectives the Global Optimum Pareto set is not fully
        defined by the global_optimum function.
        Huband, Simon, et al.
        "A review of multiobjective test problems and a scalable test problem toolkit."
        Evolutionary Computation, IEEE Transactions on 10.5 (2006): 477-506.


    This class defines the DTLZ5 multiobjective minimization problem
    taken from `(Deb et al., "Scalable Multi-Objective Optimization Test Problems."
    CEC 2002, pp. 825--830) <http://www.tik.ee.ethz.ch/sop/download/supplementary/testproblems/dtlz1/index.php>`__.
    This function accepts an n-dimensional input and produces an m-dimensional output.
    It is defined as follows:

    .. math::

        f_1(\\vec{x}) &= (1 + g(\\vec{x_m}))\\cos(\\theta_1 \\pi/2)\\cos(\\theta_2 \\pi/2)\\dots\\cos(\\theta_{m-2} \\pi/2)\\cos(\\theta_{m-1} \\pi/2) \\\\
        f_i(\\vec{x}) &= (1 + g(\\vec{x_m}))\\cos(\\theta_1 \\pi/2)\\cos(\\theta_2 \\pi/2)\\dots\\cos(\\theta_{m-i} \\pi/2)\\sin(\\theta_{m-i+1} \\pi/2) \\\\
        f_m(\\vec{x}) &= (1 + g(\\vec{x_m}))\\sin(\\theta_1 \\pi/2) \\\\
        \\theta_i     &= \\frac{\\pi}{4(1+g(\\vec{x_m}))}(1 + 2g(\\vec{x_m}) x_i) \\\\
        g(\\vec{x_m}) &= \\sum_{x_i \\in \\vec{x_m}}(x_i - 0.5)^2 \\\\

    Here, :math:`n` represents the number of dimensions, :math:`m` represents the
    number of objectives, :math:`x_i \\in [0, 1]` for :math:`i=1,...,n`, and
    :math:`\\vec{x_m} = x_m x_{m+1} \\dots x_{n}.`

    The recommendation given in the paper mentioned above is to provide 9 more
    dimensions than objectives. For instance, if we want to use 2 objectives, we
    should use 11 dimensions.

    """
    def __init__(self, dimensions=2, objectives=2):
        Benchmark.__init__(self, dimensions, objectives)
        if dimensions < objectives:
            raise ValueError('dimensions ({0}) must be greater than or equal to objectives ({1})'.format(dimensions, objectives))
        self.bounder = ec.Bounder([0.0] * self.dimensions, [1.0] * self.dimensions)
        self.maximize = False

    def global_optimum(self):
        """Return a globally optimal solution to this problem.

        This function returns a globally optimal solution (i.e., a
        solution that lives on the Pareto front). Since there are many
        solutions that are Pareto-optimal, this function randomly
        chooses one to return.

        .. warning::

            For 4 or more objectives the Global Optimum Pareto set is not fully
            defined by the this function.
            Huband, Simon, et al.
            "A review of multiobjective test problems and a scalable test problem toolkit."
            Evolutionary Computation, IEEE Transactions on 10.5 (2006): 477-506.

        """
        if self.objectives >= 4:
            warnings.warn(
                "Warning the DTLZ5 globally optimal pareto set is not fully defined for 4 or more objectives")

        x = [random.uniform(0, 1) for _ in range(self.objectives - 1)]
        x.extend([0.5 for _ in range(self.dimensions - self.objectives + 1)])
        return x

    def generator(self, random, args):
        return [random.uniform(0.0, 1.0) for _ in range(self.dimensions)]

    def evaluator(self, candidates, args):
        fitness = []
        g = lambda x: sum([(a - 0.5)**2 for a in x])
        for c in candidates:
            gval = g(c[self.objectives-1:])
            theta = lambda x: math.pi / (4.0 * (1 + gval)) * (1 + 2 * gval * x)
            fit = [(1 + gval) * math.cos(math.pi / 2.0 * c[0]) *
                   reduce(lambda x,y: x*y, [math.cos(theta(a)) for a in c[1:self.objectives-1]])]
            for m in reversed(list(range(1, self.objectives))):
                if m == 1:
                    fit.append((1 + gval) * math.sin(math.pi / 2.0 * c[0]))
                else:
                    fit.append((1 + gval) * math.cos(math.pi / 2.0 * c[0]) *
                               reduce(lambda x,y: x*y, [math.cos(theta(a)) for a in c[1:m-1]], 1) *
                               math.sin(theta(c[m-1])))
            fitness.append(emo.Pareto(fit))
        return fitness

class DTLZ6(Benchmark):
    """Defines the DTLZ6 multiobjective benchmark problem.

    This class defines the DTLZ6 multiobjective minimization problem
    taken from `(Deb et al., "Scalable Multi-Objective Optimization Test Problems."
    CEC 2002, pp. 825--830) <http://www.tik.ee.ethz.ch/sop/download/supplementary/testproblems/dtlz1/index.php>`__.
    This function accepts an n-dimensional input and produces an m-dimensional output.
    It is defined as follows:

    .. math::

        f_1(\\vec{x}) &= (1 + g(\\vec{x_m}))\\cos(\\theta_1 \\pi/2)\\cos(\\theta_2 \\pi/2)\\dots\\cos(\\theta_{m-2} \\pi/2)\\cos(\\theta_{m-1} \\pi/2) \\\\
        f_i(\\vec{x}) &= (1 + g(\\vec{x_m}))\\cos(\\theta_1 \\pi/2)\\cos(\\theta_2 \\pi/2)\\dots\\cos(\\theta_{m-i} \\pi/2)\\sin(\\theta_{m-i+1} \\pi/2) \\\\
        f_m(\\vec{x}) &= (1 + g(\\vec{x_m}))\\sin(\\theta_1 \\pi/2) \\\\
        \\theta_i     &= \\frac{\\pi}{4(1+g(\\vec{x_m}))}(1 + 2g(\\vec{x_m}) x_i) \\\\
        g(\\vec{x_m}) &= \\sum_{x_i \\in \\vec{x_m}}x_i^{0.1} \\\\

    Here, :math:`n` represents the number of dimensions, :math:`m` represents the
    number of objectives, :math:`x_i \\in [0, 1]` for :math:`i=1,...,n`, and
    :math:`\\vec{x_m} = x_m x_{m+1} \\dots x_{n}.`

    The recommendation given in the paper mentioned above is to provide 9 more
    dimensions than objectives. For instance, if we want to use 2 objectives, we
    should use 11 dimensions.

    """
    def __init__(self, dimensions=2, objectives=2):
        Benchmark.__init__(self, dimensions, objectives)
        if dimensions < objectives:
            raise ValueError('dimensions ({0}) must be greater than or equal to objectives ({1})'.format(dimensions, objectives))
        self.bounder = ec.Bounder([0.0] * self.dimensions, [1.0] * self.dimensions)
        self.maximize = False

    def global_optimum(self):
        """Return a globally optimal solution to this problem.

        This function returns a globally optimal solution (i.e., a
        solution that lives on the Pareto front). Since there are many
        solutions that are Pareto-optimal, this function randomly
        chooses one to return.

        """
        x = [random.uniform(0, 1) for _ in range(self.objectives - 1)]
        x.extend([0 for _ in range(self.dimensions - self.objectives + 1)])
        return x

    def generator(self, random, args):
        return [random.uniform(0.0, 1.0) for _ in range(self.dimensions)]

    def evaluator(self, candidates, args):
        fitness = []
        g = lambda x: sum([a**0.1 for a in x])
        for c in candidates:
            gval = g(c[self.objectives-1:])
            theta = lambda x: math.pi / (4.0 * (1 + gval)) * (1 + 2 * gval * x)
            fit = [(1 + gval) * math.cos(math.pi / 2.0 * c[0]) *
                   reduce(lambda x,y: x*y, [math.cos(theta(a)) for a in c[1:self.objectives-1]])]
            for m in reversed(list(range(1, self.objectives))):
                if m == 1:
                    fit.append((1 + gval) * math.sin(math.pi / 2.0 * c[0]))
                else:
                    fit.append((1 + gval) * math.cos(math.pi / 2.0 * c[0]) *
                               reduce(lambda x,y: x*y, [math.cos(theta(a)) for a in c[1:m-1]], 1) *
                               math.sin(theta(c[m-1])))
            fitness.append(emo.Pareto(fit))
        return fitness

class DTLZ7(Benchmark):
    """Defines the DTLZ7 multiobjective benchmark problem.

    This class defines the DTLZ7 multiobjective minimization problem
    taken from `(Deb et al., "Scalable Multi-Objective Optimization Test Problems."
    CEC 2002, pp. 825--830) <http://www.tik.ee.ethz.ch/sop/download/supplementary/testproblems/dtlz1/index.php>`__.
    This function accepts an n-dimensional input and produces an m-dimensional output.
    It is defined as follows:

    .. math::

        f_1(\\vec{x}) &= x_1 \\\\
        f_i(\\vec{x}) &= x_i \\\\
        f_m(\\vec{x}) &= (1 + g(\\vec{x_m}))h(f_1, f_2, \\dots, f_{m-1}, g) \\\\
        g(\\vec{x_m}) &= 1 + \\frac{9}{|\\vec{x_m}|}\\sum_{x_i \\in \\vec{x_m}}x_i \\\\
        h(f_1, f_2, \\dots, f_{m-1}, g) &= m - \\sum_{i=1}^{m-1}\\left[\\frac{f_1}{1+g}(1 + \\sin(3\\pi f_i))\\right] \\\\

    Here, :math:`n` represents the number of dimensions, :math:`m` represents the
    number of objectives, :math:`x_i \\in [0, 1]` for :math:`i=1,...,n`, and
    :math:`\\vec{x_m} = x_m x_{m+1} \\dots x_{n}.`

    The recommendation given in the paper mentioned above is to provide 19 more
    dimensions than objectives. For instance, if we want to use 2 objectives, we
    should use 21 dimensions.

    .. figure:: _static/dtlz7funb.jpg
        :alt: DTLZ7 Pareto front
        :width: 700 px
        :align: center

        Three-dimensional DTLZ7 Pareto front
        (`image source <http://delta.cs.cinvestav.mx/~ccoello/EMOO/testfuncs/>`__)

    """
    def __init__(self, dimensions=2, objectives=2):
        Benchmark.__init__(self, dimensions, objectives)
        if dimensions < objectives:
            raise ValueError('dimensions ({0}) must be greater than or equal to objectives ({1})'.format(dimensions, objectives))
        self.bounder = ec.Bounder([0.0] * self.dimensions, [1.0] * self.dimensions)
        self.maximize = False

    def global_optimum(self):
        """Return a globally optimal solution to this problem.

        This function returns a globally optimal solution (i.e., a
        solution that lives on the Pareto front). Since there are many
        solutions that are Pareto-optimal, this function randomly
        chooses one to return.

        """
        x = [random.uniform(0, 1) for _ in range(self.objectives - 1)]
        x.extend([0 for _ in range(self.dimensions - self.objectives + 1)])
        return x

    def generator(self, random, args):
        return [random.uniform(0.0, 1.0) for _ in range(self.dimensions)]

    def evaluator(self, candidates, args):
        fitness = []
        g = lambda x: 1 + 9.0 / len(x) * sum([a for a in x])
        for c in candidates:
            gval = g(c[self.objectives-1:])
            fit = []
            for m in range(self.objectives-1):
                fit.append(c[m])
            fit.append((1 + gval) * (self.objectives - sum([a / (1.0 + gval) * (1 + math.sin(3 * math.pi * a)) for a in c[:self.objectives-1]])))
            fitness.append(emo.Pareto(fit))
        return fitness


#-----------------------------------------------------------------------
#                  DISCRETE OPTIMIZATION PROBLEMS
#-----------------------------------------------------------------------

class TSP(Benchmark):
    """Defines the Traveling Salesman benchmark problem.

    This class defines the Traveling Salesman problem: given a set of
    locations and their pairwise distances, find the shortest route that
    visits each location once and only once. This problem assumes that
    the ``weights`` parameter is an *n*-by-*n* list of pairwise
    distances among *n* locations. This problem is treated as a
    maximization problem, so fitness values are determined to be the
    reciprocal of the total path length.

    In the case of typical evolutionary computation, a candidate solution
    is represented as a permutation of the *n*-element list of the integers
    from 0 to *n*-1. In the case of ant colony optimization, a candidate
    solution is represented by a list of ``TrailComponent`` objects which
    have (source, destination) tuples as their elements and the reciprocal
    of the weight from source to destination as their values.

    If evolutionary computation is to be used, then the ``generator``
    function should be used to create candidates. If ant colony
    optimization is used, then the ``constructor`` function creates
    candidates. The ``evaluator`` function performs the evaluation for
    both types of candidates.

    Public Attributes:

    - *weights* -- the two-dimensional list of pairwise distances
    - *components* -- the set of ``TrailComponent`` objects constructed
      from the ``weights`` attribute, where the element is the (source,
      destination) tuple and the value is the reciprocal of its
      ``weights`` entry
    - *bias* -- the bias in selecting the component of maximum desirability
      when constructing a candidate solution for ant colony optimization
      (default 0.5)

    """
    def __init__(self, weights):
        Benchmark.__init__(self, len(weights))
        self.weights = weights
        self.components = [swarm.TrailComponent((i, j), value=(1 / weights[i][j])) for i, j in itertools.permutations(list(range(len(weights))), 2)]
        self.bias = 0.5
        self.bounder = ec.DiscreteBounder([i for i in range(len(weights))])
        self.maximize = True
        self._use_ants = False

    def generator(self, random, args):
        """Return a candidate solution for an evolutionary computation."""
        locations = [i for i in range(len(self.weights))]
        random.shuffle(locations)
        return locations

    def constructor(self, random, args):
        """Return a candidate solution for an ant colony optimization."""
        self._use_ants = True
        candidate = []
        while len(candidate) < len(self.weights) - 1:
            # Find feasible components
            feasible_components = []
            if len(candidate) == 0:
                feasible_components = self.components
            elif len(candidate) == len(self.weights) - 1:
                first = candidate[0]
                last = candidate[-1]
                feasible_components = [c for c in self.components if c.element[0] == last.element[1] and c.element[1] == first.element[0]]
            else:
                last = candidate[-1]
                already_visited = [c.element[0] for c in candidate]
                already_visited.extend([c.element[1] for c in candidate])
                already_visited = set(already_visited)
                feasible_components = [c for c in self.components if c.element[0] == last.element[1] and c.element[1] not in already_visited]
            if len(feasible_components) == 0:
                candidate = []
            else:
                # Choose a feasible component
                if random.random() <= self.bias:
                    next_component = max(feasible_components)
                else:
                    next_component = selectors.fitness_proportionate_selection(random, feasible_components, {'num_selected': 1})[0]
                candidate.append(next_component)
        return candidate

    def evaluator(self, candidates, args):
        """Return the fitness values for the given candidates."""
        fitness = []
        if self._use_ants:
            for candidate in candidates:
                total = 0
                for c in candidate:
                    total += self.weights[c.element[0]][c.element[1]]
                last = (candidate[-1].element[1], candidate[0].element[0])
                total += self.weights[last[0]][last[1]]
                fitness.append(1 / total)
        else:
            for candidate in candidates:
                total = 0
                for src, dst in zip(candidate, candidate[1:] + [candidate[0]]):
                    total += self.weights[src][dst]
                fitness.append(1 / total)
        return fitness

class Knapsack(Benchmark):
    """Defines the Knapsack benchmark problem.

    This class defines the Knapsack problem: given a set of items, each
    with a weight and a value, find the set of items of maximal value
    that fit within a knapsack of fixed weight capacity. This problem
    assumes that the ``items`` parameter is a list of (weight, value)
    tuples. This problem is most easily defined as a maximization problem,
    where the total value contained in the knapsack is to be maximized.
    However, for the evolutionary computation (which may create infeasible
    solutions that exceed the knapsack capacity), the fitness is either
    the total value in the knapsack (for feasible solutions) or the
    negative difference between the actual contents and the maximum
    capacity of the knapsack.

    If evolutionary computation is to be used, then the ``generator``
    function should be used to create candidates. If ant colony
    optimization is used, then the ``constructor`` function creates
    candidates. The ``evaluator`` function performs the evaluation for
    both types of candidates.

    Public Attributes:

    - *capacity* -- the weight capacity of the knapsack
    - *items* -- a list of (weight, value) tuples corresponding to the
      possible items to be placed into the knapsack
    - *components* -- the set of ``TrailComponent`` objects constructed
      from the ``items`` parameter
    - *duplicates* -- Boolean value specifying whether items may be
      duplicated in the knapsack (i.e., False corresponds to 0/1 Knapsack)
    - *bias* -- the bias in selecting the component of maximum desirability
      when constructing a candidate solution for ant colony optimization
      (default 0.5)

    """
    def __init__(self, capacity, items, duplicates=False):
        Benchmark.__init__(self, len(items))
        self.capacity = capacity
        self.items = items
        self.components = [swarm.TrailComponent((item[0]), value=item[1]) for item in items]
        self.duplicates = duplicates
        self.bias = 0.5
        if self.duplicates:
            max_count = [self.capacity // item[0] for item in self.items]
            self.bounder = ec.DiscreteBounder([i for i in range(max(max_count)+1)])
        else:
            self.bounder = ec.DiscreteBounder([0, 1])
        self.maximize = True
        self._use_ants = False

    def generator(self, random, args):
        """Return a candidate solution for an evolutionary computation."""
        if self.duplicates:
            max_count = [self.capacity // item[0] for item in self.items]
            return [random.randint(0, m) for m in max_count]
        else:
            return [random.choice([0, 1]) for _ in range(len(self.items))]

    def constructor(self, random, args):
        """Return a candidate solution for an ant colony optimization."""
        self._use_ants = True
        candidate = []
        while len(candidate) < len(self.components):
            # Find feasible components
            feasible_components = []
            if len(candidate) == 0:
                feasible_components = self.components
            else:
                remaining_capacity = self.capacity - sum([c.element for c in candidate])
                if self.duplicates:
                    feasible_components = [c for c in self.components if c.element <= remaining_capacity]
                else:
                    feasible_components = [c for c in self.components if c not in candidate and c.element <= remaining_capacity]
            if len(feasible_components) == 0:
                break
            else:
                # Choose a feasible component
                if random.random() <= self.bias:
                    next_component = max(feasible_components)
                else:
                    next_component = selectors.fitness_proportionate_selection(random, feasible_components, {'num_selected': 1})[0]
                candidate.append(next_component)
        return candidate

    def evaluator(self, candidates, args):
        """Return the fitness values for the given candidates."""
        fitness = []
        if self._use_ants:
            for candidate in candidates:
                total = 0
                for c in candidate:
                    total += c.value
                fitness.append(total)
        else:
            for candidate in candidates:
                total_value = 0
                total_weight = 0
                for c, i in zip(candidate, self.items):
                    total_weight += c * i[0]
                    total_value += c * i[1]
                if total_weight > self.capacity:
                    fitness.append(self.capacity - total_weight)
                else:
                    fitness.append(total_value)
        return fitness


