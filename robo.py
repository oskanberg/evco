
from RobotFactory import RobotFactory
from RoboBattle import RoboBattle

import csv
import os, sys
from multiprocessing import Process, Queue
from Robots import SplitRobot, PlainRobot
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

# RECORD_LOCATION = '/usr/userfs/o/ost500/fitness_record.csv'
RECORD_LOCATION = '/home/oliver/fitness_record.csv'
CLEAN = False
POPULATION_SIZE = 20 
# number of bots (excluding tested, hof and sample)
NUM_BOTS_PER_BATTLE = 3
GENOME_SIZE = 800
GENERATIONS = 1
MUTATION_RATE = 0.05
ROUNDS = 5
CROSSOVER_RATE = 0.2
NUM_MOVERS = 3
HALL_OF_FAME = True

rf = RobotFactory()
rb = RoboBattle()

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
	return g1[0:point] + g2[point:len(g2)]

def generate_random_genome(length):
	return [ random.randint(0, 255) for i in xrange(length) ]

def get_genome_fitness_proportionate(population):
	highest = max([ robot.fitness for robot in population.itervalues() ])
	highest = max(highest, 1)
	while True:
		selection = population[random.choice(population.keys())]
		norm_fitness = selection.fitness / float(highest)
		if random.random() < norm_fitness:
			return selection.get_genome()

def get_next_gen_ms(population, generation, rtype):
	pairs = [ (robot.fullname, robot.fitness) for robot in population.itervalues() ]
	highest = max([ p[1] for p in pairs ])
	print rtype
	print 'higest fitness: ', highest
	print 'avg.   fitness: ', sum([ p[1] for p in pairs ]) / len(pairs)
	new_pop = {}
	while len(new_pop) < POPULATION_SIZE:
		new_genome = get_genome_fitness_proportionate(population)
		if CROSSOVER_RATE > 0:
			if random.random() < CROSSOVER_RATE:
				other_parent = new_genome
				# would do this, but there might only be one good
				# while other_parent == new_genome:
				other_parent = get_genome_fitness_proportionate(population)
				new_genome = one_point_crossover(new_genome, other_parent)
		if MUTATION_RATE > 0:
			new_genome = mutate(new_genome)		
		new = SplitRobot(new_genome, rf, rtype)
		new.register(generation)
		new_pop[new.fullname] = new
	return new_pop


hof = []

def get_next_gen(population, generation):
	robots = population.values()
	robots.sort(key=lambda x: x.fitness, reverse=True)
	highest = robots[0].fitness
	print 'higest fitness: ', highest
	print 'avg.   fitness: ', sum([ r.fitness for r in robots ]) / len(robots)
	new_pop = {}
	while len(new_pop) < POPULATION_SIZE:
		new_genome = get_genome_fitness_proportionate(population)
		if CROSSOVER_RATE > 0:
			if random.random() < CROSSOVER_RATE:
				other_parent = new_genome
				# would do this, but there might only be one good
				# while other_parent == new_genome:
				other_parent = get_genome_fitness_proportionate(population)
				new_genome = one_point_crossover(new_genome, other_parent)
		if MUTATION_RATE > 0:
			new_genome = mutate(new_genome)
		new = PlainRobot(new_genome, rf)
		new.register(generation)
		new_pop[new.fullname] = new
	if HALL_OF_FAME and len(hof) > 0:
		random_hofer = random.choice(hof).get_genome()
		new = PlainRobot(random_hofer, rf)
		new.register(generation)
		new_pop[new.fullname] = new
	return new_pop

def record_fitness(population, filename):
	with open(filename, 'a') as f:
		csv_writer = csv.writer(f)
		csv_writer.writerow([ p.fitness for p in population.itervalues() ])

def record_values(values, filename):
	with open(filename, 'a') as f:
		csv_writer = csv.writer(f)
		csv_writer.writerow([ value for value in values ])

def test_robot(robot_fullname, q):
	result = rb.battle([robot_fullname, 'sample.Fire', 'sample.Walls', 'sample.RamFire'], rounds=ROUNDS)
	q.put((robot_fullname, result[robot_fullname]['total']/float(ROUNDS)))

def test_actual_fitness(robot_fullname):
	robots = [robot_fullname, 'squigsoft.SquigBot2_8*']
	return rb.battle(robots, rounds=ROUNDS)[robot_fullname]['total'] / float(ROUNDS)

def coevolve_test(robots, q):
	result = rb.battle(robots, rounds=ROUNDS)
	for robot in robots:
		q.put((robot, result[robot]))

def clean_dir(folder):
	for the_file in os.listdir(folder):
    		file_path = os.path.join(folder, the_file)
    		try:
       			if os.path.isfile(file_path):
            			os.unlink(file_path)
		except Exception,e:
			print e

def single_population_vs_sample():
	population = {}
	#name:obj pairs
	# create starting population
	for i in xrange(POPULATION_SIZE):
		new = PlainRobot(generate_random_genome(GENOME_SIZE), rf)
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

		record_fitness(population, '/usr/userfs/o/ost500/fitness_record.csv')
		clean_dir('/usr/userfs/o/ost500/robocode/robots/sample/evolved')
		clean_dir('/tmp')
		population = get_next_gen(population, generation + 1)
		rf.compile_generation(generation + 1)

def multiprocess_split(movers, shooters):
	processes = []
	q = Queue()
	for robot in shooters.itervalues():
		names = movers.keys()
		random.shuffle(names)
		battle_robots = names[:NUM_MOVERS]
		battle_robots.append(robot.fullname)
		processes.append(Process(target=coevolve_test, args=(battle_robots,q)))
		processes[-1].start()
	for process in processes:
		process.join()
	while not q.empty():
		record = q.get()
		if record[0] in movers.keys():
			movers[record[0]].fitness = record[1]['survival']
		else:
			shooters[record[0]].fitness = record[1]['damage']
	return movers, shooters

def multiprocess_plain(population):
	exclude = []
	processes = []
	q = Queue()
	for robot in population.itervalues():
		names = population.keys()
		random.shuffle(names)
		battle_robots = names[:NUM_BOTS_PER_BATTLE]
		battle_robots.append(robot.fullname)
		battle_robots.append('sample.Fire')
		exclude.append('sample.Fire')
		processes.append(Process(target=coevolve_test, args=(battle_robots,q)))
		processes[-1].start()
	for process in processes:
		process.join()
	while not q.empty():
		record = q.get()
		if record[0] not in exclude:
			population[record[0]].fitness += record[1]['total']
			population[record[0]].battles_fought += 1

def coevolve_movers_shooters():
	# name:obj pairs
	movers = {}
	shooters = {}

	# create starting population
	for i in xrange(int(POPULATION_SIZE/2)):
		new = SplitRobot(generate_random_genome(GENOME_SIZE), rf, 'mover')
		new.register(0)
		movers[new.fullname] = new

	for i in xrange(int(POPULATION_SIZE/2)):
		new = SplitRobot(generate_random_genome(GENOME_SIZE), rf, 'shooter')
		new.register(0)
		shooters[new.fullname] = new

	rf.compile_generation(0)

	for generation in xrange(GENERATIONS):
		movers, shooters = multiprocess_split(movers, shooters)

		print 'MOVERS:'
		for robot in movers.itervalues():
			print robot.fullname + " : " + str(robot.fitness)
		print 'SHOOTERS:'
		for robot in shooters.itervalues():
			print robot.fullname + " : " + str(robot.fitness)

		population = movers.copy()
		population.update(shooters)
		record_fitness(population, RECORD_LOCATION)
		if CLEAN:
			clean_dir('/usr/userfs/o/ost500/robocode/robots/sample/evolved')
			clean_dir('/tmp')
		movers = get_next_gen_ms(movers, generation + 1, 'mover')
		shooters = get_next_gen_ms(shooters, generation + 1, 'shooter')
		rf.compile_generation(generation + 1)

def coevolve_plain():
	population = {}
	for i in xrange(POPULATION_SIZE):
		new = PlainRobot(generate_random_genome(GENOME_SIZE), rf)
		new.register(0)
		population[new.fullname] = new

	rf.compile_generation(0)

	for generation in xrange(GENERATIONS):
		multiprocess_plain(population)
		for robot in population.itervalues():
			robot.fitness = robot.fitness / float(robot.battles_fought)
			print robot.fullname + ' : ' + str(robot.fitness) + ' (' + str(robot.battles_fought) + ' battles)'
		
		robots = population.values()
		robots.sort(key=lambda x: x.fitness, reverse=True)
		
		robots[0].actual_fitness = test_actual_fitness(robots[0].fullname)
		print 'actual fitness of ' + robots[0].fullname + ' : ' + str(robots[0].actual_fitness)
		# hall of fame 
		if HALL_OF_FAME:
			if len(hof) > 5:
				# smallest first
				if robots[0].actual_fitness > hof[0].actual_fitness:
					hof[0] = robots[0]
					hof.sort(key=lambda x: x.fitness)
			else:
				# add the best
				hof.append(robots[0])

			print 'Hall of Fame'
			for r in hof:
				print r.fullname + ' : ' + str(r.fitness)

		record_values([robots[0].actual_fitness], '/home/oliver/best_actual.csv')
		record_fitness(population, RECORD_LOCATION)
		if CLEAN:
			clean_dir('/usr/userfs/o/ost500/robocode/robots/sample/evolved')
			clean_dir('/tmp')
		population = get_next_gen(population, generation + 1)
		rf.compile_generation(generation + 1)

	record_values([r.get_genome() for r in hof], '/home/oliver/hof.csv')

if HALL_OF_FAME and CLEAN:
	print "YOU CAN'T HAVE BOTH HALL OF FAME AND CLEAN"

coevolve_plain()