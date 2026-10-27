"""Custom recovery node: when the global plan keeps flipping between routes, forbid planning through unknown map cells for the rest of the goal.

Reads /plan and the NavigateToPose action status; on a trigger (see flip_logic) sets planner_server GridBased.allow_unknown to false, and sets it
back to true when no goal has been active for `release_after_s`. It uses only a published, runtime-settable parameter of the Nav2 planner.
Events are published on plan_flip_guard/events as 'flip', 'trigger' and 'release' (the trial runner counts the triggers).
"""
import math

import rclpy
from action_msgs.msg import GoalStatusArray
from nav_msgs.msg import Path
from rcl_interfaces.msg import Parameter as ParameterMsg, ParameterType, ParameterValue
from rcl_interfaces.srv import SetParameters
from rclpy.node import Node
from std_msgs.msg import String

from nav_study_trials.flip_logic import FlipDetector

ACTIVE = (1, 2, 3)  # STATUS_ACCEPTED, STATUS_EXECUTING, STATUS_CANCELING


class PlanFlipGuard(Node):
    def __init__(self):
        super().__init__("plan_flip_guard")
        self.release_after_s = self.declare_parameter("release_after_s", 2.0).value
        self.detector = FlipDetector()
        self.forbidding = False
        self.active = False
        self.idle_since = None
        self.events = self.create_publisher(String, "plan_flip_guard/events", 10)
        self.set_srv = self.create_client(SetParameters, "/planner_server/set_parameters")
        self.create_subscription(Path, "plan", self._on_plan, 10)
        self.create_subscription(GoalStatusArray, "navigate_to_pose/_action/status", self._on_status, 10)
        self.create_timer(0.5, self._tick)

    def _now(self):
        return self.get_clock().now().nanoseconds * 1e-9

    def _emit(self, kind):
        self.events.publish(String(data=kind))
        self.get_logger().info(f"{kind} at t={self._now():.1f}")

    def _set_allow_unknown(self, value):
        if not self.set_srv.service_is_ready():
            self.get_logger().warn("planner_server/set_parameters not available")
            return False
        p = ParameterMsg(name="GridBased.allow_unknown", value=ParameterValue(type=ParameterType.PARAMETER_BOOL, bool_value=value))
        req = SetParameters.Request(parameters=[p])
        self.set_srv.call_async(req)
        return True

    def _on_plan(self, msg):
        if not self.active or len(msg.poses) < 2:
            return
        pts = [(p.pose.position.x, p.pose.position.y) for p in msg.poses]
        length = sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))
        is_flip, is_trigger = self.detector.add_plan(self._now(), length)
        if is_flip:
            self._emit("flip")
        if is_trigger and not self.forbidding and self._set_allow_unknown(False):
            self.forbidding = True
            self._emit("trigger")

    def _on_status(self, msg):
        self.active = any(s.status in ACTIVE for s in msg.status_list)

    def _tick(self):
        if self.active:
            self.idle_since = None
            return
        if self.idle_since is None:
            self.idle_since = self._now()
        if self._now() - self.idle_since >= self.release_after_s:
            self.detector.reset()
            if self.forbidding and self._set_allow_unknown(True):
                self.forbidding = False
                self._emit("release")


def main(args=None):
    rclpy.init(args=args)
    rclpy.spin(PlanFlipGuard())


if __name__ == "__main__":
    main()
