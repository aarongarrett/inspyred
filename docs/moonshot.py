# Title:  Moon probe evolution example
# Author: Mike Vella

#start_imports
import os
import math
import pylab
import itertools
from matplotlib import pyplot as plt
from matplotlib.patches import Circle
from random import Random
from time import time
import inspyred
#end_imports

# All units are in SI unless stated otherwise.

# Global constants
#start_globals
G = 6.67300e-11 # Universal gravitational constant
earth_mass = 5.9742e24
earth_radius = 6.378e6
moon_mass = 7.36e22
moon_radius = 1.737e6
moon_position = (384403e3, 0)
earth_position = (0, 0)
#end_globals

def pairwise(iterable):
    """s -> (s0,s1), (s1,s2), (s2, s3), ..."""
    a, b = itertools.tee(iterable)
    next(b, None)
    return itertools.izip(a, b)
    
def distance_between(position_a, position_b):
    return math.sqrt((position_a[0] - position_b[0])**2 + (position_a[1] - position_b[1])**2)
    
def gravitational_force(position_a, mass_a, position_b, mass_b):
    """Returns the gravitational force between the two bodies a and b."""
    distance = distance_between(position_a, position_b)

    # Calculate the direction and magnitude of the force.
    angle = math.atan2(position_a[1] - position_b[1], position_a[0] - position_b[0])
    magnitude = G * mass_a * mass_b / (distance**2)

    # Find the x and y components of the force.
    # Determine sign based on which one is the larger body.
    sign = -1 if mass_b > mass_a else 1
    x_force = sign * magnitude * math.cos(angle)
    y_force = sign * magnitude * math.sin(angle)
    return x_force, y_force

def force_on_satellite(position, mass):
    """Returns the total gravitational force acting on the body from the Earth and Moon."""
    earth_grav_force = gravitational_force(position, mass, earth_position, earth_mass)
    moon_grav_force = gravitational_force(position, mass, moon_position, moon_mass)
    F_x = earth_grav_force[0] + moon_grav_force[0]
    F_y = earth_grav_force[1] + moon_grav_force[1]
    return F_x, F_y

def acceleration_of_satellite(position, mass):
    """Returns the acceleration based on all forces acting upon the body."""
    F_x, F_y = force_on_satellite(position, mass)
    return F_x / mass, F_y / mass

def moonshot(orbital_height, satellite_mass, boost_velocity, initial_y_velocity, 
             time_step=60, max_iterations=5e4, plot_trajectory=False):
    fitness = 0.0
    distance_from_earth_center = orbital_height + earth_radius
    eqb_velocity = math.sqrt(G * earth_mass / distance_from_earth_center)
    
    # Start the simulation.
    # Keep up with the positions of the satellite as it moves.
    position = [(earth_radius + orbital_height, 0.0)] # The initial position of the satellite.
    velocity = [0.0, initial_y_velocity]
    time = 0
    min_distance_from_moon = distance_between(position[-1], moon_position) - moon_radius

    i = 0 
    keep_simulating = True
    rockets_boosted = False

    while keep_simulating:
        # Calculate the acceleration and corresponding change in velocity.
        # (This is effectively the Forward Euler Algorithm.)
        acceleration = acceleration_of_satellite(position[-1], satellite_mass)
        velocity[0] += acceleration[0] * time_step
        velocity[1] += acceleration[1] * time_step 

        # Start the rocket burn:
        # add a boost in the +x direction of 1m/s
        # closest point to the moon
        if position[-1][1] < -100 and position[-1][0] > distance_from_earth_center-100 and not rockets_boosted: 
            launch_point = position[-1]
            velocity[0] += boost_velocity[0]
            velocity[1] += boost_velocity[1]
            rockets_boosted = True

        # Calculate the new position based on the velocity.
        position.append((position[-1][0] + velocity[0] * time_step, 
                         position[-1][1] + velocity[1] * time_step))
        time += time_step

        if i >= max_iterations:
            keep_simulating = False

        distance_from_moon_surface = distance_between(position[-1], moon_position) - moon_radius
        distance_from_earth_surface = distance_between(position[-1], earth_position) - earth_radius
        if distance_from_moon_surface < min_distance_from_moon:
            min_distance_from_moon = distance_from_moon_surface
            
        # See if the satellite crashes into the Moon or the Earth, or
        # if the satellite gets too far away (radio contact is lost).
        if distance_from_moon_surface <= 0:
            fitness += 100000 # penalty of 100,000 km if crash on moon
            keep_simulating = False
        elif distance_from_earth_surface <= 0:
            keep_simulating = False
            fitness -= 100000 # reward of 100,000 km if land on earth
        elif distance_from_earth_surface > 2 * distance_between(earth_position, moon_position): 
            keep_simulating = False #radio contact lost
        i += 1

    # Augment the fitness to include the minimum distance (in km) 
    # that the satellite made it to the Moon (lower without crashing is better).
    fitness += min_distance_from_moon / 1000.0 
    
    # Augment the fitness to include 1% of the total distance
    # traveled by the probe (in km). This means the probe
    # should prefer shorter paths.
    total_distance = 0
    for p, q in pairwise(position):
        total_distance += distance_between(p, q)
    fitness += total_distance / 1000.0 * 0.01

    if plot_trajectory:
        axes = plt.gca()
        earth = Circle(earth_position, earth_radius, facecolor='b', alpha=1)
        moon = Circle(moon_position, moon_radius, facecolor='0.5', alpha=1)
        axes.add_artist(earth)
        axes.add_artist(moon)
        axes.annotate('Earth', xy=earth_position,  xycoords='data',
                      xytext=(0, 1e2), textcoords='offset points',
                      arrowprops=dict(arrowstyle="->"))
        axes.annotate('Moon', xy=moon_position,  xycoords='data',
                      xytext=(0, 1e2), textcoords='offset points',
                      arrowprops=dict(arrowstyle="->"))
        x = [p[0] for p in position] 
        y = [p[1] for p in position]
        cm = pylab.get_cmap('gist_rainbow')
        lines = plt.scatter(x, y, c=range(len(x)), cmap=cm, marker='o', s=2)
        plt.setp(lines, edgecolors='None')  
        plt.axis("equal")
        plt.grid("on")
        projdir = os.path.dirname(os.getcwd())
        name = '{0}/{1}.pdf'.format(projdir, str(fitness))
        plt.savefig(name, format="pdf")
        plt.clf()
        
    return fitness


def satellite_generator(random, args):
    chromosome = []
    bounder = args["_ec"].bounder
    # The constraints are as follows:
    #             orbital   satellite   boost velocity      initial y
    #             height    mass        (x,       y)        velocity
    for lo, hi in zip(bounder.lower_bound, bounder.upper_bound):
        chromosome.append(random.uniform(lo, hi))
    return chromosome

def moonshot_evaluator(candidates, args):
    fitness=[]
    for chromosome in candidates:
        orbital_height = chromosome[0]
        satellite_mass = chromosome[1]
        boost_velocity = (chromosome[2], chromosome[3])
        initial_y_velocity = chromosome[4]
        fitness.append(moonshot(orbital_height, satellite_mass, boost_velocity, initial_y_velocity))
    return fitness
    
def custom_observer(population, num_generations, num_evaluations, args):
    best = max(population)
    print('Generations: {0}  Evaluations: {1}  Best: {2}'.format(num_generations, num_evaluations, str(best)))

   
#start_main   
rand = Random()
rand.seed(int(time()))
# The constraints are as follows:
#             orbital   satellite   boost velocity      initial y
#             height    mass        (x,       y)        velocity
constraints=((6e6,      10.0,       3e3,    -10000.0,   4000), 
             (8e6,      40.0,       9e3,     10000.0,   6000))

algorithm = inspyred.ec.EvolutionaryComputation(rand)
algorithm.terminator = inspyred.ec.terminators.evaluation_termination
algorithm.observer = inspyred.ec.observers.file_observer
algorithm.selector = inspyred.ec.selectors.tournament_selection
algorithm.replacer = inspyred.ec.replacers.generational_replacement
algorithm.variator = [inspyred.ec.variators.blend_crossover, inspyred.ec.variators.gaussian_mutation]
projdir = os.path.dirname(os.getcwd())

stat_file_name = '{0}/moonshot_ec_statistics.csv'.format(projdir)
ind_file_name = '{0}/moonshot_ec_individuals.csv'.format(projdir)
stat_file = open(stat_file_name, 'w')
ind_file = open(ind_file_name, 'w')
final_pop = algorithm.evolve(generator=satellite_generator,
                             evaluator=moonshot_evaluator,
                             pop_size=100,
                             maximize=False,
                             bounder=inspyred.ec.Bounder(constraints[0], constraints[1]),
                             num_selected=100,
                             tournament_size=2,
                             num_elites=1,
                             mutation_rate=0.3,
                             max_evaluations=600,
                             statistics_file=stat_file,
                             individuals_file=ind_file)

stat_file.close()
ind_file.close()

# Sort and print the fittest individual, who will be at index 0.
final_pop.sort(reverse=True)
best = final_pop[0]
components = best.candidate
print('\nFittest individual:')
print(best)
moonshot(components[0], components[1], (components[2], components[3]), components[4], plot_trajectory=True)
#end_main
