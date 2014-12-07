#!/usr/bin/python

import random
import re
import json

class GramGen():

	derivation_table = {}

	def __init__(self, json_file):
		json_string = ''
		with open(json_file, 'r') as f:
			j_str = f.read().replace('\n', '').replace('\r', '').replace('\t', '    ')
			# print j_str[2195:2200]
			self.derivation_table = json.loads(j_str)

	def _get_unresolved(self, derivation):
		return re.findall('<([a-zA-Z-_]+)>', derivation)

	def generate_random(self):
		# always start with 'main'
		derivation = '<main>'
		unresolved = self._get_unresolved(derivation)
		while len(unresolved) > 0:
			options = self.derivation_table[unresolved[0]]
			chosen = options[random.randint(0, len(options) - 1)]
			derivation = derivation.replace('<' + unresolved[0] + '>', chosen, 1)
			unresolved = self._get_unresolved(derivation)

		return derivation

	def generate_from_seq(self, sequence, iteration_limit):
		sequence = sequence[:]
		i = 0

		# always start with 'main'
		derivation = '<main>'
		unresolved = self._get_unresolved(derivation)
		while len(unresolved) > 0:
			options = self.derivation_table[unresolved[0]]
			chosen = options[sequence[i % len(sequence)] % len(options)]
			i += 1
			derivation = derivation.replace('<' + unresolved[0] + '>', chosen, 1)
			unresolved = self._get_unresolved(derivation)
			if i > iteration_limit:
				print 'derivation exceeded limit'
				return ''
		return derivation