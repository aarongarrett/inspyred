"""
    ==================================
    :mod:`swarm` -- Swarm intelligence
    ==================================
    
    This module provides standard swarm intelligence algorithms.
    
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
       
    .. moduleauthor:: Aaron Garrett <aaron.lee.garrett@gmail.com>
"""
from inspyred.swarm.swarm import ACS
from inspyred.swarm.swarm import PSO
from inspyred.swarm.swarm import TrailComponent
import inspyred.swarm.topologies

__all__ = ['ACS', 'PSO', 'TrailComponent', 'topologies']
