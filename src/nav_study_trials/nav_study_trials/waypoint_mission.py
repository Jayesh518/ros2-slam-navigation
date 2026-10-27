"""Custom mission node: drive through a list of map-frame waypoints with NavigateToPose, retry a failed leg once, skip it after that, log every leg.

Usage: ros2 run nav_study_trials waypoint_mission --ros-args -p waypoints_file:=configs/mission_world_b.yaml -p log_file:=results/mission_log.csv
The waypoint file is a YAML list: waypoints: [{x: 1.0, y: 2.0, yaw: 0.0}, ...] in the map frame. Needs a running Nav2 with AMCL localised.
"""
import csv
import math
from pathlib import Path

import rclpy
import yaml
from action_msgs.msg import GoalStatus
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node

from nav_study_trials.mission_logic import Mission


class WaypointMission(Node):
    def __init__(self):
        super().__init__("waypoint_mission")
        wp_file = self.declare_parameter("waypoints_file", "").value
        self.log_file = self.declare_parameter("log_file", "mission_log.csv").value
        self.leg_timeout = self.declare_parameter("leg_timeout_s", 180.0).value
        waypoints = yaml.safe_load(Path(wp_file).read_text())["waypoints"]
        self.mission = Mission(waypoints, max_attempts=self.declare_parameter("max_attempts", 2).value)
        self.nav = ActionClient(self, NavigateToPose, "navigate_to_pose")
        self.t_leg = None
        self.timer = self.create_timer(0.5, self._start_leg)
        self.busy = False

    def _now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def _start_leg(self):
        if self.busy:
            return
        wp = self.mission.current()
        if wp is None:
            self._finish()
            return
        if not self.nav.wait_for_server(timeout_sec=1.0):
            self.mission.attempts -= 1  # not an attempt
            return
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = "map"
        goal.pose.pose.position.x, goal.pose.pose.position.y = float(wp["x"]), float(wp["y"])
        yaw = float(wp.get("yaw", 0.0))
        goal.pose.pose.orientation.z, goal.pose.pose.orientation.w = math.sin(yaw / 2), math.cos(yaw / 2)
        self.busy, self.t_leg = True, self._now()
        self.get_logger().info(f"leg {self.mission.index + 1}/{len(self.mission.waypoints)} attempt {self.mission.attempts}: ({wp['x']}, {wp['y']})")
        self.nav.send_goal_async(goal).add_done_callback(self._accepted)
        self.timeout_timer = self.create_timer(self.leg_timeout, self._timeout)

    def _accepted(self, fut):
        self.handle = fut.result()
        if not self.handle.accepted:
            self._leg_done(False)
            return
        self.handle.get_result_async().add_done_callback(lambda f: self._leg_done(f.result().status == GoalStatus.STATUS_SUCCEEDED))

    def _timeout(self):
        if self.busy and getattr(self, "handle", None) is not None:
            self.handle.cancel_goal_async()  # the result callback then reports a failed leg

    def _leg_done(self, reached):
        if not self.busy:
            return
        self.timeout_timer.cancel()
        outcome = self.mission.report(reached, self._now() - self.t_leg)
        self.get_logger().info(f"leg {self.mission.log[-1]['leg'] + 1}: {outcome}")
        self.busy = False

    def _finish(self):
        self.timer.cancel()
        Path(self.log_file).parent.mkdir(parents=True, exist_ok=True)
        with open(self.log_file, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["leg", "attempt", "outcome", "duration_s"])
            w.writeheader()
            w.writerows(self.mission.log)
        self.get_logger().info(f"mission finished: {self.mission.summary()}")
        raise SystemExit(0)


def main(args=None):
    rclpy.init(args=args)
    try:
        rclpy.spin(WaypointMission())
    except SystemExit:
        pass


if __name__ == "__main__":
    main()
