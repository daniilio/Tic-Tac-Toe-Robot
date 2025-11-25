import trajectory_lib as ttr
import sys
import pickle
import targets
import targets_joint


if __name__ == "__main__":
    robot, rtb_model = ttr.new_robot()

    # First, we need to be in the ready position that the saved trajectories expect
    q_target = rtb_model.qr
    ttr.joint_trajectory(robot, q_target)

    if (len(sys.argv) > 1):
        # Try to load trajectories
        for i in range(1, len(sys.argv)):
            # Find the trajectories from the files given
            with open(f"trajectories/{sys.argv[i]}.pkl", "rb") as f:
                q_trajs = pickle.load(f)
            with open(f"trajectories/{sys.argv[i]}.dt.pkl", "rb") as f:
                dt = pickle.load(f)
            ttr.run_on_robot(robot, q_trajs, dt)
    else:
       # Does the following: 
        # - From ready position, draws the board, then goes back to the ready position. 
        # - From ready position, goes into drawing mode (a ready position that is closer to the board)
        # - From drawing mode, go back to ready position

        # draw the board: READY to DRAWING THE BOARD to READY (because it returns back)
        factors=(0.02, 0.01, 0.05)


        ttr.make_trajectories_and_run(
            robot,
            [targets.board],
            [factors],
            "READY_to_BOARD_to_READY",
            save=True
        )


        # Go from READY to DRAWING_MODE first
        q_target = targets_joint.DRAWING_MODE
        ttr.joint_trajectory(robot, q_target, "READY_to_DRAWING_MODE", save=True)

        # Horizontal strikes
        for idx, mode in zip([9, 6, 3], [targets.drawing_mode_9, targets.drawing_mode_6, targets.drawing_mode_3]):
            ttr.make_trajectories_and_run(
                robot,
                [mode],
                [factors],
                f"DRAWING_MODE_to_MODE_{idx}",
                save=True
            )
            ttr.make_trajectories_and_run(
                robot,
                [targets.strike_horizontal],
                [factors],
                f"MODE_{idx}_to_HORIZONTAL_{idx}",
                save=True
            )
            q_target = targets_joint.DRAWING_MODE
            ttr.joint_trajectory(robot, q_target, f"HORIZONTAL_{idx}_to_DRAWING_MODE", save=True)

        # Vertical strikes
        for idx, mode in zip([3, 2, 1], [targets.drawing_mode_3, targets.drawing_mode_2, targets.drawing_mode_1]):
            ttr.make_trajectories_and_run(
                robot,
                [mode],
                [factors],
                f"DRAWING_MODE_to_MODE_{idx}",
                save=True
            )
            ttr.make_trajectories_and_run(
                robot,
                [targets.strike_vertical],
                [factors],
                f"MODE_{idx}_to_VERTICAL_{idx}",
                save=True
            )
            q_target = targets_joint.DRAWING_MODE
            ttr.joint_trajectory(robot, q_target, f"VERTICAL_{idx}_to_DRAWING_MODE", save=True)

        # Diagonal strikes
        diagonal_modes = [
            (9, targets.drawing_mode_9, targets.strike_diagonal_from_9),
            (7, targets.drawing_mode_7, targets.strike_diagonal_from_7)
        ]

        for idx, mode, strike_func in diagonal_modes:
            ttr.make_trajectories_and_run(
                robot,
                [mode],
                [factors],
                f"DRAWING_MODE_to_MODE_{idx}",
                save=True
            )
            ttr.make_trajectories_and_run(
                robot,
                [strike_func],
                [factors],
                f"MODE_{idx}_to_DIAGONAL_{idx}",
                save=True
            )
            q_target = targets_joint.DRAWING_MODE
            ttr.joint_trajectory(robot, q_target, f"DIAGONAL_{idx}_to_DRAWING_MODE", save=True)

        # WILL BE AT DRAWING MODE NOW

        # Loop over drawing modes 1-9
        for i in range(1, 10):
            mode_name = f"drawing_mode_{i}"
            se3_func = getattr(targets, mode_name)

            ttr.make_trajectories_and_run(
                robot,
                [se3_func],
                [factors],
                f"DRAWING_MODE_to_MODE_{i}",
                save=True
            )

            ttr.make_trajectories_and_run(
                robot,
                [targets.cross],
                [factors],
                f"MODE_{i}_to_CROSS_{i}_to_MODE_{i}",
                save=True
            )

            # Return to DRAWING_MODE after each drawing mode
            q_target = targets_joint.DRAWING_MODE
            ttr.joint_trajectory(robot, q_target, f"MODE_{i}_to_DRAWING_MODE", save=True)

    
    # When done, return to the ready position
    q_target = targets_joint.READY
    ttr.joint_trajectory(robot, q_target, "DRAWING_MODE_to_READY", save=True)


    robot.stop() # Makes sure render thread ends