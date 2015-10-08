import logging; logger = logging.getLogger("morse." + __name__)
from morse.core import blenderapi
from morse.robots.grasping_robot import GraspingRobot
from morse.core.services import service

class Human(GraspingRobot):
    """ Class definition for the human as a robot entity.

    Sub class of GraspingRobot.
    """

    def __init__(self, obj, parent=None):
        """ Call the constructor of the parent class """
        logger.info('%s initialization' % obj.name)
        GraspingRobot.__init__(self, obj, parent)

        # We define here the name of the human grasping hand:
        #self.hand_name = 'Hand_Grab.R'

        armatures = blenderapi.get_armatures(self.bge_object)
        if len(armatures) == 0:
            logger.error("The human <%s> has not armature. Something is wrong!" % obj.name)
            return
        if len(armatures) > 1:
            logger.warning("The human <%s> has more than one armature. Using the first one" % obj.name)

        self.armature = armatures[0]

        logger.info('Component initialized')


    def apply_speed(self, kind, linear_speed, angular_speed):
        """
        Apply speed parameter to the human.
        
        This overloaded version of Robot.apply_speed manage the walk/rest
        animations of the human avatar.

        :param string kind: the kind of control to apply. Can be one of
        ['Position', 'Velocity'].
        :param list linear_speed: the list of linear speed to apply, for
        each axis, in m/s.
        :param list angular_speed: the list of angular speed to apply,
        for each axis, in rad/s.
        """

        parent = self.bge_object

        # TODO: adjust this value depending on linear_speed to avoid 'slipping'
        speed_factor = 1.0

        # start/end frames of walk cycle in human_rig.blend
        # TODO: get that automatically from the timeline?
        WALK_START_FRAME = 9
        WALK_END_FRAME = 32

        logger.warning("Applying speed " + str(linear_speed))
        if linear_speed[0] != 0 or angular_speed[2] != 0:
            self.armature.playAction("walk", 
                                     WALK_START_FRAME, WALK_END_FRAME, 
                                     speed=speed_factor)
        else:
            self.armature.playAction("walk", 
                                     WALK_START_FRAME, WALK_START_FRAME)


        if kind == 'Position':
            parent.applyMovement(linear_speed, True)
            parent.applyRotation(angular_speed, True)
        else:
            logger.error("Only the control type 'Position' is currently supported "
                         "by the human avatar")

#        elif kind == 'Velocity':
#            if self._is_ground_robot:
#                """
#                A ground robot cannot control its vz not rx, ry speed in
#                the world frame. So convert {linear, angular}_speed in
#                world frame, remove uncontrolable part and then pass it
#                against in the robot frame"""
#                linear_speed = mathutils.Vector(linear_speed)
#                angular_speed = mathutils.Vector(angular_speed)
#                linear_speed.rotate(parent.worldOrientation)
#                angular_speed.rotate(parent.worldOrientation)
#                linear_speed[2] = parent.worldLinearVelocity[2]
#                angular_speed[0] = parent.worldAngularVelocity[0]
#                angular_speed[1] = parent.worldAngularVelocity[1]
#                linear_speed.rotate(parent.worldOrientation.transposed())
#                angular_speed.rotate(parent.worldOrientation.transposed())
#
#            # Workaround against 'strange behaviour' for robot with
#            # 'Dynamic' Physics Controller. [0.0, 0.0, 0.0] seems to be
#            # considered in a special way, i.e. is basically ignored.
#            # Setting it to 1e-6 instead of 0.0 seems to do the trick!
#            if angular_speed == [0.0, 0.0, 0.0]:
#                angular_speed = [0.0, 0.0, 1e-6]
#            parent.setLinearVelocity(linear_speed, True)
#            parent.setAngularVelocity(angular_speed, True)

#    @service
#    def move(self, speed, rotation):
#        """ Move the human. """
#
#        human = self.bge_object
#
#        if not human['Manipulate']:
#            human.applyMovement( [speed,0,0], True )
#            human.applyRotation( [0,0,rotation], True )
#        else:
#            scene = blenderapi.scene()
#            target = scene.objects['IK_Target_Empty.R']
#
#            target.applyMovement([0.0, rotation, 0.0], True)
#            target.applyMovement([0.0, 0.0, -speed], True)
#
#    @service
#    def move_head(self, pan, tilt):
#        """ Move the human head. """
#
#        human = self.bge_object
#        scene = blenderapi.scene()
#        target = scene.objects['Target_Empty']
#
#        if human['Manipulate']:
#            return
#
#        target.applyMovement([0.0, pan, 0.0], True)
#        target.applyMovement([0.0, 0.0, tilt], True)
#
#    @service
#    def move_hand(self, diff, tilt):
#        """ Move the human hand (wheel).
#
#        A request to use by a socket.
#        Done for wiimote remote control.
#        """
#
#        human = self.bge_object
#        if human['Manipulate']:
#            scene = blenderapi.scene()
#            target = scene.objects['IK_Target_Empty.R']
#            target.applyMovement([diff, 0.0, 0.0], True)  
#        
#    @service
#    def toggle_manipulation(self):
#        """ Change from and to manipulation mode.
#
#        A request to use by a socket.
#        Done for wiimote remote control.
#        """
#
#        human = self.bge_object
#        scene = blenderapi.scene()
#        hand_target = scene.objects['IK_Target_Empty.R']
#        head_target = scene.objects['Target_Empty']
#
#        if human['Manipulate']:
#            human['Manipulate'] = False
#            # Place the hand beside the body
#            hand_target.localPosition = [0.0, -0.3, 0.8]
#            head_target.setParent(human)
#            head_target.localPosition = [1.3, 0.0, 1.7]
#        else:
#            human['Manipulate'] = True
#            head_target.setParent(hand_target)
#            # Place the hand in a nice position
#            hand_target.localPosition = [0.6, 0.0, 1.4]
#            # Place the head in the same place
#            head_target.localPosition = [0.0, 0.0, 0.0]
#
    def default_action(self):
        """ Main function of this component. """
        pass
