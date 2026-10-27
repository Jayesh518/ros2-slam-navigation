"""Automated trial runner (docs/protocol.md): sends goals to a running Nav2 stack, judges them against Gazebo ground truth, writes one CSV row per trial.

Run one (configuration, world) session against a running simulation + Nav2 (see scripts/run_session.sh):
    ros2 run nav_study_trials run_trials --config baseline --world world_a --repeats 2 --seed 1 --out results/trials/baseline_world_a.csv

Per trial: stop the robot, teleport it to the start pose, set the AMCL initial pose to the true start pose (protocol section 3), clear the costmaps,
send NavigateToPose, record ground truth / AMCL / contacts / behaviour-tree events until the result or the timeout (simulated time), stop the
robot (the Gazebo drive plugin keeps the last velocity command), compute the metrics in metrics.py and append the CSV row.
"""
import argparse
import csv
import math
import random
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

import rclpy
import yaml
from action_msgs.msg import GoalStatus
from geometry_msgs.msg import PoseWithCovarianceStamped, Twist
from nav2_msgs.action import NavigateToPose
from nav2_msgs.msg import BehaviorTreeLog, CollisionMonitorState
from nav2_msgs.srv import ClearEntireCostmap
from nav_msgs.msg import Odometry, Path as PathMsg
from rclpy.action import ActionClient
from rclpy.node import Node
from rclpy.parameter import Parameter
from rclpy.qos import qos_profile_sensor_data
from ros_gz_interfaces.msg import Contacts
from sensor_msgs.msg import LaserScan
from std_msgs.msg import String

from nav_study_trials import metrics

COLUMNS = ["trial_id", "config", "world", "pair", "repeat", "seed", "success", "failure_reason", "nav2_status", "time_s", "path_m",
           "final_error_m", "valid", "reset_attempts", "collisions", "recovery_events", "loc_err_max_m", "loc_err_mean_m", "loc_failure", "sim_end_s", "wall_s", "started_utc"]
STATUS = {GoalStatus.STATUS_SUCCEEDED: "SUCCEEDED", GoalStatus.STATUS_ABORTED: "ABORTED", GoalStatus.STATUS_CANCELED: "CANCELED"}
CONTACT_TOPICS = {"contact/base": "base", "contact/lidar": "lidar", "contact/wheel_left": "wheel_left", "contact/wheel_right": "wheel_right"}


def yaw_of(q):
    return math.atan2(2 * (q.w * q.z + q.x * q.y), 1 - 2 * (q.y * q.y + q.z * q.z))


def quat(yaw):
    return math.sin(yaw / 2), math.cos(yaw / 2)  # z, w


class TrialRunner(Node):
    def __init__(self, args, alignment):
        super().__init__("trial_runner", parameter_overrides=[Parameter("use_sim_time", Parameter.Type.BOOL, True)])
        self.args, self.al = args, alignment
        self.recording = False
        self.gt = None          # latest (t, x, y, yaw) in the world frame
        self.track, self.amcl_err, self.contacts, self.bt = [], [], [], []
        self.latest_amcl = None
        # optional per-trial trace for diagnosis (Phase 5); off unless --trace-dir is given, and it does not change what is measured
        self.trace, self.events = [], []
        self.cmd, self.scan_min, self.cm_state = (0.0, 0.0), math.nan, ""
        self.last_trace_t = -1.0
        if args.trace_dir:
            self.create_subscription(Twist, "cmd_vel", self._on_cmd, 10)
            self.create_subscription(LaserScan, "scan", self._on_scan, qos_profile_sensor_data)
            self.create_subscription(PathMsg, "plan", self._on_plan, 10)
            self.create_subscription(CollisionMonitorState, "collision_monitor_state", self._on_cm, 10)
        self.guard_triggers = 0
        if args.guard:  # recovery configuration: count the triggers of the plan_flip_guard node (docs/protocol.md change (n))
            self.create_subscription(String, "plan_flip_guard/events", self._on_guard, 10)
        self.create_subscription(Odometry, "ground_truth", self._on_gt, 10)
        self.create_subscription(PoseWithCovarianceStamped, "amcl_pose", self._on_amcl, 10)
        self.create_subscription(BehaviorTreeLog, "behavior_tree_log", self._on_bt, 50)
        for topic, part in CONTACT_TOPICS.items():
            self.create_subscription(Contacts, topic, lambda msg, p=part: self._on_contacts(msg, p), 50)
        self.cmd_pub = self.create_publisher(Twist, "cmd_vel", 10)
        self.init_pub = self.create_publisher(PoseWithCovarianceStamped, "initialpose", 10)
        self.nav = ActionClient(self, NavigateToPose, "navigate_to_pose")
        self.clear = [self.create_client(ClearEntireCostmap, n) for n in
                      ("global_costmap/clear_entirely_global_costmap", "local_costmap/clear_entirely_local_costmap")]

    # --- callbacks -------------------------------------------------------------------------------------------------------------------
    def now(self):
        return self.get_clock().now().nanoseconds / 1e9

    def _on_gt(self, msg):
        p = msg.pose.pose
        self.gt = (self.now(), p.position.x, p.position.y, yaw_of(p.orientation))
        if self.recording:
            self.track.append(self.gt)
            if self.args.trace_dir and self.gt[0] - self.last_trace_t >= 0.2:  # 5 Hz
                self.last_trace_t = self.gt[0]
                a = self.latest_amcl
                ax, ay = (metrics.map_to_world(a[1], a[2], 0.0, self.al)[:2]) if a else (math.nan, math.nan)
                self.trace.append((self.gt[0], self.gt[1], self.gt[2], self.gt[3], ax, ay, self.cmd[0], self.cmd[1], self.scan_min, self.cm_state))

    def _on_amcl(self, msg):
        p = msg.pose.pose
        self.latest_amcl = (self.now(), p.position.x, p.position.y, yaw_of(p.orientation))
        if self.recording and self.gt is not None:
            wx, wy, _ = metrics.map_to_world(p.position.x, p.position.y, 0.0, self.al)
            self.amcl_err.append((self.now(), math.dist((wx, wy), self.gt[1:3])))

    def _on_cmd(self, msg):
        self.cmd = (msg.linear.x, msg.angular.z)

    def _on_scan(self, msg):
        r = [x for x in msg.ranges if math.isfinite(x) and x >= msg.range_min]
        self.scan_min = min(r) if r else math.nan

    def _on_plan(self, msg):
        if self.recording and msg.poses:
            pts = [(p.pose.position.x, p.pose.position.y) for p in msg.poses]
            wx = [metrics.map_to_world(x, y, 0.0, self.al)[:2] for x, y in pts]
            length = sum(math.dist(a, b) for a, b in zip(wx, wx[1:]))
            self.events.append((self.now(), "plan", f"poses={len(pts)} length_m={length:.2f} end=({wx[-1][0]:.2f};{wx[-1][1]:.2f})"))

    def _on_guard(self, msg):
        if self.recording and msg.data == "trigger":
            self.guard_triggers += 1

    def _on_cm(self, msg):
        self.cm_state = f"{msg.action_type}:{msg.polygon_name}"

    def _on_contacts(self, msg, part):
        if self.recording:
            for c in msg.contacts:
                self.contacts.append((self.now(), c.collision1.name, c.collision2.name))  # collision1 is the sensor's own (robot) collision

    def _on_bt(self, msg):
        if self.recording:
            self.bt += [(e.node_name, e.previous_status, e.current_status) for e in msg.event_log]
            if self.args.trace_dir:
                self.events += [(self.now(), "bt", f"{e.node_name} {e.previous_status}->{e.current_status}") for e in msg.event_log]

    # --- helpers ---------------------------------------------------------------------------------------------------------------------
    def spin_for(self, seconds):
        """Spin for the given amount of simulated time (with a wall-clock guard of 20x)."""
        end, wall_end = self.now() + seconds, time.time() + 20 * seconds + 5
        while self.now() < end and time.time() < wall_end and rclpy.ok():
            rclpy.spin_once(self, timeout_sec=0.05)

    def stop_robot(self):
        for _ in range(5):
            self.cmd_pub.publish(Twist())
            rclpy.spin_once(self, timeout_sec=0.05)

    def teleport(self, x, y, yaw):
        z, w = quat(yaw)
        req = f'name: "nav_study_robot", position: {{x: {x}, y: {y}, z: 0.01}}, orientation: {{x: 0, y: 0, z: {z}, w: {w}}}'
        out = subprocess.run(["gz", "service", "-s", "/world/default/set_pose", "--reqtype", "gz.msgs.Pose", "--reptype", "gz.msgs.Boolean",
                              "--timeout", "3000", "--req", req], capture_output=True, text=True, timeout=20)
        if "true" not in out.stdout:
            raise RuntimeError(f"teleport failed: {out.stdout} {out.stderr}")

    def set_initial_pose(self, x, y, yaw):
        mx, my, myaw = metrics.world_to_map(x, y, yaw, self.al)
        msg = PoseWithCovarianceStamped()
        msg.header.frame_id = "map"
        msg.pose.pose.position.x, msg.pose.pose.position.y = mx, my
        msg.pose.pose.orientation.z, msg.pose.pose.orientation.w = quat(myaw)
        msg.pose.covariance[0] = msg.pose.covariance[7] = 0.05
        msg.pose.covariance[35] = 0.02
        for _ in range(3):
            self.init_pub.publish(msg)
            self.spin_for(0.3)

    def reset_localisation(self, x, y, yaw, attempts=5):
        """Set the AMCL pose to the true start pose and check, against ground truth, that AMCL accepted it (error < 0.5 m).

        The first pose is sometimes ignored right after a teleport (observed in validation); retry, and report how many attempts it took.
        Returns the attempt number that worked, or 0 if none did (the trial is then marked invalid and not judged).
        """
        for attempt in range(1, attempts + 1):
            self.latest_amcl = None
            self.set_initial_pose(x, y, yaw)
            end = self.now() + 6.0
            while self.now() < end and (self.latest_amcl is None):
                rclpy.spin_once(self, timeout_sec=0.05)
            self.spin_for(1.0)
            if self.latest_amcl is not None and self.gt is not None:
                wx, wy, _ = metrics.map_to_world(self.latest_amcl[1], self.latest_amcl[2], 0.0, self.al)
                if math.dist((wx, wy), self.gt[1:3]) < metrics.LOC_ERROR_THRESHOLD_M:
                    return attempt
        return 0

    def clear_costmaps(self):
        for c in self.clear:
            if c.wait_for_service(timeout_sec=2.0):
                fut = c.call_async(ClearEntireCostmap.Request())
                end = time.time() + 5
                while not fut.done() and time.time() < end:
                    rclpy.spin_once(self, timeout_sec=0.05)

    def write_trace(self, trial_id, t0, t_done):
        d = Path(self.args.trace_dir)
        d.mkdir(parents=True, exist_ok=True)
        with (d / f"{trial_id}_trace.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["t_s", "x", "y", "yaw", "amcl_x", "amcl_y", "cmd_v", "cmd_w", "scan_min_m", "collision_monitor"])
            for t, *rest in self.trace:
                w.writerow([round(t - t0, 2)] + [round(v, 3) if isinstance(v, float) else v for v in rest])
        with (d / f"{trial_id}_events.csv").open("w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["t_s", "kind", "detail"])
            for t, kind, detail in self.events:
                w.writerow([round(t - t0, 2), kind, detail])

    # --- one trial -------------------------------------------------------------------------------------------------------------------
    def run_trial(self, pair, repeat, trial_id, seed):
        s, g = pair["start"], pair["goal"]
        wall0, started = time.time(), datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.stop_robot()
        self.teleport(s["x"], s["y"], s["yaw"])
        self.spin_for(2.0)
        attempts = self.reset_localisation(s["x"], s["y"], s["yaw"])
        self.spin_for(2.0)
        self.clear_costmaps()
        self.track, self.amcl_err, self.contacts, self.bt = [], [], [], []
        self.trace, self.events, self.last_trace_t, self.cm_state = [], [], -1.0, ""
        self.guard_triggers = 0
        if attempts == 0:  # reset could not be verified: do not judge navigation on a bad start
            return {"trial_id": trial_id, "config": self.args.config, "world": self.args.world, "pair": pair["id"], "repeat": repeat, "seed": seed,
                    "success": 0, "failure_reason": "invalid_reset", "nav2_status": "NOT_SENT", "valid": 0, "reset_attempts": 5,
                    "sim_end_s": round(self.now(), 2), "wall_s": round(time.time() - wall0, 1), "started_utc": started}
        self.recording = True
        t0 = self.now()

        heading = math.atan2(g["y"] - s["y"], g["x"] - s["x"])
        gx, gy, gyaw = metrics.world_to_map(g["x"], g["y"], heading, self.al)
        goal = NavigateToPose.Goal()
        goal.pose.header.frame_id = "map"
        goal.pose.pose.position.x, goal.pose.pose.position.y = gx, gy
        goal.pose.pose.orientation.z, goal.pose.pose.orientation.w = quat(gyaw)

        self.nav.wait_for_server(timeout_sec=30.0)
        send = self.nav.send_goal_async(goal)
        wall_guard = time.time() + 20 * self.args.timeout + 30
        while not send.done() and time.time() < wall_guard:
            rclpy.spin_once(self, timeout_sec=0.05)
        handle = send.result()
        timed_out, nav2_status, t_done = False, "REJECTED", self.now()
        if handle is not None and handle.accepted:
            result = handle.get_result_async()
            while not result.done():
                rclpy.spin_once(self, timeout_sec=0.05)
                if self.now() - t0 > self.args.timeout or time.time() > wall_guard:
                    timed_out = True
                    break
            t_done = self.now()
            if timed_out:
                cancel = handle.cancel_goal_async()
                end = time.time() + 10
                while not cancel.done() and time.time() < end:
                    rclpy.spin_once(self, timeout_sec=0.05)
                nav2_status = "CANCELED"
            else:
                nav2_status = STATUS.get(result.result().status, str(result.result().status))
        self.stop_robot()
        self.spin_for(1.0)
        self.recording = False
        if self.args.trace_dir:
            self.write_trace(trial_id, t0, t_done)

        final = self.gt[1:3] if self.gt else (math.nan, math.nan)
        err = metrics.goal_error(final, (g["x"], g["y"]))
        success, reason = metrics.classify_outcome(nav2_status, timed_out, err, self.args.tolerance)
        errs = [e for _, e in self.amcl_err]
        emax, emean = metrics.localisation_stats(errs)
        row = {"trial_id": trial_id, "config": self.args.config, "world": self.args.world, "pair": pair["id"], "repeat": repeat, "seed": seed,
               "success": int(success), "failure_reason": reason, "nav2_status": nav2_status, "time_s": round(t_done - t0, 2),
               "path_m": round(metrics.path_length([(x, y) for _, x, y, _ in self.track]), 3), "final_error_m": round(err, 3), "valid": 1, "reset_attempts": attempts,
               "collisions": metrics.count_collisions(self.contacts), "recovery_events": metrics.count_recoveries(self.bt),
               "loc_err_max_m": round(emax, 3) if errs else "", "loc_err_mean_m": round(emean, 3) if errs else "",
               "loc_failure": int(metrics.localisation_failure(self.amcl_err, t_done)), "sim_end_s": round(self.now(), 2),
               "wall_s": round(time.time() - wall0, 1), "started_utc": started}
        if self.args.guard:
            row["guard_triggers"] = self.guard_triggers
        return row


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--world", required=True)
    ap.add_argument("--repeats", type=int, default=1, help="trials per pair (protocol change log (k): 1)")
    ap.add_argument("--seed", type=int, default=1, help="session seed (also passed to gz sim); trial seed = seed*1000 + trial index")
    ap.add_argument("--out", required=True)
    ap.add_argument("--pairs", default="configs/pairs.yaml")
    ap.add_argument("--alignment", default="configs/map_alignment.yaml")
    ap.add_argument("--only", default="", help="comma-separated pair ids to run (default all of the world)")
    ap.add_argument("--guard", action="store_true", help="the plan_flip_guard node is running: add a guard_triggers column")
    ap.add_argument("--trace-dir", default="", help="write a 5 Hz trace and an event log per trial here (diagnosis; off by default)")
    ap.add_argument("--timeout", type=float, default=metrics.TIMEOUT_S)
    ap.add_argument("--tolerance", type=float, default=metrics.SUCCESS_TOLERANCE_M)
    args = ap.parse_args(argv)

    pairs = yaml.safe_load(Path(args.pairs).read_text())["worlds"][args.world]
    if args.only:
        pairs = [p for p in pairs if p["id"] in args.only.split(",")]
    alignment = yaml.safe_load(Path(args.alignment).read_text())[args.world]
    trials = [(p, r) for p in pairs for r in range(1, args.repeats + 1)]
    random.Random(args.seed).shuffle(trials)  # fixed shuffle: machine drift is not confounded with pair order

    rclpy.init()
    runner = TrialRunner(args, alignment)
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    new = not out.exists()
    with out.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS + (["guard_triggers"] if args.guard else []))
        if new:
            w.writeheader()
        for i, (pair, rep) in enumerate(trials, 1):
            row = runner.run_trial(pair, rep, f"{args.config}-{pair['id']}-r{rep}", args.seed * 1000 + i)
            w.writerow(row)
            f.flush()  # one row per finished trial: a crash loses at most the trial in progress
            print(f"[{i}/{len(trials)}] {row['trial_id']}: success={row['success']} {row['failure_reason']} time={row['time_s']}s "
                  f"collisions={row['collisions']} recoveries={row['recovery_events']} wall={row['wall_s']}s", flush=True)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
