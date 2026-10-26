#!/bin/bash
# Stop every simulation process this project starts (Gazebo, bridge, Nav2, robot_state_publisher, launch files).
# Matches process names (comm) and the launch script path, not free text, so it cannot kill the shell that calls it.
NAMES="gz ruby component_conta parameter_bridge robot_state_pub rviz2 create"
for sig in INT KILL; do
  for n in $NAMES; do pkill -$sig -x "$n" 2>/dev/null; done
  pkill -$sig -f "/opt/ros/jazzy/bin/ros2 launch" 2>/dev/null
  [ "$sig" = INT ] && sleep 3
done
exit 0
