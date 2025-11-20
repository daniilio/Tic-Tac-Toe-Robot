# A file for storing trajectory targets. All targets are
# relative to the end effector of the Panda, which is given by se3_start. 

from spatialmath import SE3
import numpy as np

descent = 0.328

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


ready_pose = SE3(np.array([
    [1, 0, 0, 0.484],
    [0, -1, 0, 0],
    [0, 0, -1, 0.4126],
    [0, 0, 0, 1],
]))

def ready(se3_start):
    return [ready_pose]

def lift(pos):
    return SE3.Tz(0.02) * pos

def place(pos):
    return SE3.Tz(-0.02) * pos

def ua(t, se3_targets):
    """ Short for "update and append"
    """
    se3_target = t
    se3_targets.append(se3_target)


def board(se3_start):
    se3_targets = []
    side_length = 0.18

    # Start at current pose
    se3_target = se3_start

    # Move down (get close to the table)
    ua(SE3.Tz(-descent) * SE3.Tx(side_length/2) * SE3.Ty(side_length/2) * se3_target, se3_targets)

    # --- Draw outer square ---
    ua(SE3.Ty(-side_length) * se3_target, se3_targets)  # bottom edge
    ua(SE3.Tx(-side_length) * se3_target, se3_targets)  # left edge
    ua(SE3.Ty(side_length) * se3_target, se3_targets)   # top edge
    ua(SE3.Tx(side_length) * se3_target, se3_targets)   # right edge (close square)
    ua(lift(se3_target), se3_targets)

    # --- Draw inner grid lines (4 lines total) ---

    # Start first vertical
    ua(SE3.Tx(-side_length / 3) * se3_target, se3_targets)
    ua(place(se3_target), se3_targets)
    ua(SE3.Ty(-side_length) * se3_target, se3_targets)
    ua(lift(se3_target), se3_targets)
    # End first vertical

    # Start second vertical
    ua(SE3.Tx(-side_length / 3) * se3_target, se3_targets)
    ua(place(se3_target), se3_targets)
    ua(SE3.Ty(side_length) * se3_target, se3_targets)
    ua(lift(se3_target), se3_targets)
    # End second vertical

    # Begin first horizontal
    ua(SE3.Tx(-side_length / 3) * SE3.Ty(-side_length / 3) * se3_target, se3_targets)
    ua(place(se3_target), se3_targets)
    ua(SE3.Tx(side_length) * se3_target, se3_targets)
    ua(lift(se3_target), se3_targets)
    # End first horizontal

    # Begin second horizontal
    ua(SE3.Ty(-side_length / 3) * se3_target, se3_targets)
    ua(place(se3_target), se3_targets)
    ua(SE3.Tx(-side_length) * se3_target, se3_targets)
    ua(lift(se3_target), se3_targets)

    se3_targets.append(se3_start)

    return se3_targets

def grab_marker(se3_start):
    se3_targets = []
    


def ee_init(se3_start):
    se3_targets = []

    # Start at current pose
    se3_target = se3_start

    arr = np.array([
        [0, 0, -1, 0.1749],
        [0, -1, 0, 0],
        [-1, 0, 0, 0.5046],
        [0, 0, 0, 1]
    ])

    # Rotate
    ua(SE3(arr), se3_targets)

    # Move ahead a bit
    ua(SE3.Tx(0.2) * se3_target, se3_targets)

    return se3_targets