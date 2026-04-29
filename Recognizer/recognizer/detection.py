import cv2
import matplotlib.pyplot as plt

from recognizer.config import mp_drawing, mp_hands


def detect_hands_landmarks(image, hands, draw=True, display=True):
    """
    Detect hand landmarks on an image.
    """
    output_image = image.copy()
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = hands.process(image_rgb)

    if results.multi_hand_landmarks and draw:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                image=output_image,
                landmark_list=hand_landmarks,
                connections=mp_hands.HAND_CONNECTIONS,
                landmark_drawing_spec=mp_drawing.DrawingSpec(
                    color=(255, 255, 255),
                    thickness=2,
                    circle_radius=2,
                ),
                connection_drawing_spec=mp_drawing.DrawingSpec(
                    color=(0, 255, 0),
                    thickness=2,
                    circle_radius=2,
                ),
            )

    if display:
        plt.figure(figsize=[15, 15])
        plt.subplot(121)
        plt.imshow(image[:, :, ::-1])
        plt.title("Original Image")
        plt.axis("off")
        plt.subplot(122)
        plt.imshow(output_image[:, :, ::-1])
        plt.title("Output")
        plt.axis("off")

    return output_image, results
