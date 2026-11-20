"""Robot state publisher for either the physical AMR or Gazebo Classic.

For physical hardware use sim_mode:=false use_sim_time:=false.
For Gazebo use sim_mode:=true use_sim_time:=true.
Does NOT command motors or open a serial port.
"""
import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, LaunchConfiguration, FindExecutable
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    package_share = get_package_share_directory('my_amr')
    xacro_file = os.path.join(package_share, 'description', 'robot.urdf.xacro')

    use_sim_time = LaunchConfiguration('use_sim_time')
    sim_mode = LaunchConfiguration('sim_mode')
    use_ros2_control = LaunchConfiguration('use_ros2_control')

    robot_description = ParameterValue(
        Command([
            FindExecutable(name='xacro'), ' ', xacro_file,
            ' sim_mode:=', sim_mode,
            ' use_ros2_control:=', use_ros2_control,
        ]),
        value_type=str,
    )

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time', default_value='false',
            description='Gazebo clock if true; wall time for physical robot.'),
        DeclareLaunchArgument(
            'sim_mode', default_value='false',
            description='True only for Gazebo Classic simulations.'),
        DeclareLaunchArgument(
            'use_ros2_control', default_value='false',
            description='Only relevant with sim_mode:=true.'),
        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            parameters=[{
                'robot_description': robot_description,
                'use_sim_time': ParameterValue(use_sim_time, value_type=bool),
            }],
        ),
    ])
