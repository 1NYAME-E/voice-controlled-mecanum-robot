import os
import subprocess
import xml.etree.ElementTree as ET

import pytest
import yaml


def _pkg_share() -> str:
    try:
        from ament_index_python.packages import get_package_share_directory
        return get_package_share_directory("robot_description")
    except Exception:
        return os.path.join(os.path.dirname(__file__), "..")


_EXPANDED_URDF: str | None = None


def _get_urdf() -> ET.Element:
    global _EXPANDED_URDF
    if _EXPANDED_URDF is None:
        urdf_path = os.path.join(_pkg_share(), "urdf", "robot.urdf.xacro")
        result = subprocess.run(["xacro", urdf_path],
                                capture_output=True, text=True)
        if result.returncode != 0:
            pytest.skip(f"xacro expansion failed: {result.stderr}")
        _EXPANDED_URDF = result.stdout
    return ET.fromstring(_EXPANDED_URDF)


class TestRobotURDF:
    def test_essential_links_and_joints(self):
        root = _get_urdf()
        links = {l.attrib["name"] for l in root.findall(".//link")}
        joints = {j.attrib["name"] for j in root.findall(".//joint")}

        expected_links = {"base_link", "chassis",
                          "laser_frame", "front_left_wheel", "rear_right_wheel"}
        assert expected_links.issubset(links), f"Missing links. Found: {links}"

        expected_joints = {"chassis_joint", "laser_joint",
                           "front_left_wheel_joint", "rear_right_wheel_joint"}
        assert expected_joints.issubset(
            joints), f"Missing joints. Found: {joints}"

    def test_wheel_symmetry(self):
        """Checks if front-left and rear-left wheels are symmetric along the X axis."""
        root = _get_urdf()
        fl_x = float(root.find(
            ".//joint[@name='front_left_wheel_joint']/origin").attrib["xyz"].split()[0])
        rl_x = float(root.find(
            ".//joint[@name='rear_left_wheel_joint']/origin").attrib["xyz"].split()[0])
        assert fl_x == pytest.approx(-rl_x, rel=1e-4)

    def test_lidar_configuration(self):
        root = _get_urdf()
        sensor = root.find(".//sensor[@name='laser']")
        assert sensor is not None, "Missing laser sensor in URDF"
        assert sensor.find("topic").text.strip() == "scan"
        assert int(sensor.find(".//horizontal/samples").text) == 360
        assert float(sensor.find("update_rate").text) == pytest.approx(10.0)

    def test_mecanum_plugin_configuration(self):
        root = _get_urdf()
        plugin = root.find(".//plugin[@name='gz::sim::systems::MecanumDrive']")
        assert plugin is not None, "MecanumDrive plugin not found"
        assert plugin.find("topic").text.strip() == "cmd_vel"
        assert plugin.find("front_left_joint").text.strip(
        ) == "front_left_wheel_joint"


class TestConfigAndLaunch:
    def test_bridge_parameters(self):
        path = os.path.join(_pkg_share(), "config", "bridge_parameters.yaml")
        if not os.path.exists(path):
            pytest.skip("bridge_parameters.yaml not found")

        with open(path) as f:
            bridge = yaml.safe_load(f)

        expected_topics = {
            "/cmd_vel": ("ROS_TO_GZ", "geometry_msgs/msg/Twist"),
            "/scan": ("GZ_TO_ROS", "sensor_msgs/msg/LaserScan"),
            "/odom": ("GZ_TO_ROS", "nav_msgs/msg/Odometry")
        }

        for entry in bridge:
            topic = entry.get("ros_topic_name")
            if topic in expected_topics:
                assert entry["direction"] == expected_topics[topic][0]
                assert entry["ros_type_name"] == expected_topics[topic][1]

    @pytest.mark.parametrize("launch_file, expected_strings", [
        ("rsp.launch.py", ["robot_state_publisher",
         "robot.urdf.xacro", "xacro", "use_sim_time"]),
        ("spawn.launch.py", ["rsp.launch.py", "mecanum_robot",
         "-1.90694", "mecanum_classroom", "ros_gz_bridge", "ogre"])
    ])
    def test_launch_file_contents(self, launch_file, expected_strings):
        path = os.path.join(_pkg_share(), "launch", launch_file)
        if not os.path.exists(path):
            pytest.skip(f"{launch_file} not found")

        content = open(path).read()
        for expected in expected_strings:
            assert expected in content, f"Expected '{expected}' in {launch_file}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
