"""
    ===============================================
    :mod:`analysis` -- Optimization result analysis
    ===============================================
    
    This module provides analysis methods for the results of evolutionary computations.

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
       
    .. module:: analysis
    .. moduleauthor:: Aaron Garrett <aaron.lee.garrett@gmail.com>
"""
import csv
import math

def fitness_statistics(population):
    """Return the basic statistics of the population's fitness values.
    
    This function returns a dictionary containing the "best", "worst",
    "mean", "median", and "std" fitness values in the population.
    ("std" is the standard deviation.) A typical usage would be similar
    to the following::
    
       stats = fitness_statistics(population)
       print(stats['best'])
       print(stats['worst'])
       print(stats['mean'])
       print(stats['median'])
       print(stats['std'])
    
    .. note::
    
       This function makes use of the numpy library for calculations. If that
       library is not found, it attempts to complete the calculations 
       internally. However, this second attempt will fail for multiobjective
       fitness values and will return ``nan`` for the mean, median, and 
       standard deviation.
    
    Arguments:
    
    - *population* -- the population of individuals 

    """
    population.sort(reverse=True)
    worst_fit = population[-1].fitness
    best_fit = population[0].fitness
    try:
        import numpy
        f = [p.fitness for p in population]
        med_fit = numpy.median(f)
        avg_fit = numpy.mean(f)
        std_fit = numpy.std(f)
    except ImportError:
        try:
            plen = len(population)
            if plen % 2 == 1:
                med_fit = population[(plen - 1) // 2].fitness
            else:
                med_fit = float(population[plen // 2 - 1].fitness + population[plen // 2].fitness) / 2
            avg_fit = sum([p.fitness for p in population]) / float(plen)
            if plen > 1:
                std_fit = math.sqrt(sum([(p.fitness - avg_fit)**2 for p in population]) / float(plen - 1))
            else:
                std_fit = 0
        except TypeError:
            med_fit = float('nan')
            avg_fit = float('nan')
            std_fit = float('nan')
    return {'best': best_fit, 'worst': worst_fit, 'mean': avg_fit, 
            'median': med_fit, 'std': std_fit}
            

def generation_plot(filename, errorbars=True):
    """Plot the results of the algorithm using generation statistics.
    
    This function creates a plot of the generation fitness statistics 
    (best, worst, median, and average). This function requires the 
    pylab and matplotlib libraries.
    
    .. note::
    
       This function only works for single-objective problems.

    .. figure:: _static/generation_plot.png
        :alt: Example generation plot
        :align: center
        
        An example image saved from the ``generation_plot`` function (without error bars).
    
    Arguments:
    
    - *filename* -- the name of the statistics file produced by the file_observer 
    - *errorbars* -- Boolean value stating whether standard error bars should 
      be drawn (default True)

    """
    import pylab
    import matplotlib.font_manager 
    
    generation = []
    psize = []
    worst = []
    best = []
    median = []
    average = []
    stdev = []
    reader = csv.reader(open(filename))
    for row in reader:
        generation.append(int(row[0]))
        psize.append(int(row[1]))
        worst.append(float(row[2]))
        best.append(float(row[3]))
        median.append(float(row[4]))
        average.append(float(row[5]))
        stdev.append(float(row[6]))
    stderr = [s / math.sqrt(p) for s, p in zip(stdev, psize)]
    
    data = [average, median, best, worst]
    colors = ['black', 'blue', 'green', 'red']
    labels = ['average', 'median', 'best', 'worst']
    figure = pylab.figure()
    if errorbars:
        pylab.errorbar(generation, average, stderr, color=colors[0], label=labels[0])
    else:
        pylab.plot(generation, average, color=colors[0], label=labels[0])
    for d, col, lab in zip(data[1:], colors[1:], labels[1:]):
        pylab.plot(generation, d, color=col, label=lab)
    pylab.fill_between(generation, data[2], data[3], color='#e6f2e6')
    pylab.grid(True)
    ymin = min([min(d) for d in data])
    ymax = max([max(d) for d in data])
    yrange = ymax - ymin
    pylab.ylim((ymin - 0.1*yrange, ymax + 0.1*yrange))  
    prop = matplotlib.font_manager.FontProperties(size=8) 
    pylab.legend(loc='upper left', prop=prop)    
    pylab.xlabel('Generation')
    pylab.ylabel('Fitness')
    pylab.show()    

    
def allele_plot(filename, normalize=False, alleles=None, generations=None):
    """Plot the alleles from each generation from the individuals file.
    
    This function creates a plot of the individual allele values as they
    change through the generations. It creates three subplots, one for each
    of the best, median, and average individual. The best and median 
    individuals are chosen using the fitness data for each generation. The 
    average individual, on the other hand, is actually an individual created
    by averaging the alleles within a generation. This function requires the 
    pylab library.

    .. note::
    
       This function only works for single-objective problems.

    .. figure:: _static/allele_plot.png
        :alt: Example allele plot
        :align: center
        
        An example image saved from the ``allele_plot`` function.
    
    Arguments:
    
    - *filename* -- the name of the individuals file produced by the file_observer 
    - *normalize* -- Boolean value stating whether allele values should be
      normalized before plotting (default False)
    - *alleles* -- a list of allele index values that should be plotted
      (default None)
    - *generations* -- a list of generation numbers that should be plotted
      (default None)

    If *alleles* is ``None``, then all alleles are plotted. Similarly, if 
    *generations* is ``None``, then all generations are plotted.

    """    
    import pylab
    
    generation_data = []
    reader = csv.reader(open(filename))
    for row in reader:
        g = int(row[0])
        row[3] = row[3].replace('[', '')
        row[-1] = row[-1].replace(']', '')
        individual = [float(r) for r in row[3:]]
        individual.append(float(row[2]))
        try:
            generation_data[g]
        except IndexError:
            generation_data.append([])
        generation_data[g].append(individual)
    for gen in generation_data:
        gen.sort(key=lambda x: x[-1])
        for j, g in enumerate(gen):
            gen[j] = g[:-1]
        
    best = []
    median = []
    average = []
    for gen in generation_data:
        best.append(gen[0])
        plen = len(gen)
        if plen % 2 == 1:
            med = gen[(plen - 1) // 2]
        else:
            med = []
            for a, b in zip(gen[plen // 2 - 1], gen[plen // 2]):
                med.append(float(a + b) / 2)
        median.append(med)
        avg = [0] * len(gen[0])
        for individual in gen:
            for i, allele in enumerate(individual):
                avg[i] += allele
        for i, a in enumerate(avg):
            avg[i] /= float(len(gen))
        average.append(avg)        
    
    for plot_num, (data, title) in enumerate(zip([best, median, average], 
                                                 ["Best", "Median", "Average"])):
        if alleles is None:
            alleles = list(range(len(data[0])))
        if generations is None:
            generations = list(range(len(data)))    
        if normalize:
            columns = list(zip(*data))
            max_col = [max(c) for c in columns]
            min_col = [min(c) for c in columns]
            for dat in data:
                for i, d in enumerate(dat):
                    dat[i] = (d - min_col[i]) / float(max_col[i] - min_col[i])
        plot_data = []
        for g in generations:
            plot_data.append([data[g][a] for a in alleles])
        sub = pylab.subplot(3, 1, plot_num + 1)
        pylab.pcolor(pylab.array(plot_data))
        pylab.colorbar()
        step_size = max(len(generations) // 7, 1)
        ytick_locs = list(range(step_size, len(generations), step_size))
        ytick_labs = generations[step_size::step_size]
        pylab.yticks(ytick_locs, ytick_labs)
        pylab.ylabel('Generation')
        if plot_num == 2:
            xtick_locs = list(range(len(alleles)))
            xtick_labs = alleles
            pylab.xticks(xtick_locs, xtick_labs)
            pylab.xlabel('Allele')
        else:
            pylab.setp(sub.get_xticklabels(), visible=False)
        pylab.title(title)
    pylab.show()

    
def hypervolume(pareto_set, reference_point=None):
    """Calculates the hypervolume by slicing objectives (HSO).
    
    This function calculates the hypervolume (or S-measure) of a nondominated
    set using the Hypervolume by Slicing Objectives (HSO) procedure of `While, et al. 
    (IEEE CEC 2005) <http://www.lania.mx/~ccoello/EMOO/while05a.pdf.gz>`_.
    The *pareto_set* should be a list of lists of objective values.
    The *reference_point* may be specified or it may be left as the default 
    value of None. In that case, the reference point is calculated to be the
    maximum value in the set for all objectives (the ideal point). This function 
    assumes that objectives are to be maximized.
    
    Arguments:
    
    - *pareto_set* -- the list or lists of objective values comprising the Pareto front
    - *reference_point* -- the reference point to be used (default None)
    
    """
    def dominates(p, q, k=None):
        if k is None:
            k = len(p)
        d = True
        while d and k < len(p):
            d = not (q[k] > p[k])
            k += 1
        return d
        
    def insert(p, k, pl):
        ql = []
        while pl and pl[0][k] > p[k]:
            ql.append(pl[0])
            pl = pl[1:]
        ql.append(p)
        while pl:
            if not dominates(p, pl[0], k):
                ql.append(pl[0])
            pl = pl[1:]
        return ql

    def slice(pl, k, ref):
        p = pl[0]
        pl = pl[1:]
        ql = []
        s = []
        while pl:
            ql = insert(p, k + 1, ql)
            p_prime = pl[0]
            s.append((math.fabs(p[k] - p_prime[k]), ql))
            p = p_prime
            pl = pl[1:]
        ql = insert(p, k + 1, ql)
        s.append((math.fabs(p[k] - ref[k]), ql))
        return s

    ps = pareto_set
    ref = reference_point
    n = min([len(p) for p in ps])
    if ref is None:
        ref = [max(ps, key=lambda x: x[o])[o] for o in range(n)]
    pl = ps[:]
    pl.sort(key=lambda x: x[0], reverse=True)
    s = [(1, pl)]
    for k in range(n - 1):
        s_prime = []
        for x, ql in s:
            for x_prime, ql_prime in slice(ql, k, ref):
                s_prime.append((x * x_prime, ql_prime))
        s = s_prime
    vol = 0
    for x, ql in s:
        vol = vol + x * math.fabs(ql[0][n - 1] - ref[n - 1])
    return vol



    
    
