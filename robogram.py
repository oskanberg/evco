# encoding: utf-8

def grammar():
  return {
    # The body of the tank class.
    'main' : ['''

      // This is run in its own thread and is responsible for performing
      // the majority of the actions of simpler tanks.

      public void run() {

        // You could perform some initialisation on your
        // tank here, such as setting each of its colours.
        while (true) {

          <m_run>

          // This statement executes all of the actions at once.
          // Without it, the robot would never do anything!
          execute();
        }

      }

      // This method is called when a robot is spotted by the radar.
      public void onScannedRobot(ScannedRobotEvent e) {
        fire(1);
      }

      // This method is called when the robot is hit by a bullet.
      //public void onHitByBullet(HitByBulletEvent e) { }

      // This method is called when the robot hits another.
      //public void onHitRobot(HitRobotEvent e) { }

      // This method is called when the robot bumps into a wall.
      //public void onHitWall(HitWallEvent e) { }
    '''],

    # Literal information.
    'nz_digit' : ['1', '2', '3', '4', '5', '6', '7', '8', '9'],
    'digit' : ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9'],
    'fractional' : ['<digit>', '<digit><digit>'],
    'literal_boolean' : ['true', 'false'],
    'literal_int' : ['<nz_digit><literal_int>', '<digit>'],
    'literal_float' : ['<literal_int>.<fractional>'],

    # Returns an integer.
    'int' : [
      '<literal_int>',
      'getNumRounds()',
      'getNumSentries()',
      'getOthers()',
      'Math.round(<float>)'
    ],

    # Returns a floating point.
    'float' : [
      '<literal_float>',
      'getX()',
      'getY()',
      'getVelocity()',
      'getHeight()',
      'getHeading()',
      'getEnergy()',
      'getGunHeading()',
      'getGunCoolingRate()',
      'getBattleFieldHeight()',
      'getBattleFieldWidth()',
      'getGunHeat()',
      'getRadarHeading()',
      'getTime()',
      '(float) <int>'
    ],

    # Returns a numeric type.
    'numeric' : ['<float>', '<int>'],

    # Returns a boolean.
    'expression_boolean' : [
      '<expression_boolean_term>'
    ],
    'expression_boolean_term' : [
      '<numeric> == <numeric>',
      '<numeric> != <numeric>',
      '<numeric> > <numeric>',
      '<numeric> >= <numeric>',
      '<numeric> < <numeric>',
      '<numeric> <= <numeric>'
    ],
    'bool' : [
      '<literal_boolean>',
      '<expression_boolean>'
    ],

    # Composes a series of statements.
    'statements' : [
      '<statement> <statements>',
      '<statement>'
    ],
    'statement' : [
      '''if (<bool>) {
        <statements>
      }
      else {
        <statements>
      }''',
      '<action>;'
    ],
    # Robocode tank actions.
    'action' : [
      'setAhead(<float>)',
      'setBack(<float>)',
      'setStop()',
      'setResume()',
      'setTurnRight(<float>)',
      'setTurnLeft(<float>)',
      'setTurnGunLeft(<float>)',
      'setTurnGunRight(<float>)',
      'setTurnRadarLeft(<float>)',
      'setTurnRadarLeft(<float>)',
      'setAdjustGunForRobotTurn(<bool>)',
      'setAdjustRadarForRobotTurn(<bool>)',
      'setAdjustRadarForGunTurn(<bool>)',
      'fire(<float>)'
    ],
    # The body of the while loop in the "run" method.
    'm_run' : ['<statements>'],
  }
