# robot_description

This package contains the URDF/Xacro robot model, sensor definitions, and Gazebo simulation launch files for a mecanum-wheeled robot.

## Overview

This package defines the complete robot model for a 4-wheeled mecanum drive platform, including its physical geometry, inertial properties, wheel friction behaviour, and a 360° GPU LiDAR sensor. It also provides launch files to bring up the `robot_state_publisher`, spawn the robot in a Gazebo simulation, and bridge topics between Gazebo and ROS 2.

## Robot Model Summary

| Property             | Value                                 |
| -------------------- | ------------------------------------- |
| **Drive type**       | Mecanum (4-wheel, omnidirectional)    |
| **Chassis**          | 0.35 × 0.35 × 0.15 m box, 5.0 kg      |
| **Wheel radius**     | 0.05 m                                |
| **Wheel width**      | 0.04 m, 1.5 kg each                   |
| **Wheel separation** | 0.40 m (lateral)                      |
| **Wheelbase**        | 0.45 m (longitudinal)                 |
| **Max acceleration** | ±1.5 m/s²                             |
| **Sensor**           | 360° GPU LiDAR, 10 Hz, range 0.3–12 m |

### Mecanum Wheel Friction Directions

The `fdir1` (friction direction 1) values are set per-wheel to emulate mecanum roller physics in Gazebo:

| Wheel       | Position (x, y) | `fdir1`  |
| ----------- | --------------- | -------- |
| Front Left  | +0.225, +0.20   | `1 -1 0` |
| Front Right | +0.225, −0.20   | `1  1 0` |
| Rear Left   | −0.225, +0.20   | `1  1 0` |
| Rear Right  | −0.225, −0.20   | `1 -1 0` |

## Package Structure

```
robot_description/
├── urdf/
│   ├── robot.urdf.xacro        # Includes core + lidar
│   ├── robot_core.xacro        # Chassis, wheels, and Gazebo plugins
│   ├── lidar.xacro             # LiDAR link, joint, and sensor plugin
│   └── inertial_macros.xacro   # Reusable inertia helper macros
├── config/
│   └── bridge_parameters.yaml  # ROS to Gazebo topic bridge config
├── launch/
│   ├── rsp.launch.py           # Robot State Publisher launch
│   └── spawn.launch.py         # Full simulation launch (Gazebo + robot + bridge)
├── package.xml
└── CMakeLists.txt
```

## URDF / Xacro Files

### `robot.urdf.xacro`

Top-level entry point. Simply includes `robot_core.xacro` and `lidar.xacro`.

### `robot_core.xacro`

Defines the full robot structure:

- `base_link` — root frame (inertial reference)
- `chassis` — orange box body, fixed to `base_link`
- Four wheels via the `wheel` macro — continuous joints along the Y axis
- **Gazebo plugins:**
  - `gz-sim-mecanum-drive-system` — handles `/cmd_vel` → wheel velocity, publishes `/odom` and `/tf`
  - `gz-sim-joint-state-publisher-system` — publishes `/joint_states`

### `lidar.xacro`

Defines the LiDAR sensor:

- `laser_frame` — fixed to the top-front of the chassis (`x=0.1, z=0.175` relative to chassis)
- 360° horizontal scan, 360 samples per revolution
- GPU accelerated (`gpu_lidar`), publishes to `/scan`

### `inertial_macros.xacro`

Two parameterised macros for computing inertia tensors:

| Macro               | Parameters                            | Use              |
| ------------------- | ------------------------------------- | ---------------- |
| `inertial_box`      | `mass`, `x`, `y`, `z`, `*origin`      | Chassis body     |
| `inertial_cylinder` | `mass`, `radius`, `length`, `*origin` | Wheels and LiDAR |

## Gazebo Bridge Topics

The `bridge_parameters.yaml` configures the `ros_gz_bridge` to relay the following topics between Gazebo and ROS 2:

| ROS 2 Topic     | Type                         | Direction |
| --------------- | ---------------------------- | --------- |
| `/clock`        | `rosgraph_msgs/msg/Clock`    | GZ → ROS  |
| `/cmd_vel`      | `geometry_msgs/msg/Twist`    | ROS → GZ  |
| `/scan`         | `sensor_msgs/msg/LaserScan`  | GZ → ROS  |
| `/tf`           | `tf2_msgs/msg/TFMessage`     | GZ → ROS  |
| `/joint_states` | `sensor_msgs/msg/JointState` | GZ → ROS  |
| `/odom`         | `nav_msgs/msg/Odometry`      | GZ → ROS  |

## Launch Files

### `rsp.launch.py` — Robot State Publisher only

Processes `robot.urdf.xacro` via `xacro` and starts `robot_state_publisher` with `use_sim_time: true`.

```bash
ros2 launch robot_description rsp.launch.py
```

### `spawn.launch.py` — Full simulation

Launches the complete simulation stack in order:

1. **RSP** (`rsp.launch.py`) — publishes robot description
2. **Gazebo** (`ros_gz_sim`) — loads `mecanum_classroom.sdf` from the `mecanum_world` package
3. **Spawn entity** — places the robot at `x=-1.907, y=-1.487`

Launches the complete simulation stack in order:

1. **RSP** (`rsp.launch.py`) — publishes robot description
2. **Gazebo** (`ros_gz_sim`) — loads `mecanum_classroom.sdf` from the `mecanum_world` package
3. **Spawn entity** — places the robot at `x=-1.907, y=-1.487`
4. **ROS–GZ Bridge** — starts `parameter_bridge` with `bridge_parameters.yaml`

```bash
ros2 launch robot_description spawn.launch.py
```

## Dependencies

- ROS 2 Jazzy
- `xacro`
- `robot_state_publisher`
- `ros_gz_sim`
- `ros_gz_bridge`
- `mecanum_world` package (provides the `mecanum_classroom.sdf` world file)

## Building

```bash
cd ~/ros2_ws
colcon build --packages-select robot_description
source install/setup.bash
```
