import os
import tempfile
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from std_msgs.msg import String
from voice_control_msgs.msg import VoiceIntent

rclpy = pytest.importorskip('rclpy')
pytest.importorskip('voice_control_msgs.msg')


@pytest.fixture(scope='module', autouse=True)
def ros_init():
    rclpy.init()
    yield
    rclpy.shutdown()

# udp_receiver_node (FileReaderNode)


def test_file_reader_lifecycle():
    from voice_control.udp_receiver_node import FileReaderNode
    node = FileReaderNode()
    node.publisher_ = MagicMock()

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write('go forward')
        tmp_path = f.name

    node.file_path = tmp_path
    # Test 1: File exists with content
    node.check_file()
    assert node.publisher_.publish.call_count == 1
    assert node.publisher_.publish.call_args[0][0].data == 'go forward'
    assert not os.path.exists(tmp_path)

    # Test 2: File is gone
    node.check_file()
    assert node.publisher_.publish.call_count == 1

    node.destroy_node()

# nlu_node (NLUNode)


@pytest.fixture
def nlu_node():
    with patch('os.path.exists', return_value=True), patch('joblib.load') as mock_load:
        model = MagicMock()
        mock_load.return_value = model
        from voice_control.nlu_node import NLUNode
        node = NLUNode()
        node.publisher_ = MagicMock()
        yield node, model
        node.destroy_node()


@pytest.mark.parametrize('pred, conf, expected', [
    ('FORWARD', 0.95, 'FORWARD'),  # Above threshold
    ('FORWARD', 0.50, 'IGNORE'),   # Below threshold
    ('STOP', 0.80, 'STOP'),        # Exact threshold acts as valid intent
])
def test_nlu_inference_thresholds(nlu_node, pred, conf, expected):
    node, model = nlu_node
    model.predict.return_value = [pred]
    mock_probas = np.array([[1 - conf, conf]])
    model.predict_proba.return_value = mock_probas

    node.text_callback(String(data='test string'))
    published = node.publisher_.publish.call_args[0][0]

    assert published.intent == expected


def test_nlu_model_exception_handling(nlu_node):
    node, model = nlu_node
    model.predict_proba.side_effect = RuntimeError('Simulated crash')
    node.text_callback(String(data='crash me'))

# voice_to_movement_node (VoiceCmdVelNode)


@pytest.fixture
def cmd_vel_node():
    from voice_control.voice_to_movement_node import VoiceCmdVelNode
    node = VoiceCmdVelNode()
    node.publisher_ = MagicMock()
    node.nav_client = MagicMock()
    yield node
    node.destroy_node()


def make_intent(intent: str) -> VoiceIntent:
    return VoiceIntent(intent=intent, raw_text='', confidence=1.0)


@pytest.mark.parametrize('intent, attr1, attr2, check_fn', [
    ('FORWARD', 'linear', 'x', lambda val: val > 0),
    ('BACKWARD', 'linear', 'x', lambda val: val < 0),
    ('STRAFE_LEFT', 'linear', 'y', lambda val: val > 0),
    ('STRAFE_RIGHT', 'linear', 'y', lambda val: val < 0),
    ('ROTATE_LEFT', 'angular', 'z', lambda val: val > 0),
    ('ROTATE_RIGHT', 'angular', 'z', lambda val: val < 0),
    ('STOP', 'linear', 'x', lambda val: val == 0.0),
])
def test_movement_kinematics(cmd_vel_node, intent, attr1, attr2, check_fn):
    cmd_vel_node.intent_callback(make_intent(intent))
    val = getattr(getattr(cmd_vel_node.current_twist, attr1), attr2)
    assert check_fn(val)


def test_speed_and_navigation_logic(cmd_vel_node):
    # Speed Limits
    initial_speed = cmd_vel_node.speed
    for _ in range(20):
        cmd_vel_node.intent_callback(make_intent('SPEED_UP'))
    assert cmd_vel_node.speed > initial_speed  # Max limit engaged

    for _ in range(40):
        cmd_vel_node.intent_callback(make_intent('SLOW_DOWN'))
    assert cmd_vel_node.speed > 0  # Min limit engaged

    # Navigation
    cmd_vel_node.intent_callback(make_intent('NAV_BASE'))
    cmd_vel_node.nav_client.send_goal_async.assert_called_once()

    # Unknown nav acts as ignore
    cmd_vel_node.nav_client.reset_mock()
    cmd_vel_node.intent_callback(make_intent('NAV_UNKNOWN'))
    cmd_vel_node.nav_client.send_goal_async.assert_not_called()
