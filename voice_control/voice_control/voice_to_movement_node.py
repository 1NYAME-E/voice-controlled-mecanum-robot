#!/usr/bin/env python3
import rclpy
from geometry_msgs.msg import Twist
from nav2_msgs.action import NavigateToPose
from rclpy.action import ActionClient
from rclpy.node import Node
from voice_control_msgs.msg import VoiceIntent

MIN_SPEED = 0.1
MAX_SPEED = 2.0
SPEED_STEP = 0.5


class VoiceCmdVelNode(Node):
    def __init__(self):
        super().__init__('voice_to_movement_node')

        self.subscription = self.create_subscription(
            VoiceIntent, '/voice_intent', self.intent_callback, 10)

        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)

        self.current_twist = Twist()
        self.speed = 0.2

        self.timer = self.create_timer(0.1, self.timer_callback)

        self.nav_client = ActionClient(
            self, NavigateToPose, 'navigate_to_pose')
        self.waypoint_coordinates = {
            "NAV_DOOR": [-4.79323, -3.84942],
            "NAV_SECOND_DOOR": [-4.90086, 4.05501],
            "NAV_TABLE": [-4.30279, -3.6005],
            "NAV_DESK": [-5.0927, -0.0550461],
            "NAV_BASE": [2.98107, -4.02083]
        }

        self.get_logger().info("Ready to implement movement. Waiting for intents...")

    def send_nav_goal(self, intent, x, y):
        self.nav_client.wait_for_server()

        goal_msg = NavigateToPose.Goal()
        goal_msg.pose.header.frame_id = 'map'
        goal_msg.pose.header.stamp = self.get_clock().now().to_msg()
        goal_msg.pose.pose.position.x = float(x)
        goal_msg.pose.pose.position.y = float(y)
        goal_msg.pose.pose.orientation.w = 1.0

        self.nav_client.send_goal_async(goal_msg)

    def intent_callback(self, msg):
        intent = msg.intent
        self.get_logger().info(f"Node heard: '{intent}'")

        if intent.startswith("NAV_") and intent in self.waypoint_coordinates:
            self.current_twist = Twist()
            coords = self.waypoint_coordinates[intent]
            self.send_nav_goal(intent, coords[0], coords[1])
            return

        if intent == "SPEED_UP":
            self.speed = min(self.speed + SPEED_STEP, MAX_SPEED)
            self.get_logger().info(f"Speed increased to {self.speed:.1f}")
            self._reapply_speed()
            return

        if intent == "SLOW_DOWN":
            self.speed = max(self.speed - SPEED_STEP, MIN_SPEED)
            self.get_logger().info(f"Speed decreased to {self.speed:.1f}")
            self._reapply_speed()
            return

        new_twist = Twist()

        if intent == "FORWARD":
            new_twist.linear.x = self.speed
        elif intent == "BACKWARD":
            new_twist.linear.x = -self.speed
        elif intent == "STRAFE_LEFT":
            new_twist.linear.y = self.speed
        elif intent == "STRAFE_RIGHT":
            new_twist.linear.y = -self.speed
        elif intent == "ROTATE_LEFT":
            new_twist.angular.z = self.speed
        elif intent == "ROTATE_RIGHT":
            new_twist.angular.z = -self.speed
        elif intent == "STOP":
            pass
        elif intent == "IGNORE" or intent.startswith("NAV_"):
            self.get_logger().warn("Garbage command detected. Continuing previous action.")
            return

        self.current_twist = new_twist
        self.get_logger().info(
            f"Executing: {intent} at speed {self.speed:.1f}")

    def _reapply_speed(self):
        t = self.current_twist
        if t.linear.x != 0.0:
            t.linear.x = self.speed if t.linear.x > 0 else -self.speed
        elif t.linear.y != 0.0:
            t.linear.y = self.speed if t.linear.y > 0 else -self.speed
        elif t.angular.z != 0.0:
            t.angular.z = self.speed if t.angular.z > 0 else -self.speed

    def timer_callback(self):
        self.publisher_.publish(self.current_twist)


def main(args=None):
    rclpy.init(args=args)
    node = VoiceCmdVelNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
