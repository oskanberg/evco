
from GramGen import GramGen

class Robot:

	fitness = 0
	genome = ''
	name = ''
	fullname = ''
	lame = False

	def __init__(self, genome, robot_factory, rtype):
		seg = len(genome) / 3
		self.move_genome = genome[:seg]
		self.shoot_genome = genome[seg:seg*2]
		self.scan_genome = genome[seg*2:]
		self.fitness = 0
		self.name = ''
		self.fullname = ''
		self.lame = False
		self.rf = robot_factory
		self.rtype = rtype

		self.move_gen = GramGen('move.json')
		self.shoot_gen = GramGen('shoot.json')
		self.scan_gen = GramGen('scanned.json')
			

	def register(self, generation):
		if self.rtype == 'mover':
			derivation = self.move_gen.generate_from_seq(self.move_genome)
		elif self.rtype == 'shooter':
			derivation = self.shoot_gen.generate_from_seq(self.shoot_genome)
			derivation += self.scan_gen.generate_from_seq(self.scan_genome)
		if len(derivation) == 0:
			# derivation failed
			self.lame = True
			derivation = LAME_DERIVATION
			self.fitness = 0
		self.name = self.rf.add_robot(derivation, generation)
		self.fullname = 'sample.evolved.' + self.name

	def get_genome(self):
		return self.move_genome + self.shoot_genome + self.scan_genome