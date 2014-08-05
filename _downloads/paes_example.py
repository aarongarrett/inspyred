from random import Random
from time import time
import inspyred

def main(prng=None, display=False):
    if prng is None:
        prng = Random()
        prng.seed(time()) 
        
    problem = inspyred.benchmarks.Kursawe(3)
    ea = inspyred.ec.emo.PAES(prng)
    ea.terminator = inspyred.ec.terminators.evaluation_termination
    final_pop = ea.evolve(generator=problem.generator, 
                          evaluator=problem.evaluator, 
                          bounder=problem.bounder,
                          maximize=problem.maximize,
                          max_evaluations=10000,
                          max_archive_size=100,
                          num_grid_divisions=4)
    
    if display:
        final_arc = ea.archive
        print('Best Solutions: \n')
        for f in final_arc:
            print(f)
        import pylab
        x = []
        y = []
        for f in final_arc:
            x.append(f.fitness[0])
            y.append(f.fitness[1])
        pylab.scatter(x, y, color='b')
        pylab.savefig('{0} Example ({1}).pdf'.format(ea.__class__.__name__, 
                                                     problem.__class__.__name__), 
                      format='pdf')
        pylab.show()
    return ea

if __name__ == '__main__':
    main(display=True)
