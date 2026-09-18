import os

from ament_index_python.packages import get_package_share_directory

from launch import LaunchDescription
from launch.actions import (
    IncludeLaunchDescription,
    DeclareLaunchArgument
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch.conditions import IfCondition

from launch_ros.actions import Node


def generate_launch_description():

    package_name = 'my_amr'

    rviz_config = os.path.join(
        get_package_share_directory(package_name),
        'config',
        'drive_robot.rviz'
    )

    # ---------------------------------------------------------
    # Launch argument:
    #
    # true  -> ros2_control
    # false -> gazebo diff_drive plugin
    # ---------------------------------------------------------

    use_ros2_control = LaunchConfiguration('use_ros2_control')
    world = LaunchConfiguration('world')


    # ---------------------------------------------------------
    # Robot State Publisher
    # ---------------------------------------------------------

    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory(package_name),
                'launch',
                'rsp.launch.py'
            )
        ]),
        launch_arguments={
            'use_sim_time': 'true',
            'use_ros2_control': use_ros2_control
        }.items()
    )


    # ---------------------------------------------------------
    # Gazebo
    # ---------------------------------------------------------

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([
            os.path.join(
                get_package_share_directory('gazebo_ros'),
                'launch',
                'gazebo.launch.py'
            )
        ]),
        launch_arguments={
            'world': world
        }.items()
    )


    # ---------------------------------------------------------
    # Spawn robot into Gazebo
    # ---------------------------------------------------------

    spawn_entity = Node(
        package='gazebo_ros',
        executable='spawn_entity.py',
        arguments=[
            '-topic', 'robot_description',
            '-entity', 'my_bot'
        ],
        output='screen'
    )


    # ---------------------------------------------------------
    # ros2_control controllers
    #
    # Chỉ chạy khi:
    # use_ros2_control = true
    # ---------------------------------------------------------

    diff_drive_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['diff_cont'],
        output='screen',
        condition=IfCondition(use_ros2_control)
    )


    joint_broad_spawner = Node(
        package='controller_manager',
        executable='spawner',
        arguments=['joint_broad'],
        output='screen',
        condition=IfCondition(use_ros2_control)
    )

    #---------------------------------------------------------
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        parameters=[{'use_sim_time': True}],
        output='screen'
    )

    # ---------------------------------------------------------
    # Launch
    # ---------------------------------------------------------

    return LaunchDescription([

        DeclareLaunchArgument(
            'use_ros2_control',
            default_value='true',
            description='Use ros2_control if true, Gazebo diff_drive if false'
        ),

        DeclareLaunchArgument(
            'world',
            default_value='',
            description='Gazebo world file'
        ),

        rsp,
        gazebo,
        spawn_entity,

        diff_drive_spawner,
        joint_broad_spawner,
        
        rviz
    ])