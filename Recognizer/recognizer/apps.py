import cv2

from recognizer.config import (
    DEFAULT_CAMERA_INDEX,
    FINGERS_COUNTER_WINDOW,
    FRAME_HEIGHT,
    FRAME_WIDTH,
    create_video_hands,
)
from recognizer.counting import count_fingers
from recognizer.detection import detect_hands_landmarks
from recognizer.serial_sender import SerialDigitSender


def _create_video_capture(camera_index):
    backends = [None]
    if hasattr(cv2, "CAP_DSHOW"):
        backends.append(cv2.CAP_DSHOW)

    for backend in backends:
        if backend is None:
            camera_video = cv2.VideoCapture(camera_index)
        else:
            camera_video = cv2.VideoCapture(camera_index, backend)

        camera_video.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        camera_video.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

        if camera_video.isOpened():
            return camera_video

        camera_video.release()

    return None


def _open_camera(camera_index):
    if camera_index is not None:
        camera_video = _create_video_capture(camera_index)
        if camera_video is None:
            raise RuntimeError(f"Could not open camera index {camera_index}")
        return camera_video

    attempted_indexes = []
    for candidate_index in range(4):
        attempted_indexes.append(candidate_index)
        camera_video = _create_video_capture(candidate_index)
        if camera_video is not None:
            return camera_video

    attempted = ", ".join(str(index) for index in attempted_indexes)
    raise RuntimeError(
        f"Could not open any camera. Tried indexes: {attempted}. "
        "If you know the correct device index, run with --camera-index N."
    )


def _show_frame(window_name, frame):
    cv2.imshow(window_name, frame)
    return cv2.waitKey(1) & 0xFF


def _draw_serial_status(frame, serial_sender, detected_digit):
    frame_height = frame.shape[0]
    sent_digit = serial_sender.last_sent_digit
    status_text = f"Serial: {serial_sender.port_label}"
    sent_text = f"STM32: {sent_digit if sent_digit is not None else '-'}"
    detected_text = f"Detected: {detected_digit}"

    cv2.putText(
        frame,
        status_text,
        (10, frame_height - 70),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
    )
    cv2.putText(
        frame,
        sent_text,
        (10, frame_height - 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 255),
        2,
    )
    cv2.putText(
        frame,
        detected_text,
        (10, frame_height - 10),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2,
    )


def run_finger_counter(
    camera_index=DEFAULT_CAMERA_INDEX,
    serial_port=None,
    serial_baudrate=115200,
    stable_frames=4,
):
    hands = create_video_hands()
    camera_video = None
    serial_sender = SerialDigitSender(
        port=serial_port,
        baudrate=serial_baudrate,
        stable_frames=stable_frames,
    )

    try:
        camera_video = _open_camera(camera_index)
        cv2.namedWindow(FINGERS_COUNTER_WINDOW, cv2.WINDOW_NORMAL)

        while camera_video.isOpened():
            ok, frame = camera_video.read()
            if not ok:
                continue

            frame = cv2.flip(frame, 1)
            frame, results = detect_hands_landmarks(frame, hands, display=False)
            frame, _, count = count_fingers(frame, results, display=False)
            detected_digit = sum(count.values())

            serial_sender.update(detected_digit)
            _draw_serial_status(frame, serial_sender, detected_digit)

            if _show_frame(FINGERS_COUNTER_WINDOW, frame) == 27:
                break
    finally:
        if camera_video is not None:
            camera_video.release()
        serial_sender.close()
        hands.close()
        cv2.destroyAllWindows()
