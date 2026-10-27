"""Simulation plus Nav2 (and SLAM Toolbox for mapping, or AMCL on a saved map).

Mapping:      ros2 launch nav_study_bringup nav.launch.py world:=world_a slam:=True
Navigation:   ros2 launch nav_study_bringup nav.launch.py world:=world_a map:=/path/world_a.yaml params_file:=/path/baseline.yaml
SLAM Toolbox, AMCL and Nav2 run with their published launch files; only the parameter file differs between configurations.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch_ros.actions import Node
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration


def generate_launch_description():
    here = get_package_share_directory('nav_study_bringup')
    nav2 = get_package_share_directory('nav2_bringup')
    args = ['world', 'headless', 'x', 'y', 'yaw', 'rtf', 'seed']
    return LaunchDescription([
        DeclareLaunchArgument('world', default_value='world_a'),
        DeclareLaunchArgument('headless', default_value='true'),
        DeclareLaunchArgument('x', default_value='0.0'),
        DeclareLaunchArgument('y', default_value='0.0'),
        DeclareLaunchArgument('yaw', default_value='0.0'),
        DeclareLaunchArgument('rtf', default_value='1'),
        DeclareLaunchArgument('seed', default_value='1'),
        DeclareLaunchArgument('slam', default_value='False'),
        DeclareLaunchArgument('map', default_value=''),
        DeclareLaunchArgument('params_file', default_value=''),
        DeclareLaunchArgument('use_rviz', default_value='false'),
        DeclareLaunchArgument('guard', default_value='false'),  # recovery configuration: start the plan_flip_guard node
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(here, 'launch', 'sim.launch.py')),
            launch_arguments={a: LaunchConfiguration(a) for a in args}.items()),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(os.path.join(nav2, 'launch', 'bringup_launch.py')),
            launch_arguments={
                'slam': LaunchConfiguration('slam'),
                'map': LaunchConfiguration('map'),
                'params_file': LaunchConfiguration('params_file'),
                'use_sim_time': 'True',
                'autostart': 'True',
            }.items()),
        Node(package='nav_study_trials', executable='plan_flip_guard', name='plan_flip_guard', output='screen',
             parameters=[{'use_sim_time': True}], condition=IfCondition(LaunchConfiguration('guard'))),
    ])
