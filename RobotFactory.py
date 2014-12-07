
import subprocess
import re
import os
# import glob

if 'ROBOCODE_EVOLVED_BOTS' in os.environ:
        path_to_evolved_robots = os.environ['ROBOCODE_EVOLVED_BOTS']
else:
        path_to_evolved_robots = '/home/oliver/projects/robocode/robots/sample/evolved'

if 'ROBOCODE' in os.environ:
        path_to_robocode        = os.environ['ROBOCODE']
else:
        path_to_robocode        = '/home/oliver/projects/robocode'


class RobotFactory:

	num_robots = 0

	def __init__(self):
		self.num_robots = 0
		pass

	def add_robot(self, source, generation):
		robot_name = 'gen' + str(generation) + '_' + str(self.num_robots)
		source = source.replace('##name##', robot_name)
		source = self.check_for_overflow(source)
		java_path = path_to_evolved_robots + '/' + robot_name + '.java'
		with open(java_path,'w') as f:
			f.write(source)

		properties_path = path_to_evolved_robots + '/' + robot_name + '.properties'
		with open(properties_path, 'w') as f:
			f.write("""#Robot Properties
robot.description=Evolved using magic
robot.webpage=
robocode.version=1.1.2
robot.java.source.included=true
robot.author.name=magic
robot.classname=sample.evolved.%s
robot.name=%s""" % (robot_name, robot_name)
			)
		self.num_robots += 1
		return robot_name
	

	def check_for_overflow(self, source):
		# replace large numbers
		return re.sub(r'[\d]{6}', '1', source)

	def compile_generation(self, generation):
		cmd = [
			"javac",
			"-classpath",
			path_to_robocode + "/libs/robocode.jar",
			path_to_evolved_robots + "/gen" + str(generation) + "_*.java"
		]
		os.system(' '.join(cmd))

