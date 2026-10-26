#!/usr/bin/env bash
# Read-only environment check for Project 2 (ROS 2 Jazzy, Gazebo Harmonic, Nav2, SLAM Toolbox).
# Prints OK / MISSING / WRONG for each requirement in PLAN.md section 8. Installs nothing.
# Usage: bash scripts/check_env.sh | tee docs/environment-check.txt

missing=0
ok()  { printf '  OK       %-34s %s\n' "$1" "$2"; }
bad() { printf '  %-8s %-34s %s\n' "$1" "$2" "$3"; if [ "$1" != "OPTIONAL" ]; then missing=$((missing+1)); fi; }

echo "Project 2 environment check, $(date -u +%Y-%m-%dT%H:%MZ)"

echo "[1] Ubuntu"
ver=$(lsb_release -rs 2>/dev/null)
if [ "$ver" = "24.04" ]; then ok "Ubuntu 24.04" "$ver"; else bad WRONG "Ubuntu 24.04" "found: ${ver:-unknown}"; fi

echo "[2] ROS 2 Jazzy"
if [ -f /opt/ros/jazzy/setup.bash ]; then
  # shellcheck disable=SC1091
  source /opt/ros/jazzy/setup.bash 2>/dev/null
  if command -v ros2 >/dev/null; then ok "ros2 (jazzy)" "ROS_DISTRO=${ROS_DISTRO:-unset}"; else bad MISSING "ros2 command" ""; fi
else
  bad MISSING "/opt/ros/jazzy/setup.bash" "install ROS 2 Jazzy"
fi

# pkg <apt name> <label>
pkg() {
  if dpkg -s "$1" >/dev/null 2>&1; then ok "$2" "$(dpkg -s "$1" | awk '/^Version:/{print $2}')"
  else bad MISSING "$2" "apt package $1"; fi
}

echo "[3] Gazebo Harmonic and ROS bridge"
if command -v gz >/dev/null; then
  gzv=$(gz sim --versions 2>/dev/null | head -1)
  case "$gzv" in
    8.*) ok "Gazebo Harmonic (gz sim)" "$gzv" ;;
    *)   bad WRONG "Gazebo Harmonic (gz sim 8.x)" "found: ${gzv:-unknown}" ;;
  esac
else
  bad MISSING "gz (Gazebo)" ""
fi
pkg ros-jazzy-ros-gz-sim "ros_gz_sim"
pkg ros-jazzy-ros-gz-bridge "ros_gz_bridge"

echo "[4] RViz 2"
if command -v rviz2 >/dev/null; then ok "rviz2" "found"; else bad MISSING "rviz2" ""; fi

echo "[5] Nav2"
pkg ros-jazzy-navigation2 "navigation2"
pkg ros-jazzy-nav2-bringup "nav2_bringup"

echo "[6] SLAM Toolbox"
pkg ros-jazzy-slam-toolbox "slam_toolbox"

echo "[7] Build and git tools"
for c in colcon rosdep git gh python3 pytest; do
  if command -v "$c" >/dev/null; then ok "$c" "$(command -v "$c")"; else bad MISSING "$c" ""; fi
done

echo "[8] Python analysis packages"
for m in numpy pandas matplotlib scipy yaml; do
  if python3 -c "import $m" >/dev/null 2>&1; then ok "python: $m" "found"; else bad MISSING "python: $m" ""; fi
done

echo "[9] Disk space"
avail=$(df -BG --output=avail . 2>/dev/null | tail -1 | tr -dc '0-9')
if [ -n "$avail" ] && [ "$avail" -ge 20 ]; then ok "free space (>= 20 GB)" "${avail} GB"; else bad WRONG "free space (>= 20 GB)" "found: ${avail:-unknown} GB"; fi

echo "[10] GitHub access"
if git ls-remote origin >/dev/null 2>&1; then ok "git remote origin" "reachable"; else bad MISSING "git remote origin" "no network, or sign in with gh auth login"; fi

echo "[11-12] Optional"
if command -v nvidia-smi >/dev/null && nvidia-smi >/dev/null 2>&1; then
  ok "NVIDIA driver" "$(nvidia-smi --query-gpu=name,driver_version --format=csv,noheader | head -1)"
else
  bad OPTIONAL "NVIDIA driver" "not required; trials can run headless"
fi
if command -v docker >/dev/null; then ok "docker" "$(docker --version)"; else bad OPTIONAL "docker" "needed only in Phase 7"; fi

echo
if [ "$missing" -eq 0 ]; then
  echo "RESULT: all required items present."
else
  echo "RESULT: $missing required item(s) missing or wrong. Install only these, then re-run."
fi
exit 0
