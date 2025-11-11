import cv2
import numpy as np
import time


class State:
    def __init__(self):
        self.detected_motion = True


class MotionDetector:
    def __init__(self):
        self.fgbg = cv2.createBackgroundSubtractorMOG2(
            history=100, varThreshold=25, detectShadows=True
        )
        self.last_motion_time = time.time()

    def detect_motion(self, frame: cv2.typing.MatLike) -> bool:
        fgmask = self.fgbg.apply(frame)
        motion = np.sum(fgmask > 200) > 2500  # Could be tuned
        if motion:
            self.last_motion_time = time.time()
        return motion

    def time_since_last_motion(self) -> float:
        return time.time() - self.last_motion_time


class RobotController:
    def __init__(self):
        self.state = State()
        self.motion_detector = MotionDetector()

    def start_capture_loop(self):
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

            frame = self.process_frame(frame)

            # Display the resulting frame
            cv2.imshow("Video Feed", frame)

            self.take_action()

            # Break the loop on 'q' key press
            if cv2.waitKey(1) == ord("q"):
                break

        # Release the capture and close windows
        cap.release()
        cv2.destroyAllWindows()

    def process_frame(self, frame: cv2.typing.MatLike) -> cv2.typing.MatLike:
        # Example processing: convert to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Motion detection
        self.motion_detector.detect_motion(frame)
        self.state.detected_motion = (
            self.motion_detector.time_since_last_motion() < 1.0
        )  # 1 second threshold

        # here we could have something like read_board(frame), detect_hand(frame), etc. etc.
        # then based on that we could take moves with the robot arm

        return gray_frame

    def take_action(self):
        if self.state.detected_motion:
            # Detected motion, not moving
            return

        # No motion detected, safe to move


if __name__ == "__main__":
    robot_controller = RobotController()
    robot_controller.start_capture_loop()
