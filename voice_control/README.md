# voice_control

This ROS 2 package is for voice-controlled robot navigation and movement. It listens for transcribed speech commands, classifies them into intents using a trained natural language processing model, and translates them into robot motion commands or Nav2 navigation goals.

## Nodes

### `udp_receiver_node`

Polls a shared text file for new speech transcriptions and forwards them to the NLU pipeline.
The file is deleted after each successful read to prevent re-processing the same command.

> **Note:** The node class is named `FileReaderNode` internally. It was originally designed for UDP but was adapted to use a shared file for simulation; network-based input is used for physical deployment.

### `nlu_node`

Classifies raw transcribed text into a structured intent using a pre-trained scikit-learn model (`intent_model.pkl`).

| Intent                         | Meaning                                         |
| ------------------------------ | ----------------------------------------------- |
| `FORWARD`                      | Move forward                                    |
| `BACKWARD`                     | Move backward                                   |
| `STRAFE_LEFT` / `STRAFE_RIGHT` | Lateral movement                                |
| `ROTATE_LEFT` / `ROTATE_RIGHT` | In-place rotation                               |
| `STOP`                         | Halt all motion                                 |
| `SPEED_UP` / `SLOW_DOWN`       | Adjust current speed                            |
| `NAV_DOOR`                     | Navigate to first door waypoint                 |
| `NAV_SECOND_DOOR`              | Navigate to second door waypoint                |
| `NAV_TABLE`                    | Navigate to table waypoint                      |
| `NAV_DESK`                     | Navigate to desk waypoint                       |
| `NAV_BASE`                     | Navigate to base/home waypoint                  |
| `IGNORE`                       | Below confidence threshold — downstream ignores |

### `voice_to_movement_node`

Translates `VoiceIntent` messages into either direct velocity commands or Nav2 navigation goals.

| Item              | Detail                                                 |
| ----------------- | ------------------------------------------------------ |
| **Subscribes**    | `/voice_intent` (`voice_control_msgs/VoiceIntent`)     |
| **Publishes**     | `/cmd_vel` (`geometry_msgs/Twist`) at 10 Hz            |
| **Nav2 action**   | `navigate_to_pose` (`nav2_msgs/action/NavigateToPose`) |
| **Default speed** | `0.2 m/s`                                              |
| **Speed range**   | `0.1` – `2.0 m/s` in `0.5 m/s` steps                   |

The node continuously re-publishes the last `Twist` command at 10 Hz (`/cmd_vel` timer), so the robot keeps moving until a new intent arrives.

## Dependencies

- ROS 2 Jazzy
- `voice_control_msgs` (custom message package which must be built first)
- `nav2_msgs`
- `geometry_msgs`
- `std_msgs`
- Python: `joblib`, `scikit-learn`

Install Python dependencies:

```bash
pip install joblib scikit-learn
```

## Building

```bash
cd ~/ros2_ws
colcon build --packages-select voice_control_msgs voice_control
source install/setup.bash
```

## Running


Launch all three nodes together:

```bash
ros2 launch voice_control voice_control_launch.py
```

Or run nodes individually:

```bash
ros2 run voice_control udp_receiver_node
ros2 run voice_control nlu_node
ros2 run voice_control voice_to_movement_node
```

## Package Structure

```
voice_control/
├── voice_control/
│   ├── udp_receiver_node.py
│   ├── nlu_node.py
│   └── voice_to_movement_node.py
├── launch/
│   └── voice_control_launch.py
├── CMakeLists.txt
├── package.xml
└── README.md
```
