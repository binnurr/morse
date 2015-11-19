__author__ = 'fl'

from morse.builder import *

# Import the human model.
human = Human()
human.properties(Animations=False)
human.add_interface("ros")

#motion = Waypoint()
#motion.properties(ControlType="Position")
#human.append(motion)
#motion.add_stream('ros')

# Use the standard environment 'indoor-1.blend'. You could use any other.
env = Environment('sandbox')
