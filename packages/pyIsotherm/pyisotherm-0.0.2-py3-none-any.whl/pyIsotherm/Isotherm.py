import matplotlib.pyplot as plt


class Isotherm:
    p = list
    q = list

    def __init__(self, p, q):

        try:
            if all(isinstance(n, (float, int)) for n in p) and all(isinstance(n, (float, int)) for n in q):
                if len(p) == len(q):
                    self.p = p
                    self.q = q
                else:
                    exit(ValueError('ERROR: p and q must have same length'))
            else:
                exit(TypeError('ERROR: p and q must be lists of floats'))
        except TypeError:
            exit(TypeError('ERROR: p and q must be lists of floats'))

    def plot(self):
        plt.scatter(self.p, self.q)
        plt.show()
