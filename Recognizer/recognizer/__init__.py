__all__ = [
    "count_fingers",
    "detect_hands_landmarks",
]


def __getattr__(name):
    if name == "count_fingers":
        from recognizer.counting import count_fingers

        return count_fingers

    if name == "detect_hands_landmarks":
        from recognizer.detection import detect_hands_landmarks

        return detect_hands_landmarks

    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
