# A file for storing trajectory targets. All targets are
# relative to the end effector of the Panda, which is given by se3_start. 

from spatialmath import SE3

def test_targets(se3_start):
    se3_targets = []
    se3_target = SE3.Ty(-0.10) * se3_start
    se3_targets.append(se3_target)
    
    se3_target = SE3.Tx(-0.10) * se3_target
    se3_targets.append(se3_target)

    se3_target = SE3.Ty(0.10) * se3_target
    se3_targets.append(se3_target)

    se3_target = SE3.Tx(0.10) * se3_target
    se3_targets.append(se3_target)

    return se3_targets


def board(se3_start):
    se3_targets = []
    side_length = 0.6

    # Start at current pose
    se3_target = se3_start

    SOME_NUMBER = -0.35 # Tune this once we have the marker on the gripper

    # Move inward a bit (so the panda doesnt collide with itself)
    se3_target = SE3.Ty(0.35) * se3_target
    se3_targets.append(se3_target)
    se3_target = SE3.Tx(0.15) * se3_target
    se3_targets.append(se3_target)

    # Move down (get close to the table)
    se3_target = SE3.Tz(SOME_NUMBER) * se3_target
    se3_targets.append(se3_target)

    # Move along -Y
    se3_target = SE3.Ty(-side_length) * se3_target
    se3_targets.append(se3_target)

    # Move along -X
    se3_target = SE3.Tx(-side_length) * se3_target
    se3_targets.append(se3_target)

    # Move along +Y
    se3_target = SE3.Ty(side_length) * se3_target
    se3_targets.append(se3_target)

    # Move along +X to close the square
    se3_target = SE3.Tx(side_length) * se3_target
    se3_targets.append(se3_target)

    return se3_targets