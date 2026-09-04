#!/usr/bin/env python3
# Making the necessary imports
import os

import rclpy
from rclpy.node import Node
from std_msgs.msg import String


class FileReaderNode(Node):
    def __init__(self):
        # Initializing the node
        super().__init__('udp_receiver_node')
        self.publisher_ = self.create_publisher(String, '/recognized_text', 10)
        self.file_path = "/home/ubuntu/development/ros/ros2_ws/src/final-project-mecanum_3/shared_command.txt"

        # self.get_logger().info("Able to read from the shared file. Waiting for commands...")

        # Checking the textfile every 0.2 seconds
        self.timer = self.create_timer(0.2, self.check_file)

    def check_file(self):
        if os.path.exists(self.file_path):
            try:
                # Reading the words
                with open(self.file_path, 'r') as f:
                    transcription = f.read().strip()

                if transcription:
                    # self.get_logger().info(
                    #    f"Read: '{transcription}'")

                    # Publishing to the NLP
                    msg = String()
                    msg.data = transcription
                    self.publisher_.publish(msg)

# Delete the file so we don't read the same command infinitely
                os.remove(self.file_path)

            except Exception as e:
                # Printing errors encountered
                self.get_logger().error(
                    f"Tried to read file, but hit an error: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = FileReaderNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
