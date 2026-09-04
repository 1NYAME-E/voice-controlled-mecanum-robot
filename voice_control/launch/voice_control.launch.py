from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        # Including the udp receiver node (we used the file method for the simulation and network communication for physical implementation)
        Node(
            package='voice_control',
            executable='udp_receiver_node',
            name='udp_receiver_node',
            output='screen'
        ),

        # Including the NLU node
        Node(
            package='voice_control',
            executable='nlu_node',
            name='nlu_node',
            output='screen'
        ),

        # Including the voice to movement node
        Node(
            package='voice_control',
            executable='voice_to_movement_node',
            name='voice_to_movement_node',
            output='screen'
        )
    ])
