"""Gazebo Classic simulation (ROS 2 Humble), not for the physical AMR.

Use a separate ROS_DOMAIN_ID for simulation when physical robot is on LAN.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, RegisterEventHandler
from launch.conditions import IfCondition
from launch.event_handlers import OnProcessExit
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('my_amr')
    use_ros2_control = LaunchConfiguration('use_ros2_control')
    world = LaunchConfiguration('world')
    rviz_enabled = LaunchConfiguration('rviz')
    rviz_file = os.path.join(pkg, 'config', 'drive_robot.rviz')

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(pkg, 'launch', 'rsp.launch.py')),
        launch_arguments={
            'use_sim_time': 'true',
            'sim_mode': 'true',
            'use_ros2_control': use_ros2_control,
        }.items(),
    )
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')),
        launch_arguments={'world': world}.items(),
    )
    spawn_entity = Node(
        package='gazebo_ros', executable='spawn_entity.py',
        arguments=['-topic', 'robot_description', '-entity', 'my_bot'],
        output='screen',
    )
    # Start ros2_control controllers only after spawn_entity finishes.
    diff_drive_spawner = Node(
        package='controller_manager', executable='spawner',
        arguments=['diff_cont'], output='screen',
        condition=IfCondition(use_ros2_control),
    )
    joint_broad_spawner = Node(
        package='controller_manager', executable='spawner',
        arguments=['joint_broad'], output='screen',
        condition=IfCondition(use_ros2_control),
    )
    spawn_controllers = RegisterEventHandler(
        OnProcessExit(target_action=spawn_entity,
                      on_exit=[joint_broad_spawner, diff_drive_spawner]),
    )
    rviz = Node(
        package='rviz2', executable='rviz2', name='rviz2',
        arguments=['-d', rviz_file],
        parameters=[{'use_sim_time': True}],
        condition=IfCondition(rviz_enabled), output='screen',
    )
    return LaunchDescription([
        DeclareLaunchArgument('use_ros2_control', default_value='true'),
        DeclareLaunchArgument('world', default_value=''),
        DeclareLaunchArgument('rviz', default_value='true'),
        rsp, gazebo, spawn_entity, spawn_controllers, rviz,
    ])
