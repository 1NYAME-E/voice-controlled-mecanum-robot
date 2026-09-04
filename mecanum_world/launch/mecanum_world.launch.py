"""
launch/mecanum_world.launch.py
Starts Gazebo Harmonic with the mecanum obstacle course world.
ROS 2 Jazzy  |  Gazebo Harmonic  |  ros_gz_sim

Usage:
  ros2 launch mecanum_world mecanum_world.launch.py
  ros2 launch mecanum_world mecanum_world.launch.py gz_args:="-r -v 4"
"""

import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import (
    DeclareLaunchArgument,
    IncludeLaunchDescription,
    OpaqueFunction,
    SetEnvironmentVariable,
)
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():

    pkg_mecanum_world = get_package_share_directory("mecanum_world")
    world_file = os.path.join(
        pkg_mecanum_world, "worlds", "mecanum_classroom.sdf"
    )

    declare_gz_args = DeclareLaunchArgument(
        "gz_args",
        default_value=f"-r {world_file}",
        description="Extra arguments forwarded to gz sim",
    )
    declare_use_sim_time = DeclareLaunchArgument(
        "use_sim_time",
        default_value="true",
        description="Use simulation (Gazebo) clock.",
    )
    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"]
            )
        ),
        launch_arguments={"gz_args": LaunchConfiguration("gz_args")}.items(),
    )
    ros_gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        name="ros_gz_bridge",
        output="screen",
        parameters=[{"use_sim_time": LaunchConfiguration("use_sim_time")}],
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            # ---- Uncomment and adapt once your robot is ready ----
             "/cmd_vel@geometry_msgs/msg/Twist]gz.msgs.Twist",
             "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
             "/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V",
             "/scan@sensor_msgs/msg/LaserScan[gz.msgs.LaserScan",
        ],
    )
    return LaunchDescription(
        [
            declare_gz_args,
            declare_use_sim_time,
            gz_sim,
            ros_gz_bridge,
        ]
    )
