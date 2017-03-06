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
        
    .. module:: topologies
    .. moduleauthor:: Aaron Garrett <garrett@inspiredintelligence.io>
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
    
