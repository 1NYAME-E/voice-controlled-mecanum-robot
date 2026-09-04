# voice_control_msgs

A ROS 2 message package providing custom message definitions for voice control interfaces.

## Overview

`voice_control_msgs` defines the message types used to communicate voice recognition results between nodes in the voice-controlled system. It is purposed to be used alongside a speech recognition node that produces intents.

## Messages

### `VoiceIntent.msg`

Represents a single voice recognition result.

| Field        | Type      | Description                                                                   |
| ------------ | --------- | ----------------------------------------------------------------------------- |
| `intent`     | `string`  | Parsed intent label (e.g. `"move_forward"`, `"stop"`, `"turn_left"`)          |
| `raw_text`   | `string`  | The raw transcribed text from the speech recogniser                           |
| `confidence` | `float32` | Confidence score in the range `[0.0, 1.0]`, where `1.0` is maximum confidence |

**Example published message:**

```
intent: "move_forward"
raw_text: "go straight ahead"
confidence: 0.93
```

## Dependencies

- ROS 2 Jazzy
- `std_msgs`

## Building

Clone this package into your ROS 2 workspace `src/` directory and build with colcon:

```bash
cd ~/ros2_ws
colcon build --packages-select voice_control_msgs
source install/setup.bash
```

## Usage

### In Python nodes

```python
from voice_control_msgs.msg import VoiceIntent

# Publishing
msg = VoiceIntent()
msg.intent = "stop"
msg.raw_text = "stop the robot"
msg.confidence = 0.98
publisher.publish(msg)

# Subscribing
def voice_callback(msg: VoiceIntent):
    if msg.confidence > 0.8:
        handle_intent(msg.intent)
```

## Package Structure

```
voice_control_msgs/
├── msg/
│   └── VoiceIntent.msg
├── CMakeLists.txt
├── package.xml
└── README.md
```│   └── VoiceIntent.msg
├── CMakeLists.txt
├── package.xml
└── README.md
```
