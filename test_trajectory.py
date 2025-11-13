import roboticstoolbox as rtb
import time
import sys

from franka_api.motion_generator import RuckigMotionGenerator
import numpy as np
import targets

def new_robot(is_simulation=True):
    np.set_printoptions(precision=4, suppress=True,)    

    panda_rtb_model = rtb.models.Panda()

    if is_simulation:
        from franka_api.visualizer import RtbVisualizer
        robot = RtbVisualizer(panda_rtb_model, panda_rtb_model.qr)
    # else:
    #     import csc376_bind_franky
    #     robot = csc376_bind_franky.FrankaJointTrajectoryController("192.168.1.107")
    #     robot.setupSignalHandler()
    #     q_start = robot.get_current_joint_positions()

    return robot, panda_rtb_model


def compute_trajectories(rtb_model, target_func):
    relative_vel_factor = 0.08
    relative_acc_factor = 0.04
    relative_jerk_factor = 0.2

    motion_generator = RuckigMotionGenerator()
    
    q_start = rtb_model.qr
    se3_start = rtb_model.fkine(q_start)
    se3_targets = target_func(se3_start)
    
    # Calculate trajectories
    start_time = time.time()
    q_trajs = []
    se3_current = se3_start
    q_current = q_start
    for se3_target in se3_targets:
        cartesian_traj, dt = motion_generator.calculate_cartesian_pose_trajectory(se3_current, se3_target,
                                                                                  relative_vel_factor, relative_acc_factor, relative_jerk_factor) 
        q_traj = motion_generator.cartesian_pose_to_joint_trajectory(rtb_model, q_current, cartesian_traj)
        q_trajs.append(q_traj)
        se3_current = se3_target
        q_current = q_traj[-1]
    end_time = time.time()

    print(f"Took {end_time - start_time} seconds to compute trajectories.")
    yes_or_else = input("Save trajectories? (Y)\n")
    if (yes_or_else == "Y"):
        filename = input("Enter a filename.\n")
        np.save(f"trajectories/{filename}.npy", np.array(q_trajs, dtype=object))
        np.save(f"trajectories/{filename}.dt.npy", dt)

    return q_trajs, dt


def run_on_robot(q_trajs, dt):
    dt = float(dt)
    for q_traj in q_trajs:
        # yes_or_else = input("To run on the sim/real robot, type [yes], then press enter\n")
        # if yes_or_else != "yes":
        #     print("User did not type [yes], will not run on sim/real robot")
        #     return robot
        def trajectory_callback(index):
            print(f"At trajectory index: {index}")
            print(f"Commanding joint positions: {q_traj[index]}")
        robot.set_trajectory_callback(trajectory_callback)
        robot.run_joint_trajectory(q_traj, dt)


if __name__ == "__main__":
    robot, rtb_model = new_robot()

    if (len(sys.argv) > 1):
        # Find the trajectories from the file given
        q_trajs = np.load(f"trajectories/{sys.argv[1]}.npy", allow_pickle=True)
        dt = np.load(f"trajectories/{sys.argv[1]}.dt.npy", allow_pickle=True)
    else:
        q_trajs, dt = compute_trajectories(rtb_model, targets.board)
    run_on_robot(q_trajs, dt)


    robot.stop() # Makes sure render thread ends


