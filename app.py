import cv2
from collections.abc import Callable
import numpy as np


def start_capture_loop(
    process_frame_callback: Callable[[cv2.typing.MatLike], cv2.typing.MatLike],
):
    cap = cv2.VideoCapture(0)  # For other cameras, change the index to 1, 2, etc.
    # cap = cv2.VideoCapture("rtsp://your_ip_camera_url") # Example for IP camera

    if not cap.isOpened():
        print("Error: Could not open video.")
        return

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        # Process the frame using the provided callback function
        frame = process_frame_callback(frame)

        # Display the resulting frame
        cv2.imshow("Video Feed", frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) == ord("q"):
            break

    # Release the capture and close windows
    cap.release()
    cv2.destroyAllWindows()


class MotionDetector:
    fgbg = cv2.createBackgroundSubtractorMOG2(
        history=300, varThreshold=25, detectShadows=True
    )

    def detect_motion(frame: cv2.typing.MatLike) -> bool:
        fgmask = MotionDetector.fgbg.apply(frame)
        motion = np.sum(fgmask > 0) > 5000  # Could be tuned
        return motion


def process_frame(frame: cv2.typing.MatLike) -> cv2.typing.MatLike:
    # Example processing: convert to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    motion = MotionDetector.detect_motion(frame)
    if motion:
        # Don't move the robot arm if motion is detected
        pass

    # here we could have something like read_board(frame), detect_hand(frame), etc. etc.
    # then based on that we could take moves with the robot arm

    return gray_frame


def main():
    start_capture_loop(process_frame)


if __name__ == "__main__":
    main()
