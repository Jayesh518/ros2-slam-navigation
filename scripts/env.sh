#!/bin/bash
# Run a command in a clean ROS 2 Jazzy environment: usage `scripts/env.sh <command> [args...]`.
# Drops variables inherited from the shell (snap VS Code, other workspaces such as articuno_ws) so runs are reproducible.
# Sources /opt/ros/jazzy and, if built, this repo's install/ overlay. Set GUI=1 to keep display variables for RViz/Gazebo GUI.
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec env -i HOME="$HOME" USER="$USER" LOGNAME="$USER" LANG=C.UTF-8 \
  DISPLAY="${DISPLAY:-:1}" XAUTHORITY="${XAUTHORITY:-$HOME/.Xauthority}" XDG_RUNTIME_DIR="/run/user/$(id -u)" \
  PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin ROS_DOMAIN_ID="${ROS_DOMAIN_ID:-0}" \
  bash -c 'source /opt/ros/jazzy/setup.bash; [ -f "'"$ROOT"'/install/setup.bash" ] && source "'"$ROOT"'/install/setup.bash"; exec "$@"' _ "$@"
