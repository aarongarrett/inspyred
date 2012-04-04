**********************************
Introduction to Swarm Intelligence
**********************************


===========================
Particle Swarm Optimization
===========================

In addition to the evolutionary computation techniques described above, another nature-inspired optimization algorithm, called *particle swarm optimization* (PSO), was developed by Kennedy and Eberhart in 1995 [Kennedy1995]_. Inspired by the movement of bird flocks and insect swarms, they attempted to develop a model of swarm behavior that could be used to solve optimization problems. To create the analogy, they imagined a flock of birds flying around in search of a corn field. Each bird was capable of remembering the best location it had found, and each was capable of knowing the best location that any of the birds had found. The birds were allowed to fly around while being pulled toward both their individual best locations and the flock's best location. Kennedy and Eberhart found that their simulation of this analogy produced very realistic-looking behavior in their virtual flocks [Kennedy1995]_.

In the PSO model presented in [Kennedy1995]_ and expanded in [Kennedy1997]_, each particle is composed of three vectors: :math:`x`, :math:`p`, and :math:`v`. These represent the particle's current location, best location found, and velocity, respectively. These vectors are each of the same dimensionality as the search space. Additionally, each particle maintains a two values: one corresponding to the fitness of the :math:`x` vector and the other to the fitness of the :math:`p` vector.

As the particles in the swarm move around the search space, their velocities are first updated according to the following equation:

.. math::

    v_{id} = v_{id} + \phi_1R_1(p_{id} - x_{id}) + \phi_2R_2(g_{id} - x_{id})

In this equation, :math:`v_{id}` is the velocity of the :math:`i^{th}` particle along the :math:`d^{th}` dimension. The :math:`g` vector represents the best location found by the flock, and :math:`R_1` and :math:`R_2` are uniform random values such that :math:`0 \leq R_1,R_2 \leq 1`. Finally, :math:`\phi_1` and :math:`\phi_2` are two constants that control the influence of the personal best and the global best locations, respectively, on the particle's velocity. These values are often referred to as *cognitive* and *social* learning rates, respectively [Kennedy1997]_.

After the velocity vector is updated, the particle's location is updated by applying the following equation:

.. math::

    x_{id} = x_{id} + v_{id}

At this point, the new location's fitness is evaluated and compared to the fitness of the particle's personal best location. If the new location is better, then it also becomes the new personal best location for the particle.

The *topology* for a swarm refers to the structure of the neighborhood for each particle. In a *star topology*, all the particles exist in the same neighborhood, so the global best vector represents the best location found by any particle in the swarm. In contrast, a *ring topology* arranges the particles into overlapping neighborhoods of size *h*. The global best vector in this type of topology represents the best location found by any particle in that particle's neighborhood.

In 1999, Maurice Clerc introduced an improvement to the equation for updating the velocity of a particle [Clerc1999]_. He introduced a constant to be multiplied to the new velocity before updating the location of the particle. He called this constant the *constriction coefficient* [Clerc1999]_. The calculation of this coefficient is as follows:

.. math::

    K = \frac{2}{\left|2 - \phi - \sqrt{\phi^2 - 4\phi}\right|}

In this equation, :math:`\phi_ = \phi_1 + \phi_2` and :math:`\phi > 4`. The constriction coefficient is used to restrain the velocity vector of each particle so that it does not grow unbounded.

Finally, various other models have been proposed as alternatives to the so-called full model presented above [Eberhart2000]_. The *cognitive-only* model sets :math:`\phi_1` to 0, while the *social-only* model sets :math:`\phi_2` to 0. A *selfless* model was also developed which was identical to the social-only model except that a particle's personal best was not included in the search for that particle's neighborhood's global best [Eberhart2000]_.


==========
References
==========

.. [Clerc1999] \M. Clerc, "The swarm and the queen: towards a deterministic and adaptive particle swarm optimization," in *Proceedings of the International Conference on Evolutionary Computation*, Washington, DC, 1999, pp. 1951-1957.

.. [Eberhart2000] \R. C. Eberhart and Y. Shi, "Comparing inertia weights and constriction factors in particle swarm optimization," in *Proceedings of the Congress on Evolutionary Computation*, Washington, DC, 2000, pp. 84-88. 

.. [Kennedy1995] \J. Kennedy and R. Eberhart, "Particle swarm optimization," in *Proceedings of the IEEE Conference on Neural Networks*, Perth, Australia, 1995, pp. 1942-1948.

.. [Kennedy1997] \J. Kennedy, "The particle swarm: Social adaptation of knowledge," in *Proceedings of the International Conference on Evolutionary Computation*, Indianapolis, IN, 1997, pp. 303-308.
