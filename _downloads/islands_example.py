import random
import time
import multiprocessing
import inspyred

def create_island(rand_seed, island_number, problem, mp_migrator):
    evals = 200
    psize = 20
    rand = random.Random()
    rand.seed(rand_seed)
    ec = inspyred.ec.EvolutionaryComputation(rand)
    ec.observer = [inspyred.ec.observers.stats_observer, inspyred.ec.observers.file_observer]
    ec.terminator = inspyred.ec.terminators.evaluation_termination
    ec.selector = inspyred.ec.selectors.tournament_selection
    ec.replacer = inspyred.ec.replacers.generational_replacement
    ec.variator = [inspyred.ec.variators.blend_crossover, inspyred.ec.variators.gaussian_mutation]
    ec.migrator = mp_migrator
    final_pop = ec.evolve(generator=problem.generator,
                          evaluator=problem.evaluator, 
                          bounder=problem.bounder,
                          maximize=problem.maximize,
                          statistics_file=open("stats_%d.csv" % island_number, "w"),
                          individuals_file=open("inds_%d.csv" % island_number, "w"),
                          max_evaluations=evals,
                          num_elites=1,
                          pop_size=psize,
                          num_selected=psize,
                          evaluate_migrant=False)
    

if __name__ == "__main__":  
    cpus = 2
    problem = inspyred.benchmarks.Rastrigin(2)
    mp_migrator = inspyred.ec.migrators.MultiprocessingMigrator(1)
    rand_seed = int(time.time())
    jobs = []
    for i in range(cpus):
        p = multiprocessing.Process(target=create_island, args=(rand_seed + i, i, problem, mp_migrator))
        p.start()
        jobs.append(p)
    for j in jobs:
        j.join()

