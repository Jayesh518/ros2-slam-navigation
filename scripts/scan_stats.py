#!/usr/bin/env python3
"""Print beam count and min/max valid range of one /scan message. Run through scripts/env.sh (needs ROS 2)."""
import math
import sys

import rclpy
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import LaserScan

rclpy.init()
node = rclpy.create_node("scan_stats")
msg = []
node.create_subscription(LaserScan, "/scan", msg.append, qos_profile_sensor_data)
end = node.get_clock().now().nanoseconds + 10_000_000_000
while not msg and node.get_clock().now().nanoseconds < end:
    rclpy.spin_once(node, timeout_sec=0.5)
if not msg:
    print("no /scan message")
    sys.exit(1)
r = [x for x in msg[0].ranges if math.isfinite(x)]
print(f"beams {len(msg[0].ranges)}, finite {len(r)}, min {min(r):.2f} m, max {max(r):.2f} m" if r else "no finite ranges")
