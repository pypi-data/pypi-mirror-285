import pyIsotherm as iso

terma = iso.Isotherm([1,2,3,4,5,6,7,8,9,10], [1,2,3,4,5,6,7,8,9,10])

result = iso.estimate(terma.p, terma.q, 'langmuir')

print("Teste cores")

