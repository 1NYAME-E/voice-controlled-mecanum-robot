import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    package_name = 'robot_description'

    # Including the existing launch file
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(
                package_name), 'launch', 'rsp.launch.py'
        )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    # Including the gazebo launch file
    world_pkg = get_package_share_directory('mecanum_world')
    world_path = os.path.join(world_pkg, 'worlds', 'mecanum_classroom.sdf')

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(get_package_share_directory(
                'ros_gz_sim'), 'launch', 'gz_sim.launch.py')
        ),
        launch_arguments={
            'gz_args': f'-r -v 4 --render-engine ogre {world_path}'}.items(),
    )

    # Spawning the robot at the left north door facing south into classroom
    spawn_entity = Node(
        package='ros_gz_sim',
        executable='create',
        arguments=[
            '-topic', 'robot_description',
            '-name', 'mecanum_robot',
            '-x', '-1.90694',
            '-y',  '-1.48714',
            '-z',  '0.0',
            '-Y',  '0.0',
        ],
        output='screen'
    )

    # Enabling the bridging aspect
    bridge_params = os.path.join(get_package_share_directory(
        package_name), 'config', 'bridge_parameters.yaml')
    ros_gz_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        parameters=[{
            'use_sim_time': True
        }],
        arguments=[
            '--ros-args',
            '-p',
            f'config_file:={bridge_params}',
        ]
    )

    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        ros_gz_bridge,
    ])
