from pyIsotherm.Models import obj_func
from pyIsotherm.Models import call_model
from pyIsotherm.Particle import Particle
from pyIsotherm.Isotherm import Isotherm
from pyIsotherm.Result import Result
from matplotlib import colors


def estimate(p, qe, model, part_n=100, iter_n=100, param=[[0.1, 10], [1, 100], [0.1, 10]], comp_n=1, relative=False):

    if param is None:
        param = [[0.1, 10], [1, 100], [0.1, 10]]
    particles_list = []
    swarm_best_fitness = float('inf')
    swarm_best_position = [1, 1, 1]
    for _ in range(part_n):
        for _ in range(comp_n):
            particle = Particle(param)
            fitness = obj_func(p, qe, particle.position, model, relative)
            particle.fitness = fitness
            particle.best_position = particle.position.copy()
            particle.best_fitness = fitness
            particles_list.append(particle)
            if _ == 0:
                swarm_best_fitness = fitness
                swarm_best_position = particle.position.copy()
            if fitness < swarm_best_fitness:
                swarm_best_fitness = fitness
                swarm_best_position = particle.position.copy()

    for _ in range(iter_n):
        for particle in particles_list:
            particle.update_velocity(swarm_best_position)
            particle.update_position()
            fitness = obj_func(p, qe, particle.position, model, relative)
            particle.fitness = fitness
            if fitness < particle.best_fitness:
                particle.best_fitness = fitness
                particle.best_position = particle.position.copy()
            if fitness < swarm_best_fitness:
                swarm_best_fitness = fitness
                swarm_best_position = particle.position.copy()

    if not isinstance(swarm_best_fitness, (int, float)):
        exit(ValueError("ERROR: Swarm best fitness is not a number"))

    if swarm_best_fitness == float('inf'):
        exit(ValueError("ERROR: Swarm best fitness is infinite"))

    if not all(isinstance(n, (float, int)) for n in swarm_best_position):
        exit(ValueError("ERROR: There are parameters that are not numbers"))

    if any(n == float('inf') for n in swarm_best_position):
        exit(ValueError("ERROR: There are parameters that are infinite"))

    if any(n < 0 for n in swarm_best_position):
        print(f"\033[93mWARNING: There are parameters that are negative\033[0m")

    exp_iso = Isotherm(p, qe)

    qsim = []
    qfunc = call_model(model)

    for press in p:
        qsim.append(qfunc(press, swarm_best_position))

    sim_iso = Isotherm(p, qsim)

    return Result(swarm_best_position, swarm_best_fitness, exp_iso, sim_iso)
