import roboticstoolbox as rtb
import time
import sys
import pickle
import numpy as np

from franka_api.motion_generator import RuckigMotionGenerator
from franka_api.visualizer import RtbVisualizer
import targets
import targets_joint

np.set_printoptions(precision=4, suppress=True,)  

def new_robot():
    panda_rtb_model = rtb.models.Panda()
    
    q_start = panda_rtb_model.qr
    robot = RtbVisualizer(panda_rtb_model, q_start)

    return robot, panda_rtb_model


def make_trajectories_and_run(robot: RtbVisualizer, funcs, factors, save=True):
    motion_generator = RuckigMotionGenerator()
    
    q_start = robot.rtb_robot_model.q
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
        if (save):
            yes_or_else = input("Save trajectories? (Y)\n")
            if (yes_or_else == "Y"):
                filename = input("Enter a filename.\n")
                with open(f"trajectories/{filename}.pkl", "wb") as f:
                    pickle.dump(q_trajs, f)
                with open(f"trajectories/{filename}.dt.pkl", "wb") as f:
                    pickle.dump(dt, f)

        run_on_robot(robot, q_trajs, dt)


def joint_trajectory(robot: RtbVisualizer, q_target: np.array):
    motion_generator = RuckigMotionGenerator()
    q_start = robot.rtb_robot_model.q
    q_traj, dt = motion_generator.calculate_joint_pose_trajectory(q_start, 
                                                                  q_target,
                                                                  relative_vel_factor=0.2,
                                                                  relative_acc_factor=0.1,
                                                                  relative_jerk_factor=0.5)
    

    run_on_robot(robot, [q_traj], dt)


def run_on_robot(robot, q_trajs, dt):
    # Sim or real, works the same.
    dt = float(dt)
    for q_traj in q_trajs:
        def trajectory_callback(index):
            print(f"At trajectory index: {index}")
            print(f"Commanding joint positions: {q_traj[index]}")
        robot.set_trajectory_callback(trajectory_callback)
        robot.run_joint_trajectory(q_traj, dt)


if __name__ == "__main__":
    robot, rtb_model = new_robot()
    # First, we need to be in the ready position that the saved trajectories expect
    q_target = targets_joint.READY
    joint_trajectory(robot, q_target)

    if (len(sys.argv) > 1):
        # Try to load trajectories

        for i in range(1, len(sys.argv)):
            # Find the trajectories from the files given
            with open(f"trajectories/{sys.argv[i]}.pkl", "rb") as f:
                q_trajs = pickle.load(f)
            with open(f"trajectories/{sys.argv[i]}.dt.pkl", "rb") as f:
                dt = pickle.load(f)
            run_on_robot(robot, q_trajs, dt)
    else:
        # Does the following: 
        # - From ready position, draws the board, then goes back to the ready position. 
        # - From ready position, goes into drawing mode (a ready position that is closer to the board)
        # - From drawing mode, go back to ready position

        make_trajectories_and_run(
            robot, 
            [targets.board], 
            [(0.2, 0.1, 0.5)]
        )

        q_target = targets_joint.READY
        joint_trajectory(robot, q_target)

        q_target = targets_joint.DRAWING_MODE
        joint_trajectory(robot, q_target)

    
    # When done, return to the ready position
    q_target = targets_joint.READY
    joint_trajectory(robot, q_target)


    robot.stop() # Makes sure render thread ends


