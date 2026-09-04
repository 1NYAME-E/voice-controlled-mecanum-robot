import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    pkg = get_package_share_directory('mecanum_localization')

    map_file = os.path.join(pkg, 'maps', 'classroom_mapp.yaml')
    amcl_params = os.path.join(pkg, 'config', 'amcl_params.yaml')

    # Bring up robot in the classroom world
    spawn_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('robot_description'),
                'launch', 'spawn.launch.py'
            )
        )
    )

    # Map server — loads the saved classroom map
    map_server = Node(
        package='nav2_map_server',
        executable='map_server',
        name='map_server',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'yaml_filename': map_file,
        }]
    )

    # AMCL — localises the robot within the loaded map
    amcl = Node(
        package='nav2_amcl',
        executable='amcl',
        name='amcl',
        output='screen',
        parameters=[amcl_params]
    )

    # Lifecycle manager — manages map_server and amcl startup
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_localization',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': ['map_server', 'amcl'],
        }]
    )

    return LaunchDescription([
        spawn_launch,
        TimerAction(period=5.0, actions=[
            map_server,
            amcl,
            lifecycle_manager,
        ])
    ])
