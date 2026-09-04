import pytest
from voice_control_msgs.msg import VoiceIntent


def test_defaults_and_types():
    msg = VoiceIntent()
    assert msg.intent == '' and isinstance(msg.intent, str)
    assert msg.raw_text == '' and isinstance(msg.raw_text, str)
    assert msg.confidence == 0.0 and isinstance(msg.confidence, float)


def test_field_assignment():
    msg = VoiceIntent()
    msg.intent = 'move_forward'
    msg.raw_text = 'avance tout droit'
    msg.confidence = 0.95

    assert msg.intent == 'move_forward'
    assert msg.raw_text == 'avance tout droit'
    assert msg.confidence == pytest.approx(0.95, rel=1e-5)


@pytest.mark.parametrize('conf_val', [0.0, 1.0, 0.5, 0.123456789, 1e-7, 1])
def test_confidence_boundaries_and_coercion(conf_val):
    msg = VoiceIntent()
    msg.confidence = conf_val

    assert isinstance(msg.confidence, float)
    assert msg.confidence == pytest.approx(float(conf_val), rel=1e-4)
