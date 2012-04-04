"""
    =====================================
    :mod:`topologies` -- Swarm topologies
    =====================================
    
    This module defines various topologies for swarm intelligence algorithms.
    
    Particle swarms make use of topologies, which determine the logical
    relationships among particles in the swarm (i.e., which ones belong to the same
    "neighborhood"). All topology functions have the following arguments:
        
    - *random* -- the random number generator object
    - *population* -- the population of Particles
    - *args* -- a dictionary of keyword arguments
        
    Each topology function returns a list of lists of neighbors
    for each particle in the population. For example, if a swarm
    contained 10 particles, then this function would return a list
    containing 10 lists, each of which contained the neighbors for 
    its corresponding particle in the population. 
    
    Rather than constructing and returning a list of lists directly, the 
    topology functions could (and probably *should*, for efficiency) be 
    written as generators that yield each neighborhood list one at a 
    time. This is how the existing topology functions operate.

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
       
    .. module:: topologies
    .. moduleauthor:: Aaron Garrett <aaron.lee.garrett@gmail.com>
"""


def star_topology(random, population, args):
    """Returns the neighbors using a star topology.
    
    This function sets all particles as neighbors for all other particles.
    This is known as a star topology. The resulting list of lists of 
    neighbors is returned.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of particles
       args -- a dictionary of keyword arguments
    
    """
    for _ in range(len(population)):
        yield population[:]
    
    
def ring_topology(random, population, args):
    """Returns the neighbors using a ring topology.
    
    This function sets all particles in a specified sized neighborhood
    as neighbors for a given particle. This is known as a ring 
    topology. The resulting list of lists of neighbors is returned.
    
    .. Arguments:
       random -- the random number generator object
       population -- the population of particles
       args -- a dictionary of keyword arguments

    Optional keyword arguments in args:
    
    - *neighborhood_size* -- the width of the neighborhood around a 
      particle which determines the size of the neighborhood
      (default 3)
    
    """
    neighborhood_size = args.setdefault('neighborhood_size', 3)
    half_hood = neighborhood_size // 2
    neighbor_index_start = []
    for index in range(len(population)):
        if index < half_hood:
            neighbor_index_start.append(len(population) - half_hood + index)
        else:
            neighbor_index_start.append(index - half_hood)
    neighbors = []
    for start in neighbor_index_start:
        n = []
        for i in range(0, neighborhood_size):
            n.append(population[(start + i) % len(population)])
        yield n
    
