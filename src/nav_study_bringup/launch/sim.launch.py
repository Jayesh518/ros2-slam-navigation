"""Start Gazebo with one of the study worlds, spawn the robot and run the bridge and robot_state_publisher.

Example:  scripts/env.sh ros2 launch nav_study_bringup sim.launch.py world:=test_arena headless:=true
Arguments: world (file name without .sdf in this package's worlds/), headless, x, y, yaw, rtf (Gazebo real-time factor).
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, OpaqueFunction
from launch.substitutions import Command, FindExecutable, LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def _gz(context):
    share = get_package_share_directory('nav_study_bringup')
    world = os.path.join(share, 'worlds', LaunchConfiguration('world').perform(context) + '.sdf')
    headless = LaunchConfiguration('headless').perform(context).lower() == 'true'
    rtf = LaunchConfiguration('rtf').perform(context)
    actions = [ExecuteProcess(
        cmd=['gz', 'sim', '-r', '-s', world] + (['--headless-rendering'] if headless else []),
        output='screen')]
    if not headless:
        actions.append(ExecuteProcess(cmd=['gz', 'sim', '-g'], output='screen'))
    if rtf != '1':
        actions.append(ExecuteProcess(
            cmd=['bash', '-c',
                 f'sleep 8; gz service -s /world/default/set_physics --reqtype gz.msgs.Physics '
                 f'--reptype gz.msgs.Boolean --timeout 3000 --req "real_time_factor: {rtf}"'],
            output='screen'))
    return actions


def generate_launch_description():
    robot_share = get_package_share_directory('nav_study_robot')
    urdf = os.path.join(robot_share, 'urdf', 'nav_study_robot.urdf.xacro')
    sdf = os.path.join(robot_share, 'urdf', 'nav_study_robot.sdf.xacro')
    bridge_cfg = os.path.join(robot_share, 'config', 'bridge.yaml')
    xacro = FindExecutable(name='xacro')
    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='test_arena'),
        DeclareLaunchArgument('headless', default_value='true'),
        DeclareLaunchArgument('x', default_value='0.0'),
        DeclareLaunchArgument('y', default_value='0.0'),
        DeclareLaunchArgument('yaw', default_value='0.0'),
        DeclareLaunchArgument('rtf', default_value='1'),
        OpaqueFunction(function=_gz),
        Node(package='robot_state_publisher', executable='robot_state_publisher', output='screen',
             parameters=[{'use_sim_time': True,
                          'robot_description': ParameterValue(Command([xacro, ' ', urdf]), value_type=str)}]),
        Node(package='ros_gz_sim', executable='create', output='screen',
             arguments=['-name', 'nav_study_robot',
                        '-string', Command([xacro, ' ', sdf]),
                        '-x', LaunchConfiguration('x'), '-y', LaunchConfiguration('y'), '-z', '0.01',
                        '-Y', LaunchConfiguration('yaw')]),
        Node(package='ros_gz_bridge', executable='parameter_bridge', output='screen',
             parameters=[{'config_file': bridge_cfg, 'expand_gz_topic_names': True, 'use_sim_time': True}]),
    ])
