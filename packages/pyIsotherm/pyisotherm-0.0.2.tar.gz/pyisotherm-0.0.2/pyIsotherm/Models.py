import numpy as np

def call_model(q_func):
    q_obj = None

    match q_func:
        case "langmuir":
            q_obj = __langmuir_q__
        case "sips":
            q_obj = __sips_q__
        case "toth":
            q_obj = __toth_q__
        case "gab":
            q_obj = __gab_q__
        case "bet":
            q_obj = __bet_q__
        case "modifiedbet":
            q_obj = __modified_bet_q__
        case "multisite":
            q_obj = __langmuir_multi_q__
        case _:
            exit(ValueError("ERROR: Unknown model was given."))

    return q_obj


#################### Langmuir ####################
def obj_func(p, qe, param, q_func, relative=False):

    q_obj = call_model(q_func)

    result = 0
    for i in range(len(p)):
        try:
            np.seterr(all='ignore')
            value = q_obj(p[i], param)
            if relative:
                result = result + abs((qe[i] - value) / qe[i]) ** 2
            else:
                result = result + abs(qe[i] - value) ** 2
        except ValueError or TypeError or IndexError or ZeroDivisionError:
            result = result + 1e8
    return result


def __langmuir_q__(press, param):
    q_max = param[0]
    b = param[1]
    return q_max * b * press / (1 + b * press)


#################### Sips ##################


def __sips_q__(press, param):
    q_max = param[0]
    b = param[1]
    nS = param[2]
    return (q_max * (b * press) ** (1 / nS)) / (1 + (b * press) ** (1 / nS))


#################### Toth ####################



def __toth_q__(p, param):
    q_max = param[0]
    b = param[1]
    n = param[2]
    over = q_max * b * p
    under = (1 + (b * p) ** n) ** (1 / n)
    result = over / under
    return result


#################### BET ####################



def __bet_q__(p, param):
    qm = param[0]
    C = param[1]
    over = qm * C * p
    under = (1 - p) * (1 - p + C * p)
    result = over / under
    return result


#################### gab ####################
def __gab_q__(p, param):
    qm = param[0]
    C = param[1]
    K = param[2]
    np.seterr(all='ignore')
    over = qm * C * K * p
    under = (1 - K * p) * (1 - K * p + C * K * p)
    result = over / under
    return result


#################### Multisite Langmuir ####################
def f_langmuir_multi(p, q, param):
    q_max = param[0]
    b = param[1]
    a = param[2]
    return q - q_max * b * p * ((1 - (q / q_max)) ** a)


def f_prime_langmuir(p, q, param):
    q_max = param[0]
    b = param[1]
    a = param[2]

    return 1 + b * p * ((1 - q / q_max) ** a) * a / (1 - q / q_max)


def newton(p, q, param):
    for i in range(15):
        try:
            newq = q - f_langmuir_multi(p, q, param) / f_prime_langmuir(p, q, param)
            if abs(q - newq) < 1e-5:
                return newq
            q = newq
        except ValueError or TypeError or IndexError or ZeroDivisionError:
            return 1e8
    return q


def __langmuir_multi_q__(p, param):
    q = 0.5
    for i in range(20):
        try:
            newq = q - f_langmuir_multi(p, q, param) / f_prime_langmuir(p, q, param)
            if abs(q - newq) < 1e-5:
                return newq
            q = newq
        except TypeError or ValueError:
            return 0
    return q


#################### Modified BET####################
def __modified_bet_q__(p, param):
    qm = param[0]
    C = param[1]
    m = param[2]
    over = qm * C * p
    under = ((1 - p)**m) * (1 + C * p)
    result = over / under
    return result

