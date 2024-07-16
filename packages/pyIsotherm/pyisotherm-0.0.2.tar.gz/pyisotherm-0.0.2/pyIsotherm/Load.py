import csv
import pandas as pd
from pyIsotherm.Isotherm import Isotherm


def load(path, p0=1, nist_csv=False):
    isotherm = Isotherm([], [])

    try:
        if nist_csv:
            if not path.endswith('.csv'):
                exit(TypeError("ERROR: The file extension must be .csv if nist_csv is True"))
            with open(path, 'r') as file:
                csv_reader = csv.reader(file)
                next(csv_reader)
                for column in csv_reader:
                    try:
                        if column[0].split(",")[0] == 'pressure':
                            isotherm.p.append(float(column[1].split(",")[0])/p0)
                        if column[0].split(",")[0] == 'adsorption':
                            isotherm.q.append(float(column[1].split(",")[0]))
                    except IndexError or ValueError or TypeError:
                        pass
            return isotherm
        else:
            if not path.endswith('.xlsx'):
                exit(TypeError("ERROR: The file extension must be .xlsx if nist_csv is False"))
            file = pd.read_excel(path, usecols='A,B')
            if file.columns[0] != 'A' or file.columns[1] != 'B':
                exit(ValueError("ERROR: The input file must have columns A,B"))
            else:
                isotherm.p = file[str(file.columns[0])].tolist()
                isotherm.q = file[str(file.columns[1])].tolist()
            return isotherm
    except FileNotFoundError:
        exit(FileNotFoundError("ERROR: File not found"))



