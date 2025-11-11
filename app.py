import cv2
from collections.abc import Callable
from typing import Any


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


def process_frame(frame: cv2.typing.MatLike) -> cv2.typing.MatLike:
    # Example processing: convert to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # here we could have something like read_board(frame), detect_hand(frame), etc. etc.
    # then based on that we could take moves with the robot arm

    return gray_frame


def main():
    start_capture_loop(process_frame)


if __name__ == "__main__":
    main()
