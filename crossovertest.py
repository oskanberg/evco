
import random

def one_point_crossover(g1, g2):
	g1 = g1[:]
	g2 = g2[:]
	point = random.randint(0, len(g1) - 1)
	return g1[0:point] + g2[point:len(g2)]
