"""Visualize the real AMR on laptop Ubuntu (NO motor commands).

Runs only robot_state_publisher. The existing Pi-side serial bridge,
/joint_states, /odom, and RPLIDAR are separate processes.
Do NOT run simultaneously with another rsp.launch.py or Gazebo simulation.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg = get_package_share_directory('my_amr')
    rsp_path = os.path.join(pkg, 'launch', 'rsp.launch.py')
    rviz_path = os.path.join(pkg, 'config', 'view_bot.rviz')
    rviz_arg = LaunchConfiguration('rviz')

    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='false',
                              description='Start RViz2 as well, using existing view_bot.rviz.'),
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(rsp_path),
            launch_arguments={
                'use_sim_time': 'false',
                'sim_mode': 'false',
                'use_ros2_control': 'false',
            }.items(),
        ),
        Node(
            package='rviz2', executable='rviz2', output='screen',
            arguments=['-d', rviz_path], condition=IfCondition(rviz_arg),
            parameters=[{'use_sim_time': False}],
        ),
    ])
