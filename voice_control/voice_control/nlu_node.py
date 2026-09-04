#!/usr/bin/env python3
# Making the necessary imports
import os

import joblib
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from voice_control_msgs.msg import VoiceIntent


class NLUNode(Node):
    def __init__(self):
        super().__init__('nlu_node')

        # Listens for raw text
        self.subscription = self.create_subscription(
            String, '/recognized_text', self.text_callback, 10)

        # Broadcast the math info to the robot
        self.publisher_ = self.create_publisher(
            VoiceIntent, '/voice_intent', 10)

        # Loading the ML Brain
        model_path = '/home/ubuntu/development/ros/ros2_ws/src/final-project-mecanum_3/src/voice_control/voice_control/intent_model.pkl'

        if os.path.exists(model_path):
            self.model = joblib.load(model_path)
            # self.get_logger().info("NLP Online. Waiting for commands...")
        else:
            self.get_logger().error(
                f" Could not find {model_path}! Confirm path.")
            self.model = None

        self.CONFIDENCE_THRESHOLD = 0.80

        # Fake coordinates to be replaced with actual ones
        self.waypoint_coordinates = {
            "NAV_FIRST_DOOR": [-4.0, 4.5],
            "NAV_SECOND_DOOR": [4.0, 4.5],
            "NAV_TABLE": [-1.5, 3.0],
            "NAV_DESK": [0.0, 4.0],
            "NAV_BASE": [5.5, -3.5]
        }

    def text_callback(self, msg):
        if self.model is None:
            return

        raw_text = msg.data
        self.get_logger().info(f" Heard: '{raw_text}'")

        try:
            # Predict probability and class
            probabilities = self.model.predict_proba([raw_text])
            confidence = probabilities.max()
            pred = self.model.predict([raw_text])[0]

            # Preparing the ROS 2 message
            intent_msg = VoiceIntent()
            intent_msg.raw_text = raw_text
            intent_msg.confidence = float(confidence)

            # Applying the threshold for reject irrelevant commands
            if confidence < self.CONFIDENCE_THRESHOLD:
                self.get_logger().warn(
                    f" Confidence too low ({confidence:.2f}). Ignoring.")
                intent_msg.intent = "IGNORE"
            else:
                intent_msg.intent = pred

                # Printing the navigation path provided an appropraite navigation goal has been mentioned
                # if pred in self.waypoint_coordinates:
                #    coords = self.waypoint_coordinates[pred]
                #    self.get_logger().info(
                #        f" Intent: {pred} | Sending Nav2 Goal: X:{coords[0]}, Y:{coords[1]} | Confidence: {confidence:.2f}")
                # else:
                #    self.get_logger().info(
                #        f" Intent: {pred} | Confidence: {confidence:.2f}")

            # Broadcast info to the robot
            self.publisher_.publish(intent_msg)

        except Exception as e:
            self.get_logger().error(f"Failed to process text: {e}")


def main(args=None):
    rclpy.init(args=args)
    node = NLUNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
