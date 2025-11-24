# A file for storing trajectory targets. All targets are
# relative to the end effector of the Panda, which is given by se3_start. 

from spatialmath import SE3
import numpy as np

descent = 0.328
near = 0.1
descent_near = descent - near
side_length = 0.18


def lift(pos):
    return SE3.Tz(0.02) * pos

def place(pos):
    return SE3.Tz(-0.02) * pos

def ua(t, se3_targets):
    """ Short for "update and append"
    """
    se3_target = t
    se3_targets.append(se3_target)
    return se3_target


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


def drawing_mode(se3_start):
    se3_targets = []
    se3_target = se3_start

    se3_target = ua(SE3.Tz(-descent_near) * SE3.Tx(side_length/2) * SE3.Ty(side_length/2) * se3_target, se3_targets)
    
    return se3_targets


def drawing_mode_1(se3_start):
    se3_targets = []
    se3_target = se3_start

    se3_target = ua(SE3.Tx(-side_length * (1/6)) * se3_target, se3_targets)
    se3_target = ua(SE3.Ty(-side_length * (1/6)) * se3_target, se3_targets)
    se3_target = ua(SE3.Tz(-near) * se3_target, se3_targets)
    se3_target = ua(SE3.Tz(near) * se3_target, se3_targets)

    return se3_targets

def drawing_mode_2(se3_start):
    se3_targets = []
    se3_target = se3_start

    se3_target = ua(SE3.Tx(-side_length * (1/6)) * se3_target, se3_targets)
    se3_target = ua(SE3.Ty(-side_length * (3/6)) * se3_target, se3_targets)
    se3_target = ua(SE3.Tz(-near) * se3_target, se3_targets)
    se3_target = ua(SE3.Tz(near) * se3_target, se3_targets)

    return se3_targets

def drawing_mode_3(se3_start):
    se3_targets = []
    se3_target = se3_start

    se3_target = ua(SE3.Tx(-side_length * (1/6)) * se3_target, se3_targets)
    se3_target = ua(SE3.Ty(-side_length * (5/6)) * se3_target, se3_targets)
    se3_target = ua(SE3.Tz(-near) * se3_target, se3_targets)
    se3_target = ua(SE3.Tz(near) * se3_target, se3_targets)

    return se3_targets

def drawing_mode_4(se3_start):
    se3_targets = []
    se3_target = se3_start

    se3_target = ua(SE3.Tz(-near) * se3_target, se3_targets)
    se3_target = ua(SE3.Tx(-side_length * (3/6)) * se3_target, se3_targets)
    se3_target = ua(SE3.Ty(-side_length * (1/6)) * se3_target, se3_targets)

    return se3_targets

def drawing_mode_5(se3_start):
    se3_targets = []
    se3_target = se3_start

    se3_target = ua(SE3.Tz(-near) * se3_target, se3_targets)
    se3_target = ua(SE3.Tx(-side_length * (3/6)) * se3_target, se3_targets)
    se3_target = ua(SE3.Ty(-side_length * (3/6)) * se3_target, se3_targets)

    return se3_targets

def drawing_mode_6(se3_start):
    se3_targets = []
    se3_target = se3_start

    se3_target = ua(SE3.Tz(-near) * se3_target, se3_targets)
    se3_target = ua(SE3.Tx(-side_length * (3/6)) * se3_target, se3_targets)
    se3_target = ua(SE3.Ty(-side_length * (5/6)) * se3_target, se3_targets)

    return se3_targets

def drawing_mode_7(se3_start):
    se3_targets = []
    se3_target = se3_start

    se3_target = ua(SE3.Tz(-near) * se3_target, se3_targets)
    se3_target = ua(SE3.Tx(-side_length * (5/6)) * se3_target, se3_targets)
    se3_target = ua(SE3.Ty(-side_length * (1/6)) * se3_target, se3_targets)

    return se3_targets

def drawing_mode_8(se3_start):
    se3_targets = []
    se3_target = se3_start

    se3_target = ua(SE3.Tz(-near) * se3_target, se3_targets)
    se3_target = ua(SE3.Tx(-side_length * (5/6)) * se3_target, se3_targets)
    se3_target = ua(SE3.Ty(-side_length * (3/6)) * se3_target, se3_targets)

    return se3_targets

def drawing_mode_9(se3_start):
    se3_targets = []
    se3_target = se3_start

    se3_target = ua(SE3.Tz(-near) * se3_target, se3_targets)
    se3_target = ua(SE3.Tx(-side_length * (5/6)) * se3_target, se3_targets)
    se3_target = ua(SE3.Ty(-side_length * (5/6)) * se3_target, se3_targets)

    return se3_targets


def board(se3_start):
    se3_targets = []

    # Start at current pose
    se3_target = se3_start

    # Move down (get close to the table)
    se3_target = ua(SE3.Tz(-descent) * SE3.Tx(side_length/2) * SE3.Ty(side_length/2) * se3_target, se3_targets)

    # --- Draw outer square ---
    se3_target = ua(SE3.Ty(-side_length) * se3_target, se3_targets)  # bottom edge
    se3_target = ua(SE3.Tx(-side_length) * se3_target, se3_targets)  # left edge
    se3_target = ua(SE3.Ty(side_length) * se3_target, se3_targets)   # top edge
    se3_target = ua(SE3.Tx(side_length) * se3_target, se3_targets)   # right edge (close square)
    se3_target = ua(lift(se3_target), se3_targets)

    # --- Draw inner grid lines (4 lines total) ---

    # Start first vertical
    se3_target = ua(SE3.Tx(-side_length / 3) * se3_target, se3_targets)
    se3_target = ua(place(se3_target), se3_targets)
    se3_target = ua(SE3.Ty(-side_length) * se3_target, se3_targets)
    se3_target = ua(lift(se3_target), se3_targets)
    # End first vertical

    # Start second vertical
    se3_target = ua(SE3.Tx(-side_length / 3) * se3_target, se3_targets)
    se3_target = ua(place(se3_target), se3_targets)
    se3_target = ua(SE3.Ty(side_length) * se3_target, se3_targets)
    se3_target = ua(lift(se3_target), se3_targets)
    # End second vertical

    # Begin first horizontal
    se3_target = ua(SE3.Tx(-side_length / 3) * SE3.Ty(-side_length / 3) * se3_target, se3_targets)
    se3_target = ua(place(se3_target), se3_targets)
    se3_target = ua(SE3.Tx(side_length) * se3_target, se3_targets)
    se3_target = ua(lift(se3_target), se3_targets)
    # End first 

    # Begin second horizontal
    se3_target = ua(SE3.Ty(-side_length / 3) * se3_target, se3_targets)
    se3_target = ua(place(se3_target), se3_targets)
    se3_target = ua(SE3.Tx(-side_length) * se3_target, se3_targets)
    se3_target = ua(lift(se3_target), se3_targets)

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
    se3_target = ua(SE3(arr), se3_targets)

    # Move ahead a bit
    se3_target = ua(SE3.Tx(0.2) * se3_target, se3_targets)

    return se3_targets

def cross(se3_start):
    se3_targets = []
    length = 0.1

    se3_target = se3_start  # start at current pose

    # move to start point of cross
    cross_height = length * np.cos(np.pi / 4)

    se3_target = ua(SE3.Tx(cross_height / 2) * SE3.Ty(cross_height / 2) * se3_target, se3_targets)
    se3_target = ua(SE3.Ty(cross_height / 2) * se3_target, se3_targets)

    # move down toward the table before drawing
    se3_target = ua(SE3.Tz(-descent) * se3_target, se3_targets)

    # draw first line of the cross

    se3_target = ua(SE3.Tx(-1 * cross_height) * se3_target, se3_targets)
    se3_target = ua(SE3.Ty(-1 * cross_height) * se3_target, se3_targets)

    se3_target = ua(lift(se3_target), se3_targets)  # lift marker 

    # draw second line of the cross
    se3_target = ua(SE3.Tx(cross_height) * se3_target, se3_targets)
    se3_target = ua(place(se3_target), se3_targets)  # place marker close to page

    se3_target = ua(SE3.Tx(-1 * cross_height) * se3_target, se3_targets)
    se3_target = ua(SE3.Ty(cross_height) * se3_target, se3_targets)

    se3_target = ua(lift(se3_target), se3_targets)  # lift marker 

    # return to start pose
    se3_targets.append(se3_start)

    return se3_targets    


# def circle(se3_start):
#     se3_targets = []
#     radius = 0.02
#     sample = 25

#     se3_target = se3_start  # start at current pose

#     # move to start point of circle
#     se3_target = ua(SE3.Tx(radius) * se3_target, se3_targets)

#     # move down toward the table before drawing
#     se3_target = ua(SE3.Tz(-descent) * se3_target, se3_targets)

#     # --- draw circle ---
#     # se3_target = ua(place(se3_target), se3_targets)  # place marker close to page to draw

#     prev_x, prev_y = radius, 0
#     for theta in np.linspace(0, 2 * np.pi, sample, endpoint=True):
#         x = radius * np.cos(theta)
#         y = radius * np.sin(theta)
#         dx = x - prev_x
#         dy = y - prev_y
#         se3_target = ua(SE3.Tx(dx) * SE3.Ty(dy) * se3_target, se3_targets)
#         prev_x, prev_y = x, y

#     se3_target = ua(lift(se3_target), se3_targets)  # lift marker after drawing the page

#     # return to start pose
#     se3_targets.append(se3_start)

#     return se3_targets   