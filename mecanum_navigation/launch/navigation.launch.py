import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():

    pkg = get_package_share_directory('mecanum_navigation')

    nav2_params = os.path.join(pkg, 'config', 'nav2_params.yaml')

    # Start localization first (map server + AMCL)
    localization = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory('mecanum_localization'),
                'launch', 'localization.launch.py'
            )
        )
    )

    # Nav2 planner — global path planning (A*)
    planner = Node(
        package='nav2_planner',
        executable='planner_server',
        name='planner_server',
        output='screen',
        parameters=[nav2_params]
    )

    # Nav2 controller — local path planning (DWB holonomic)
    controller = Node(
        package='nav2_controller',
        executable='controller_server',
        name='controller_server',
        output='screen',
        parameters=[nav2_params]
    )

    # Nav2 behaviour server — recovery behaviours (spin, backup, wait)
    behaviours = Node(
        package='nav2_behaviors',
        executable='behavior_server',
        name='behavior_server',
        output='screen',
        parameters=[nav2_params]
    )

    # Nav2 BT navigator — orchestrates the full navigation task
    bt_navigator = Node(
        package='nav2_bt_navigator',
        executable='bt_navigator',
        name='bt_navigator',
        output='screen',
        parameters=[nav2_params]
    )

    # Lifecycle manager for Nav2 nodes
    lifecycle_manager = Node(
        package='nav2_lifecycle_manager',
        executable='lifecycle_manager',
        name='lifecycle_manager_navigation',
        output='screen',
        parameters=[{
            'use_sim_time': True,
            'autostart': True,
            'node_names': [
                'planner_server',
                'controller_server',
                'behavior_server',
                'bt_navigator',
            ],
        }]
    )

    return LaunchDescription([
        localization,
        TimerAction(period=10.0, actions=[
            planner,
            controller,
            behaviours,
            bt_navigator,
            lifecycle_manager,
        ])
    ])
