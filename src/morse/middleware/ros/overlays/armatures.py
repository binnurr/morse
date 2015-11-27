from morse.middleware.ros_request_manager import ros_action
from morse.core.services import interruptible
from morse.core.overlay import MorseOverlay
from morse.core import status
from morse.core.exceptions import MorseServiceError
from collections import OrderedDict

import logging; logger = logging.getLogger("morse."+ __name__)

import rospy # to set the parameters

from control_msgs.msg import JointTrajectoryAction

class ArmatureController(MorseOverlay):
    """
    This overlay provides a ROS JointTrajectoryAction interface to armatures.
 
    It is meant to be applied on a Armature actuator.
 
    Besides the ROS action server, it also sets a ROS parameter with the list of
    joints.
    """

    def __init__(self, overlaid_object, namespace = None):
        # Call the constructor of the parent class
        MorseOverlay.__init__(self, overlaid_object)

        joints = list(overlaid_object.local_data.keys())

        self.namespace = namespace

        name = self.name().replace(".", "/")

        rospy.set_param(name + "/joints", joints)
        rospy.set_param(name + "/joint_trajectory_action/joints", joints)

    def _stamp_to_secs(self, stamp):
        return stamp.secs + stamp.nsecs / 1e9

    def joint_trajectory_action_result(self, result):
        return result

    def name(self):

        if self.namespace:
            return self.namespace
        else:
            return MorseOverlay.name(self)

    @interruptible
    @ros_action(type = JointTrajectoryAction)
    def joint_trajectory_action(self, req):

        # Fill a MORSE trajectory structure from ROS JointTrajectory
        traj = {}

        req = req.trajectory
        traj["starttime"] = self._stamp_to_secs(req.header.stamp)

        #joint_names = req.joint_names
        joint_names = []
        virtual_joints = False
        for joint in req.joint_names:
            splitted_name = joint.rsplit('_',1)
            if len(splitted_name) == 2:
                joint_name = splitted_name[0]
                rot_axis = splitted_name[1]
                if rot_axis == 'x' or rot_axis == 'y' or rot_axis == 'z':
                    virtual_joints = True 
                    if not joint_name in joint_names:
                        joint_names.append(joint_name)
                else:
                    joint_names.append(joint)
            else:
                joint_names.append(joint)
        
        target_joints = self.overlaid_object.local_data.keys()
        diff = set(joint_names).difference(set(target_joints))

        if diff:
            raise MorseServiceError("Trajectory contains unknown joints! %s" % diff)

        points = []
        for p in req.points:
            point = {}

            # Re-order joint values to match the local_data order
            if virtual_joints:
               
                positions = OrderedDict.fromkeys(joint_names,(0.0,0.0,0.0))
                for index,joint in enumerate(req.joint_names):
                    splitted_name = joint.rsplit('_',1)
                    if len(splitted_name) == 2:
                        joint_name = splitted_name[0]
                        rot_axis = splitted_name[1]
                        if rot_axis == 'x':
                            temp = list(positions[joint_name])
                            temp[0] = p.positions[index]
                            positions[joint_name] = tuple(temp)
                        elif rot_axis == 'y':
                            temp = list(positions[joint_name])
                            temp[1] = p.positions[index]
                            positions[joint_name] = tuple(temp) 
                        elif rot_axis == 'z': 
                            temp = list(positions[joint_name])
                            temp[2] = p.positions[index]
                            positions[joint_name] = tuple(temp)
                        else:
                            positions[joint] = (p.positions[index],0.0,0.0)
                    else:
                        positions[joint] = (p.positions[index],0.0,0.0)
                point_list = []
                for joint in target_joints:
                    point_list.append(positions[joint])
                point["positions"] = point_list
                point["time_from_start"] = self._stamp_to_secs(p.time_from_start)
                points.append(point)    
                
            else:
                pos = dict(zip(joint_names, p.positions))
                point["positions"] = [pos[j] for j in target_joints if j in pos]
                vel = dict(zip(joint_names, p.velocities))
                point["velocities"] = [vel[j] for j in target_joints if j in vel]
    
                acc = dict(zip(joint_names, p.accelerations))
                point["accelerations"] = [acc[j] for j in target_joints if j in acc]
    
                point["time_from_start"] = self._stamp_to_secs(p.time_from_start)
                points.append(point)

        traj["points"] = points
        logger.info(traj)
        print("Ros overlay!")
        self.overlaid_object.trajectory(
                self.chain_callback(self.joint_trajectory_action_result),
                traj)

