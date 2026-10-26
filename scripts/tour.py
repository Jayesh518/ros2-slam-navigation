#!/usr/bin/env python3
"""Drive the robot round a world through a fixed list of waypoints with Nav2 (used while SLAM Toolbox builds the map).

Usage (through scripts/env.sh):  python3 scripts/tour.py world_a
Prints one line per waypoint (SUCCEEDED / FAILED); exit code 0 even if a waypoint fails, the map is judged by eye afterwards.
"""
import sys
import time

import rclpy
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult

TOURS = {
    "world_a": [(3.5, 3.5), (-3.5, 3.5), (-3.5, -3.5), (3.5, -3.5), (0.0, 0.0)],
    "world_b": [(6.5, 0.0), (4.0, 2.5), (6.0, 3.5), (4.0, 0.0), (4.0, -2.5), (6.0, -3.5), (4.0, 0.0), (-4.0, 0.0),
                (-4.0, 2.5), (-6.0, 3.5), (-4.0, 0.0), (-4.0, -2.5), (-6.0, -3.5), (-7.0, 0.0), (0.0, 0.0)],
    "world_c": [(0.0, 5.0), (2.5, 5.0), (5.0, 5.0), (5.0, 0.0), (5.0, -5.0), (2.5, -5.0), (0.0, -5.0), (-2.5, -5.0),
                (-5.0, -5.0), (-5.0, 0.0), (-5.0, 5.0), (-2.5, 5.0), (0.0, 0.0)],
}
TIMEOUT_S = 240  # wall-clock per waypoint
STEP = 2.0       # m; while SLAM runs the planning map only covers what the LiDAR has seen, so goals must stay close to the known area


def densify(points, step=STEP, start=(0.0, 0.0)):
    out, (px, py) = [], start
    for x, y in points:
        n = max(1, int(((x - px) ** 2 + (y - py) ** 2) ** 0.5 // step) + 1)
        out += [(px + (x - px) * k / n, py + (y - py) * k / n) for k in range(1, n + 1)]
        px, py = x, y
    return out


world = sys.argv[1]
WAYPOINTS = densify(TOURS[world])
rclpy.init()
nav = BasicNavigator()
# Own start-up wait (the helper's waitUntilNav2Active never saw slam_toolbox/get_state here): action server up, then map->base_link known.
from rclpy.duration import Duration
from rclpy.time import Time
from tf2_ros import Buffer, TransformListener

nav.nav_to_pose_client.wait_for_server()
tf_buffer = Buffer()
TransformListener(tf_buffer, nav)
while rclpy.ok() and not tf_buffer.can_transform("map", "base_link", Time(), Duration(seconds=0.5)):
    rclpy.spin_once(nav, timeout_sec=0.5)
time.sleep(5)  # let the costmaps fill from the first scans
for i, (x, y) in enumerate(WAYPOINTS, 1):
    goal = PoseStamped()
    goal.header.frame_id = "map"
    goal.header.stamp = Time().to_msg()  # zero = latest; the navigator node runs on wall time, the simulation does not
    goal.pose.position.x, goal.pose.position.y, goal.pose.orientation.w = x, y, 1.0
    nav.goToPose(goal)
    t0 = time.time()
    while not nav.isTaskComplete():
        if time.time() - t0 > TIMEOUT_S:
            nav.cancelTask()
            break
        time.sleep(0.5)
    result = nav.getResult()
    print(f"{world} waypoint {i}/{len(WAYPOINTS)} ({x}, {y}): {'SUCCEEDED' if result == TaskResult.SUCCEEDED else 'FAILED'} after {time.time() - t0:.0f} s", flush=True)
rclpy.shutdown()
