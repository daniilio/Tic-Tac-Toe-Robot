import lib.trajectory_lib as ttr
import time
import lib.targets_joint as targets_joint


if __name__ == "__main__":
    robot, rtb_model = ttr.new_robot()

    # First, we need to be in the ready position that the saved trajectories expect
    q_target = rtb_model.qr
    ttr.joint_trajectory(robot, q_target)

    # Then, go to drawing mode
    q_target = targets_joint.DRAWING_MODE
    ttr.joint_trajectory(robot, q_target, "READY_to_DRAWING_MODE", save=True)

    time.sleep(5)

    # Then, back to ready mode
    q_target = rtb_model.qr
    ttr.joint_trajectory(robot, q_target)