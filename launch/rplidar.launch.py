"""Optional RPLIDAR driver launcher for the physical Raspberry Pi 4.

Start this separately from laptop RViz and the ESP32 UART bridge.
The LiDAR serial device is /dev/ttyUSB0, NOT the ESP32 /dev/serial0.
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue


def generate_launch_description():
    serial_port = LaunchConfiguration('serial_port')
    serial_baudrate = LaunchConfiguration('serial_baudrate')
    frame_id = LaunchConfiguration('frame_id')
    scan_mode = LaunchConfiguration('scan_mode')
    angle_compensate = LaunchConfiguration('angle_compensate')

    return LaunchDescription([
        DeclareLaunchArgument('serial_port', default_value='/dev/ttyUSB0'),
        DeclareLaunchArgument('serial_baudrate', default_value='115200'),
        DeclareLaunchArgument('frame_id', default_value='laser_frame'),
        DeclareLaunchArgument('scan_mode', default_value='Standard'),
        DeclareLaunchArgument('angle_compensate', default_value='true'),
        Node(
            package='rplidar_ros', executable='rplidar_composition',
            name='rplidar_node', output='screen',
            parameters=[{
                'serial_port': serial_port,
                'serial_baudrate': ParameterValue(serial_baudrate, value_type=int),
                'frame_id': frame_id,
                'scan_mode': scan_mode,
                'angle_compensate': ParameterValue(angle_compensate, value_type=bool),
            }],
        ),
    ])
