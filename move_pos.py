import csc376_bind_franky
from franka_api.motion_generator import RuckigMotionGenerator
import roboticstoolbox as rtb
import targets_joint

TARGET_JOINTS = targets_joint.CAMERA_MODE

motion_generator = RuckigMotionGenerator()
rtb_model = rtb.models.Panda()
robot = csc376_bind_franky.FrankaJointTrajectoryController("192.168.1.107")
robot.setupSignalHandler()

q_start = robot.get_current_joint_positions()
q_traj, dt = motion_generator.calculate_joint_pose_trajectory(
    q_start,
    TARGET_JOINTS,
    relative_vel_factor=0.2,
    relative_acc_factor=0.1,
    relative_jerk_factor=0.5,
)


def trajectory_callback(index):
    print(f"At trajectory index: {index}")
    print(f"Commanding joint positions: {q_traj[index]}")


robot.set_trajectory_callback(trajectory_callback)
robot.run_joint_trajectory(q_traj, dt)
