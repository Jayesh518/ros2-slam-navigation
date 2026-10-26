#!/bin/bash
# Stop every simulation process this project starts (Gazebo, bridge, Nav2, SLAM Toolbox, robot_state_publisher, launch files).
# Usage: scripts/stop_sim.sh        stop the simulation stack
#        scripts/stop_sim.sh all    also stop a running scripts/map_world.sh / tour.py (never do this from inside those scripts)
# Matches process names and install paths, not free text, so it cannot kill the shell that calls it.
NAMES="gz ruby component_conta parameter_bridge robot_state_pub rviz2 create"
if [ "$1" = all ]; then
  pkill -KILL -f "scripts/map_world.sh" 2>/dev/null
  pkill -KILL -f "scripts/tour.py" 2>/dev/null
fi
for sig in INT KILL; do
  pkill -$sig -f "/opt/ros/jazzy/lib/nav2_" 2>/dev/null
  pkill -$sig -f "/opt/ros/jazzy/lib/slam_toolbox" 2>/dev/null
  pkill -$sig -f "/opt/ros/jazzy/lib/rclcpp_components" 2>/dev/null
  pkill -$sig -f "/opt/ros/jazzy/lib/ros_gz_" 2>/dev/null
  pkill -$sig -f "/opt/ros/jazzy/lib/robot_state_publisher" 2>/dev/null
  pkill -$sig -f "/opt/ros/jazzy/lib/rviz2" 2>/dev/null
  for n in $NAMES; do pkill -$sig -x "$n" 2>/dev/null; done
  pkill -$sig -f "/opt/ros/jazzy/bin/ros2 launch" 2>/dev/null
  [ "$sig" = INT ] && sleep 3
done
exit 0
