from GramGen import GramGen
from RobotFactory import RobotFactory
from RoboBattle import RoboBattle

import csv

from multiprocessing import Process, Queue
import random


LAME_DERIVATION = """package sample.evolved;\n
    import robocode.*;\n
    public class ##name## extends AdvancedRobot{\n
    public void run() {\n
		while (true) {\n
			execute();\n
		}\n
	}\n
	public void onScannedRobot(ScannedRobotEvent e) {\n
		fire(1);\n
	}\n
	public void onHitByBullet(HitByBulletEvent e) { }\n
	public void onHitRobot(HitRobotEvent e) { }\n
	public void onHitWall(HitWallEvent e) { }\n
}"""

# NUM_PROCESSES = 4
POPULATION_SIZE = 20
GENOME_SIZE = 800
GENERATIONS = 50
MUTATION_RATE = 0.05
ROUNDS = 5

generator = GramGen('robogram.json')
rf = RobotFactory()
rb = RoboBattle()

class Robot:

	fitness = 0
	genome = ''
	name = ''
	fullname = ''
	lame = False

	def __init__(self, genome):
		self.genome = genome
		self.fitness = 0
		self.name = ''
		self.fullname = ''
		self.lame = False

	def register(self, generation):
		derivation = generator.generate_from_seq(self.genome)
		if len(derivation) == 0:
			# derivation failed
			self.lame = True
			derivation = LAME_DERIVATION
		self.name = rf.add_robot(derivation, generation)
		self.fullname = 'sample.evolved.' + self.name

def mutate(genome):
	genome = genome[:]
	for i, gene in enumerate(genome):
		if random.random() < MUTATION_RATE:
			genome[i] = random.randint(0, 255)
	return genome

def one_point_crossover(g1, g2):
	g1 = g1[:]
	g2 = g2[:]
	point = random.randint(0, len(g1) - 1)
	new = g1[0:point].append(g2[point:len(g2)])
	assert len(new) == len(g1), 'crossover genome is not the same size'
	return new

def generate_random_genome(length):
	return [ random.randint(0, 255) for i in xrange(length) ]

def get_next_gen(population, generation):
	pairs = [ (robot.fullname, robot.fitness) for robot in population.itervalues() ]
	highest = max([ p[1] for p in pairs ])
	print 'higest fitness: ', highest
	print 'avg.   fitness: ', sum([ p[1] for p in pairs ]) / len(pairs)
	new_pop = {}
	while len(new_pop) < POPULATION_SIZE:
		selection = population[random.choice(population.keys())]
		norm_fitness = selection.fitness / float(highest)
		if random.random() < norm_fitness:
			new = Robot(mutate(selection.genome))
			new.register(generation)
			new_pop[new.fullname] = new
	return new_pop

def record_fitness(population, filename):
	with open(filename, 'a') as f:
		csv_writer = csv.writer(f)
		csv_writer.writerow([ p.fitness for p in population.itervalues() ])

def test_robot(robot_fullname, q):
	result = rb.battle([robot_fullname, 'sample.Fire', 'sample.Walls', 'sample.RamFire'], rounds=ROUNDS)
	q.put((robot_fullname, result[robot_fullname]['total']/float(ROUNDS)))

population = {}
#name:obj pairs
# create starting population
for i in xrange(POPULATION_SIZE):
	new = Robot(generate_random_genome(GENOME_SIZE))
	new.register(0)
	population[new.fullname] = new

rf.compile_generation(0)

for generation in xrange(GENERATIONS):	
	processes = []
	q = Queue()
	for robot in population.itervalues():
		if robot.lame:
			robot.fitness = 0
			continue
		processes.append(Process(target=test_robot, args=(robot.fullname,q)))
		processes[-1].start()
	for process in processes:
		process.join()
	while not q.empty():
		record = q.get()
		population[record[0]].fitness = record[1]
	for robot in population.itervalues():
		print robot.fullname + " : " + str(robot.fitness)

	record_fitness(population, '/tmp/fitness_record.csv')
	population = get_next_gen(population, generation + 1)
	rf.compile_generation(generation + 1)
