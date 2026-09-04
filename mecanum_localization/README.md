
# mecanum_localization

Package to localize the robot at (1,1) on the saved map

## Package Structure

```

racer_bringup/
├── launch/
│   ├── race.launch.py       # World + robot + energy node
├── config/
├── package.xml
└── CMakeLists.txt

```

## Launch Files

### race.launch.py
Launches the full simulation environment. Run this first.

**Launch order and timing**

| Time | Action |
|---|---|
| 0s | Gazebo starts with `race_track` world (via `ashbot_world`) |
| 8s | `racer_description/spawn.launch.py` — RSP + spawn robot |
| 19s | `energy_node` starts tracking |

**Arguments**

| Argument | Default | Options |
|---|---|---|
| `world` | `race_track` | `race_track`, `race_track_traffic_signs` |
| `drive_mode` | `diff` | `diff`, `ackermann` |

### race_run.launch.py
Launches only `racer_node` with `emulate_tty=True` so the keyboard
`S` key works. Run this in a **separate terminal** after `race.launch.py`
has finished spawning the robot.

## Quick Start

```bash
# Build
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash

# Terminal 1 — environment
ros2 launch racer_bringup race.launch.py

# Watch energy
ros2 topic echo /energy_status

# Watch debug logs
ros2 topic echo /rosout 2>/dev/null | grep -E "LAP|RACE|ENERGY"
```

## Other useful worlds

```bash
# Traffic signs world
ros2 launch racer_bringup race.launch.py world:=race_track_traffic_signs

# Ackermann steering
ros2 launch racer_bringup race.launch.py drive_mode:=ackermann
```

## Dependencies

| Package | Role |
|---|---|
| `ashbot_world` | Gazebo worlds (git submodule) |
| `racer_description` | URDF, spawn, bridges |
| `racer_control` | Wall follower, lap counter |
| `racer_monitor` | Energy tracking |
| `ros_gz_sim` | Gazebo ROS integration |

## Node Graph

```
Gazebo
  ├── /scan   → racer_node  (wall following)
  ├── /odom   → racer_node  (lap counter)
  │           → energy_node (distance tracking)
  │
racer_node
  └── /cmd_vel → Gazebo     (moves robot)
               → energy_node (start/stop detection)

energy_node
  └── /energy_status (live EU readout every 5s)
```