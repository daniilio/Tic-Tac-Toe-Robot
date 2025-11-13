import roboticstoolbox as rtb
import time
import sys
import pickle

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


def make_trajectories(funcs, factors):
    motion_generator = RuckigMotionGenerator()
    
    q_start = rtb_model.qr
    se3_start = rtb_model.fkine(q_start)

    for i, func in enumerate(funcs):
        start_time = time.time()
        q_trajs = []
        if i == 0:
            se3_current = se3_start 
            q_current = q_start
        se3_targets = func(se3_current)

        for se3_target in se3_targets:
            cartesian_traj, dt = motion_generator.calculate_cartesian_pose_trajectory(se3_current, se3_target,
                                                                                    factors[i][0], factors[i][1], factors[i][2]) 
            q_traj = motion_generator.cartesian_pose_to_joint_trajectory(rtb_model, q_current, cartesian_traj)
            q_trajs.append(q_traj)
            se3_current = se3_target
            q_current = q_traj[-1]
        end_time = time.time()

        print(f"Took {end_time - start_time} seconds to compute trajectories.")
        yes_or_else = input("Save trajectories? (Y)\n")
        if (yes_or_else == "Y"):
            filename = input("Enter a filename.\n")
            with open(f"trajectories/{filename}.pkl", "wb") as f:
                pickle.dump(q_trajs, f)
            with open(f"trajectories/{filename}.dt.pkl", "wb") as f:
                pickle.dump(dt, f)

        run_on_robot(q_trajs, dt)


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
        for i in range(1, len(sys.argv)):
            # Find the trajectories from the files given
            with open(f"trajectories/{sys.argv[i]}.pkl", "rb") as f:
                q_trajs = pickle.load(f)
            with open(f"trajectories/{sys.argv[i]}.dt.pkl", "rb") as f:
                dt = pickle.load(f)
            run_on_robot(q_trajs, dt)
    else:
        # make_trajectories([targets.ee_init, targets.board, targets.reset], [(1, 0.6, 0.6), (0.2, 0.2, 0.4), (1, 0.6, 0.6)])
        make_trajectories([targets.ee_init, targets.circle, targets.reset], [(1, 0.6, 0.6), (0.2, 0.2, 0.4), (1, 0.6, 0.6)])


    robot.stop() # Makes sure render thread ends


