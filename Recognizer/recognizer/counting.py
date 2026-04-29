import cv2
import matplotlib.pyplot as plt

from recognizer.config import FINGER_NAMES, HAND_LABELS, mp_hands


def create_default_count():
    return {hand_label: 0 for hand_label in HAND_LABELS}


def create_default_finger_statuses():
    return {
        f"{hand_label}_{finger_name}": False
        for hand_label in HAND_LABELS
        for finger_name in FINGER_NAMES
    }


def count_fingers(image, results, draw=True, display=True):
    """
    Count raised fingers for each detected hand.
    """
    _, width, _ = image.shape
    output_image = image.copy()
    count = create_default_count()
    fingers_statuses = create_default_finger_statuses()

    if not results.multi_hand_landmarks or not results.multi_handedness:
        if draw:
            cv2.putText(
                output_image,
                " Total Fingers: ",
                (10, 25),
                cv2.FONT_HERSHEY_COMPLEX,
                1,
                (20, 255, 155),
                2,
            )
            cv2.putText(
                output_image,
                "0",
                (width // 2 - 150, 240),
                cv2.FONT_HERSHEY_SIMPLEX,
                8.9,
                (20, 255, 155),
                10,
                10,
            )
        if display:
            plt.figure(figsize=[10, 10])
            plt.imshow(output_image[:, :, ::-1])
            plt.title("Output Image")
            plt.axis("off")
        return output_image, fingers_statuses, count

    fingers_tips_ids = [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP,
    ]

    for hand_index, hand_info in enumerate(results.multi_handedness):
        hand_label = hand_info.classification[0].label.upper()
        hand_landmarks = results.multi_hand_landmarks[hand_index]

        for tip_index in fingers_tips_ids:
            finger_name = tip_index.name.split("_")[0]
            if hand_landmarks.landmark[tip_index].y < hand_landmarks.landmark[tip_index - 2].y:
                fingers_statuses[f"{hand_label}_{finger_name}"] = True
                count[hand_label] += 1

        thumb_tip_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP].x
        thumb_mcp_x = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP - 2].x

        if (hand_label == "RIGHT" and thumb_tip_x < thumb_mcp_x) or (
            hand_label == "LEFT" and thumb_tip_x > thumb_mcp_x
        ):
            fingers_statuses[f"{hand_label}_THUMB"] = True
            count[hand_label] += 1

    if draw:
        cv2.putText(
            output_image,
            " Total Fingers: ",
            (10, 25),
            cv2.FONT_HERSHEY_COMPLEX,
            1,
            (20, 255, 155),
            2,
        )
        cv2.putText(
            output_image,
            str(sum(count.values())),
            (width // 2 - 150, 240),
            cv2.FONT_HERSHEY_SIMPLEX,
            8.9,
            (20, 255, 155),
            10,
            10,
        )

    if display:
        plt.figure(figsize=[10, 10])
        plt.imshow(output_image[:, :, ::-1])
        plt.title("Output Image")
        plt.axis("off")

    return output_image, fingers_statuses, count
