import csc376_bind_franky
robot = csc376_bind_franky.FrankaJointTrajectoryController("192.168.1.107")
robot.setupSignalHandler()
q_start = robot.get_current_joint_positions()
print(q_start)