import roboticstoolbox as rtb
import time
import sys
import pickle
import numpy as np

from franka_api.motion_generator import RuckigMotionGenerator
import csc376_bind_franky
import targets
import targets_joint

np.set_printoptions(precision=4, suppress=True,)  

def new_robot():
    rtb_model = rtb.models.Panda()
    robot = csc376_bind_franky.FrankaJointTrajectoryController("192.168.1.107")
    robot.setupSignalHandler()
    return robot, rtb_model


# def make_trajectories_and_run(robot: csc376_bind_franky.FrankaJointTrajectoryController,
#                               rtb_model: rtb.models.Panda, funcs, factors, filename="", save=False):
    
def make_trajectories_and_run(robot: csc376_bind_franky.FrankaJointTrajectoryController, funcs, factors, filename="", save=False):

    motion_generator = RuckigMotionGenerator()
    
    q_start =  robot.get_current_joint_positions()
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
            if len(q_traj) == 1:
                q_traj = [q_current, q_traj[0]]
            q_trajs.append(q_traj)
            se3_current = se3_target
            q_current = q_traj[-1]
        end_time = time.time()

        print(f"Took {end_time - start_time} seconds to compute trajectories.")
        if (save):
            with open(f"trajectories/{filename}.pkl", "wb") as f:
                pickle.dump(q_trajs, f)
            with open(f"trajectories/{filename}.dt.pkl", "wb") as f:
                pickle.dump(dt, f)

        run_on_robot(robot, q_trajs, dt)


def joint_trajectory(robot: csc376_bind_franky.FrankaJointTrajectoryController, q_target: np.array, 
                     filename="", save=False):
    motion_generator = RuckigMotionGenerator()
    q_start = robot.get_current_joint_positions()
    q_traj, dt = motion_generator.calculate_joint_pose_trajectory(q_start, 
                                                                  q_target,
                                                                  relative_vel_factor=0.2,
                                                                  relative_acc_factor=0.1,
                                                                  relative_jerk_factor=0.5)
    if (save):
        with open(f"trajectories/{filename}.pkl", "wb") as f:
            pickle.dump([q_traj], f)
        with open(f"trajectories/{filename}.dt.pkl", "wb") as f:
            pickle.dump(dt, f)

    run_on_robot(robot, [q_traj], dt)


def run_on_robot(robot: csc376_bind_franky.FrankaJointTrajectoryController, q_trajs, dt):
    # Sim or real, works the same.
    dt = float(dt)
    for q_traj in q_trajs:
        def trajectory_callback(index):
            print(f"At trajectory index: {index}")
            print(f"Commanding joint positions: {q_traj[index]}")
        robot.set_trajectory_callback(trajectory_callback)
        robot.run_joint_trajectory(q_traj, dt)


def run_trajectory(robot, file_name):
    # Find the trajectories from the files given
    with open(f"trajectories/{file_name}.pkl", "rb") as f:
        q_trajs = pickle.load(f)
    with open(f"trajectories/{file_name}.dt.pkl", "rb") as f:
        dt = pickle.load(f)
    run_on_robot(robot, q_trajs, dt)


# run upon initialization!
def set_to_ready_position(robot, rtb_model):
    q_target = targets_joint.READY
    joint_trajectory(robot, q_target)

    # # set to camera position
    # run_trajectory(robot, "READY_to_CAMERA_MODE")



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

        # draw the board: READY to DRAWING THE BOARD to READY (because it returns back)
        factors=(0.02, 0.01, 0.05)

        make_trajectories_and_run(
            robot,
            [targets.board],
            [factors],
            "READY_to_BOARD_to_READY",
            save=True
        )


        # Go from READY to DRAWING_MODE first
        q_target = targets_joint.DRAWING_MODE
        joint_trajectory(robot, q_target, "READY_to_DRAWING_MODE", save=True)

        # # Horizontal strikes
        for idx, mode in zip([9, 6, 3], [targets.drawing_mode_9, targets.drawing_mode_6, targets.drawing_mode_3]):
            make_trajectories_and_run(
                robot,
                [mode],
                [factors],
                f"DRAWING_MODE_to_MODE_{idx}",
                save=True
            )
            make_trajectories_and_run(
                robot,
                [targets.strike_horizontal],
                [factors],
                f"MODE_{idx}_to_HORIZONTAL_{idx}",
                save=True
            )
            q_target = targets_joint.DRAWING_MODE
            joint_trajectory(robot, q_target, f"HORIZONTAL_{idx}_to_DRAWING_MODE", save=True)

        # Vertical strikes
        for idx, mode in zip([3, 2, 1], [targets.drawing_mode_3, targets.drawing_mode_2, targets.drawing_mode_1]):
            make_trajectories_and_run(
                robot,
                [mode],
                [factors],
                f"DRAWING_MODE_to_MODE_{idx}",
                save=True
            )
            make_trajectories_and_run(
                robot,
                [targets.strike_vertical],
                [factors],
                f"MODE_{idx}_to_VERTICAL_{idx}",
                save=True
            )
            q_target = targets_joint.DRAWING_MODE
            joint_trajectory(robot, q_target, f"VERTICAL_{idx}_to_DRAWING_MODE", save=True)

        # Diagonal strikes
        diagonal_modes = [
            (9, targets.drawing_mode_9, targets.strike_diagonal_from_9),
            (7, targets.drawing_mode_7, targets.strike_diagonal_from_7)
        ]

        for idx, mode, strike_func in diagonal_modes:
            make_trajectories_and_run(
                robot,
                [mode],
                [factors],
                f"DRAWING_MODE_to_MODE_{idx}",
                save=True
            )
            make_trajectories_and_run(
                robot,
                [strike_func],
                [factors],
                f"MODE_{idx}_to_DIAGONAL_{idx}",
                save=True
            )
            q_target = targets_joint.DRAWING_MODE
            joint_trajectory(robot, q_target, f"DIAGONAL_{idx}_to_DRAWING_MODE", save=True)

        # WILL BE AT DRAWING MODE NOW

        # Loop over drawing modes 1-9
        for i in range(1, 10):
            mode_name = f"drawing_mode_{i}"
            se3_func = getattr(targets, mode_name)

            make_trajectories_and_run(
                robot,
                [se3_func],
                [factors],
                f"DRAWING_MODE_to_MODE_{i}",
                save=True
            )

            make_trajectories_and_run(
                robot,
                [targets.cross],
                [factors],
                f"MODE_{i}_to_CROSS_{i}_to_MODE_{i}",
                save=True
            )

            # Return to DRAWING_MODE after each drawing mode
            q_target = targets_joint.DRAWING_MODE
            joint_trajectory(robot, q_target, f"MODE_{i}_to_DRAWING_MODE", save=True)

    
    # When done, return to the ready position
    q_target = targets_joint.READY
    joint_trajectory(robot, q_target, "DRAWING_MODE_to_READY", save=True)

    # go to CAMERA_MODE from READY
    q_target = targets_joint.CAMERA_MODE
    joint_trajectory(robot, q_target, "READY_to_CAMERA_MODE", save=True)
    
    # go to READY from CAMERA_MODE
    q_target = targets_joint.READY
    joint_trajectory(robot, q_target, "CAMERA_MODE_to_READY", save=True)


    robot.stop() # Makes sure render thread ends



