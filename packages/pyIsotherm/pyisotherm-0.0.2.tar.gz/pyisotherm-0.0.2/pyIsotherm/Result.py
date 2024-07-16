import numpy as np
from scipy import stats
from matplotlib import pyplot as plt
from pyIsotherm.Isotherm import Isotherm


class Result:
    parameters: list
    fitness: float
    exp_isotherm: Isotherm
    sim_isotherm: Isotherm

    def __init__(self, parameters: list, fitness: float, exp_isotherm: Isotherm, sim_isotherm: Isotherm):

        self.parameters = parameters
        self.fitness = fitness
        self.exp_isotherm = exp_isotherm
        self.sim_isotherm = sim_isotherm

    def plot(self, export=False, extension='png', only_exp=False, only_sim=False, legend=False):

        new_p_exp, new_q_exp = (list(t) for t in zip(*sorted(zip(self.exp_isotherm.p, self.exp_isotherm.q))))
        new_p_sim, new_q_sim = (list(t) for t in zip(*sorted(zip(self.sim_isotherm.p, self.sim_isotherm.q))))
        if only_exp and not only_sim:
            plt.scatter(new_p_exp, new_q_exp, color='black')
            plt.legend(['Experimental'], frameon=False, loc='lower right')
        elif only_sim and not only_exp:
            plt.plot(new_p_sim, new_q_sim, color='blue')
            plt.legend(['Simulated'], frameon=False, loc='lower right')
        else:
            plt.scatter(new_p_exp, new_q_exp, color='black')
            plt.plot(new_p_sim, new_q_sim, color='blue')
            plt.legend(['Experimental', 'Simulated'], frameon=False, loc='lower right')
        plt.gca().spines['top'].set_visible(False)
        plt.gca().spines['right'].set_visible(False)

        if legend:
            xlabel = input("Enter x-axis label: ")
            ylabel = input("Enter y-axis label: ")
            plt.xlabel(xlabel)
            plt.ylabel(ylabel)
        else:
            plt.xlabel(r'P or C')
            plt.ylabel(r'q')

        fig = plt.gcf()

        plt.show()
        if export:
            name = input('File Name: ')
            if extension == 'png' or extension == 'svg':
                fig.savefig(name + '.' + extension, format=extension, bbox_inches='tight')
            else:
                exit(TypeError('ERROR: Only png or svg supported.'))

        plt.close()

    def error(self):
        error = []

        for i in range(len(self.exp_isotherm.q)):
            error.append(self.exp_isotherm.q[i] - self.sim_isotherm.q[i])

        msg = "List of errors: " + str(error) + "\n"

        print(msg)

    def abs_error(self):
        error = []

        for i in range(len(self.exp_isotherm.q)):
            error.append(abs(self.exp_isotherm.q[i] - self.sim_isotherm.q[i]))

        msg = "List of absulute errors: " + str(error) + "\n"

        print(msg)

    def quadratic_error(self):
        error = []

        for i in range(len(self.exp_isotherm.q)):
            error.append((self.exp_isotherm.q[i] - self.sim_isotherm.q[i]) ** 2)

        msg = "List of quadratic errors: " + str(error) + "\n"

        print(msg)

    def mean_error(self):
        error = []

        for i in range(len(self.exp_isotherm.q)):
            error.append(self.exp_isotherm.q[i] - self.sim_isotherm.q[i])

        msg = "Mean of errors: " + str(np.mean(error)) + "\n"

        print(msg)

    def mean_abs_error(self):
        error = []

        for i in range(len(self.exp_isotherm.q)):
            error.append(abs(self.exp_isotherm.q[i] - self.sim_isotherm.q[i]))

        msg = "Mean of absolute errors: " + str(np.mean(error)) + "\n"

        print(msg)

    def mean_quadratic_error(self):
        error = []

        for i in range(len(self.exp_isotherm.q)):
            error.append((self.exp_isotherm.q[i] - self.sim_isotherm.q[i]) ** 2)

        msg = "Mean of quadratic errors: " + str(np.mean(error)) + "\n"

        print(msg)

    def std_error(self):
        error = []

        for i in range(len(self.exp_isotherm.q)):
            error.append(self.exp_isotherm.q[i] - self.sim_isotherm.q[i])

        msg = "Standard deviation of errors: " + str(np.std(error)) + "\n"

        print(msg)

    def std_abs_error(self):
        error = []

        for i in range(len(self.exp_isotherm.q)):
            error.append(abs(self.exp_isotherm.q[i] - self.sim_isotherm.q[i]))

        msg = "Standard deviation of aboslute errors: " + str(np.std(error)) + "\n"

        print(msg)

    def std_quadratic_error(self):
        error = []

        for i in range(len(self.exp_isotherm.q)):
            error.append((self.exp_isotherm.q[i] - self.sim_isotherm.q[i]) ** 2)

        msg = "Standard deviation of quadratic errors: " + str(np.std(error)) + "\n"

        print(msg)

    def error_all(self):
        print("-----------------------------------")
        self.error()
        self.mean_error()
        self.std_error()

        print("-----------------------------------")

        self.abs_error()
        self.mean_abs_error()
        self.std_abs_error()

        print("-----------------------------------")

        self.quadratic_error()
        self.mean_quadratic_error()
        self.std_quadratic_error()

        print("-----------------------------------")

    def kruskal(self):
        print("-----------------------------------")
        print('Kruskal Wallis Test:')
        kruskal_result = stats.kruskal(self.exp_isotherm.q, self.sim_isotherm.q)
        print("statistic: " + str(kruskal_result[0]))
        print("p-value: " + str(kruskal_result[1]))
        if kruskal_result[1] < 0.05:
            print("There is significant difference between sample medians")
        else:
            print("There is NO significant difference between sample medians")
        print("-----------------------------------")

