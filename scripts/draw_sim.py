# Simulate a Panda drawing a Tic-Tac Board

import roboticstoolbox as rtb
import spatialmath as sm
import numpy as np
from swift import Swift

env = Swift()
env.launch(realtime=True)

robot = rtb.models.Panda()
robot.q = robot.qr

# Set a desired and effector pose an an offset from the current end-effector pose
Tep = robot.fkine(robot.q) * sm.SE3.Tx(0.2) * sm.SE3.Ty(0.2) * sm.SE3.Tz(0.45)

env.add(robot)

q0 = robot.q
sol = robot.ikine_LM(Tep)
qf = sol.q

# Define time vector
t = np.linspace(0, 1, 1000)
dt = t[1] - t[0]

# Generate smooth trajectory (cubic)
traj = rtb.jtraj(q0, qf, t)

# Animate or execute
for i in range(len(t)):
    robot.q = traj.q[i]
    env.step(dt)