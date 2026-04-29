from pathlib import Path

try:
    import mediapipe as mp
except ImportError as exc:
    raise ImportError(
        "Khong tim thay package 'mediapipe'. Hay cai dat bang 'pip install -r requirements.txt'."
    ) from exc

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_CAMERA_INDEX = 1
FRAME_WIDTH = 1280
FRAME_HEIGHT = 960

FINGERS_COUNTER_WINDOW = "Fingers Counter"

RIGHT_HAND = "RIGHT"
LEFT_HAND = "LEFT"
HAND_LABELS = (RIGHT_HAND, LEFT_HAND)
FINGER_NAMES = ("THUMB", "INDEX", "MIDDLE", "RING", "PINKY")


def _load_mediapipe_solutions():
    try:
        return mp.solutions.hands, mp.solutions.drawing_utils
    except AttributeError:
        pass

    try:
        from mediapipe.python.solutions import drawing_utils, hands

        return hands, drawing_utils
    except ImportError as exc:
        raise ImportError(
            "MediaPipe da duoc cai dat nhung khong co 'solutions'. "
            "Hay dung dung package 'mediapipe' va cai lai bang "
            + "'pip uninstall mediapipe -y && pip install -r requirements.txt'."
        ) from exc


mp_hands, mp_drawing = _load_mediapipe_solutions()


def create_video_hands():
    return mp_hands.Hands(
        static_image_mode=False,
        max_num_hands=2,
        min_detection_confidence=0.5,
    )
