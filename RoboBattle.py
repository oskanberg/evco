
import tempfile
import os, stat
from string import whitespace

if 'ROBOCODE_BOTS' in os.environ:
	path_to_evolved_robots = os.environ['ROBOCODE_BOTS']
else:
	path_to_evolved_robots = '/home/oliver/projects/robocode/robots/'

if 'ROBOCODE' in os.environ:
	path_to_robocode	= os.environ['ROBOCODE']
else:
	path_to_robocode	= '/home/oliver/projects/robocode'

class RoboBattle():

	def __init__(self):
		# self.battle(robots)
		pass
	
	def battle(self, robots, rounds=10):
		battle_properties = tempfile.NamedTemporaryFile(delete=False, suffix='.battle')
		battle_properties.write('''#Battle Properties
robocode.battleField.width=800
robocode.battleField.height=600
robocode.battle.numRounds=%d
robocode.battle.gunCoolingRate=0.1
robocode.battle.rules.inactivityTime=450
robocode.battle.hideEnemyNames=true
robocode.battle.selectedRobots=%s''' % (rounds, ','.join(robots)))
		battle_properties.close()

		battle_results = tempfile.NamedTemporaryFile(delete=False)
		battle_results.close()

		st = os.stat(battle_properties.name)
		os.chmod(battle_properties.name, st.st_mode | 0777)
		st = os.stat(battle_results.name)
		os.chmod(battle_results.name, st.st_mode | 0777)
		cmd = [
			"java",
			"-Djava.awt.headless=true",
			"-DROBOTPATH=" + path_to_evolved_robots,
			"-Xmx512M",
			"-Dsun.io.useCanonCaches=false",
			"-cp "+ path_to_robocode +"/libs/robocode.jar robocode.Robocode",
			"-battle " + battle_properties.name,
			"-nodisplay",
			"-nosound",
			"-results " + battle_results.name,
			">/dev/null"
		]

		os.system(' '.join(cmd))
		return self.read_results(battle_results.name)

	def read_results(self, battle_results):
		results = {}
		r_data = []
		with open(battle_results, 'r') as f:
			for line in f:
				r_data.append(line)

		r_data = r_data[2:]
		for tank in r_data:
			tank_data = tank.split('\t')
			tank_name = tank_data[0].split(' ')[1]
			results[tank_name] = {
				'total' : int(tank_data[1].split(' ')[0]),
			}

		return results
