from mpi4py import MPI
from random import Random
from time import time
import inspyred
import math

comm = MPI.COMM_WORLD
rank = comm.rank
size = comm.size


def generate_rastrigin(random, args):
	size = args.get('num_inputs', 10)
	return [random.uniform(-5.12, 5.12) for i in range(size)]

def evaluate_rastrigin(candidates, args):
	fitness = []
	for cs in candidates:
		fit = 10 * len(cs) + sum([((x - 1)**2 - 10 * 
								   math.cos(2 * math.pi * (x - 1))) 
								   for x in cs])
		fitness.append(fit)
	return fitness

def parallel_evaluation_mpi(candidates, args):
	try:
		evaluator = args['mpi_evaluator']
	except KeyError:
		logger.error('parallel_evaluation_mpi requires \'mpi_evaluator\' be defined in the keyword arguments list')
		raise 
	if rank == 0:
		xargs = comm.scatter([ args                for x in range(size)],root=0)
		rbuf = comm.scatter([ candidates[x::size] for x in range(size)],root=0)
		fitness = evaluate_rastrigin(rbuf, args)
		pbuf = comm.gather(fitness,root=0)
		fitness = [ 0 for x in candidates ]
		for i,x in enumerate(pbuf):
			for j,f in enumerate(x):
				fitness[i+j*size] = f		
	else:
		"""
		The main loop for workers here.
		We don't need additional GA running on nodes.
		"""
		while 1:
			xargs = comm.scatter(None,root=0)
			if 'mpi_stop' in xargs: break
			rbuf = comm.scatter(None,root=0)
			fitness = evaluate_rastrigin(rbuf, xargs)
			pbuf = comm.gather(fitness,root=0)
		exit(0)
	return fitness


def main(prng=None, display=False):	
	if prng is None:
		prng = Random()
		prng.seed(time()) 

	ea = inspyred.ec.DEA(prng)
	if display:
		ea.observer = inspyred.ec.observers.stats_observer 
	ea.terminator = inspyred.ec.terminators.evaluation_termination
	final_pop = ea.evolve(generator=generate_rastrigin, 
						  evaluator=parallel_evaluation_mpi,
						  mpi_evaluator=evaluate_rastrigin, 
						  pop_size=8, 
						  bounder=inspyred.ec.Bounder(-5.12, 5.12),
						  maximize=False,
						  max_evaluations=256,
						  num_selected=int(2*(size/2+1)),
						  num_inputs=3)
	#the last good bey
	rbuf = comm.scatter([ {'mpi_stop':True} for x in range(size)],root=0)					  
	if display:
		best = max(final_pop) 
		print('Best Solution: \n{0}'.format(str(best)))
	return ea

if __name__ == '__main__':
	main(display=True)
