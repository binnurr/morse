from sensor_msgs.msg import JointState
from morse.middleware.sockets.jointstate import fill_missing_pr2_joints
from morse.middleware.ros import ROSPublisher

class JointStatePublisher(ROSPublisher):
    """ Publish the data of the posture sensor. """
    ros_class = JointState

    def default(self, ci='unused'):
        js = JointState()
        js.header = self.get_ros_header()

        # collect name and positions of jointstates from sensor
        if type(list(self.data.values())[1]) is float:
            js.name = list(self.data.keys())[1:]
            js.position = list(self.data.values())[1:]
            #print (list(self.data.values()))
        elif type(list(self.data.values())[1]) is tuple:
            #print ('I ma in her')
            joint_list = list(self.data.keys())[1:]
            joint_positions = list(self.data.values())[1:]
            for joint,rot in zip(joint_list,joint_positions):
                joint_x = joint + '_x'
                joint_y = joint + '_y'
                joint_z = joint + '_z'
                rot_x = rot[0];
                rot_y = rot[1];
                rot_z = rot[2];
                js.name.append(joint_x)
                js.position.append(rot_x)
                js.name.append(joint_y)
                js.position.append(rot_y)
                js.name.append(joint_z)
                js.position.append(rot_z)
        # for now leaving out velocity and effort
        #js.velocity = [1, 1, 1, 1, 1, 1, 1]
        #js.effort = [50, 50, 50, 50, 50, 50, 50]

        self.publish(js)


class JointStatePR2Publisher(ROSPublisher):
    """ Publish the data of the posture sensor after filling missing PR2 joints. """
    ros_class = JointState

    def default(self, ci='unused'):
        js = JointState()
        js.header = self.get_ros_header()

        joints =  fill_missing_pr2_joints(self.data)
        del joints['timestamp']
        js.name = joints.keys()
        js.position = joints.values()

        self.publish(js)
