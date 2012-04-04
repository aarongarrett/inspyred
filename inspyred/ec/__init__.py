"""
    ===============================================
    :mod:`ec` -- Evolutionary computation framework
    ===============================================
    
    This module provides a framework for creating evolutionary computations.
    
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
from inspyred.ec.ec import Bounder
from inspyred.ec.ec import DEA
from inspyred.ec.ec import DiscreteBounder
from inspyred.ec.ec import EDA
from inspyred.ec.ec import Error
from inspyred.ec.ec import ES
from inspyred.ec.ec import EvolutionaryComputation
from inspyred.ec.ec import EvolutionExit
from inspyred.ec.ec import GA
from inspyred.ec.ec import Individual
from inspyred.ec.ec import SA
import inspyred.ec.analysis
import inspyred.ec.archivers
import inspyred.ec.emo
import inspyred.ec.evaluators
import inspyred.ec.migrators
import inspyred.ec.observers
import inspyred.ec.replacers
import inspyred.ec.selectors
import inspyred.ec.terminators
import inspyred.ec.utilities
import inspyred.ec.variators

__all__ = ['Bounder', 'DiscreteBounder', 'Individual', 'Error', 'EvolutionExit', 
           'EvolutionaryComputation', 'GA', 'ES', 'EDA', 'DEA', 'SA',
           'analysis', 'archivers', 'emo', 'evaluators', 'migrators', 'observers', 
           'replacers', 'selectors', 'terminators', 'utilities', 'variators']


