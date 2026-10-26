#!/bin/bash
# Clean environment: only what a GUI ROS/Gazebo session needs. Avoids snap-VS-Code and other-workspace variables.
exec env -i HOME="$HOME" USER="$USER" LOGNAME="$USER" DISPLAY="${DISPLAY:-:1}" XAUTHORITY="${XAUTHORITY:-$HOME/.Xauthority}" \
  XDG_RUNTIME_DIR="/run/user/$(id -u)" LANG=C.UTF-8 PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
  bash -c 'source /opt/ros/jazzy/setup.bash && exec ros2 launch nav2_bringup tb3_simulation_launch.py headless:=False'
