from enum import Enum
import argparse
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


class BoardReader:
    class Marks(Enum):
        X = 1
        O = 2
        EMPTY = 3

    def __init__(self):
        self.previous_fill_ratios = [0.0] * 9

    def read_board(self, frame: cv2.typing.MatLike):
        squares = self.find_squares(frame)
        self.detect_single_square_change(frame, squares, ignore_squares=[])

    def print_board(self, marks):
        if not marks:
            return
        print("Detected Board:")
        root = len(marks) ** 0.5
        for i in range(int(root)):
            row = marks[i * int(root) : (i + 1) * int(root)]
            print(" | ".join(mark.name for mark in row))

    def visualize_squares(self, frame: cv2.typing.MatLike, squares):
        empty_board = np.zeros_like(frame)
        for i, sq in enumerate(squares):
            # draw squares with the data from frame onto the empty_board for visualization
            x, y, w, h = cv2.boundingRect(sq)
            empty_board[y : y + h, x : x + w] = frame[y : y + h, x : x + w]
            cv2.putText(
                empty_board,
                str(i),
                (x + 10, y + 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 0),
                2,
            )
        cv2.imshow("Board Detection", empty_board)

    def find_squares(self, frame: cv2.typing.MatLike):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        ret, thresh = cv2.threshold(blurred, 127, 255, 1)
        if not ret:
            raise ValueError("Thresholding failed")
        kernel = np.ones((5, 5), np.uint8)
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        contours, _ = cv2.findContours(closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        # visualize contours for debugging
        contour_img = np.zeros_like(frame)
        cv2.drawContours(contour_img, contours, -1, (0, 255, 0), 2)
        cv2.imshow("Contours", contour_img)

        # Image for showing all the polygons
        polygon_img = np.zeros_like(frame)
        # Image for showing detected squares, their areas, and their fill ratios
        square_img = np.zeros_like(frame)

        squares = []
        for contour in contours:
            epsilon = 0.03 * cv2.arcLength(contour, True)
            approx = cv2.approxPolyDP(contour, epsilon, True)
            cv2.drawContours(polygon_img, [approx], -1, (255, 0, 0), 2)

            # We are looking for rectangles
            if len(approx) != 4:
                continue

            area = cv2.contourArea(approx)
            bbox = cv2.boundingRect(approx)
            aspect_ratio = float(bbox[2] / bbox[3])
            # We are looking for squares of reasonable size
            if 0.8 < aspect_ratio < 1.2 and area > 4000:
                squares.append(approx)
                cv2.drawContours(square_img, [approx], -1, (0, 0, 255), 2)
                cv2.putText(
                    square_img,
                    f"{int(area)}",
                    (bbox[0], bbox[1] + 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 255, 0),
                    2,
                )

        cv2.imshow("Contour Polygons", polygon_img)
        cv2.imshow("Detected Squares", square_img)

        # We now have all squares, but we need to filter them to find the 9 board squares
        # We assume the board squares will have similar areas, so we are looking for
        # 9 squares with the least std deviation in area
        if len(squares) < 9:
            print("Not enough squares detected")
            return []

        square_areas = [cv2.contourArea(sq) for sq in squares]
        squares_with_areas = sorted(zip(squares, square_areas), key=lambda x: x[1])
        squares = [sq for sq, _ in squares_with_areas]
        sorted_areas = [area for _, area in squares_with_areas]
        start_idx = self.find_least_std_dev_of_9(sorted_areas)
        board_squares = squares[start_idx : start_idx + 9]

        # Sort board squares by their position (top-left to bottom-right)
        # We divide y by 50 to "group" by rows i.e. we don't want y to be
        # sensitive to small variations within a row
        def sort_key(sq):
            x, y = cv2.boundingRect(sq)[:2]
            return (y // 50) * 1000 + x

        board_squares = sorted(board_squares, key=sort_key)

        return board_squares

    def find_least_std_dev_of_9(self, values):
        # this could be O(n), but n is small so whatever
        min_std_dev = float("inf")
        best_start_index = 0
        for i in range(len(values) - 8):
            window = values[i : i + 9]
            std_dev = np.std(window)
            if std_dev < min_std_dev:
                min_std_dev = std_dev
                best_start_index = i
        return best_start_index

    def get_square_fill_ratios(self, frame: cv2.typing.MatLike, squares):
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (9, 9), 0)
        _, thresh = cv2.threshold(blurred, 127, 255, 1)

        fill_ratios = []
        for i, sq in enumerate(squares):
            mask = np.zeros((thresh.shape), dtype=np.uint8)
            cv2.fillPoly(mask, [sq], 255)
            cell = cv2.bitwise_and(thresh, thresh, mask=mask)
            x, y, w, h = cv2.boundingRect(sq)
            w = int(0.9 * w)
            h = int(0.9 * h)
            cell = cell[y : y + h, x : x + w]

            non_zero_count = cv2.countNonZero(cell)
            total_pixels = cell.size
            fill_ratio = non_zero_count / total_pixels
            print(f"Square {i}: Fill Ratio = {fill_ratio:.4f}")
            fill_ratios.append(fill_ratio)

        return fill_ratios
    
    def detect_single_square_change(self, frame: cv2.typing.MatLike, squares, ignore_squares):
        current_fill_ratios = self.get_square_fill_ratios(frame, squares)
        changes = [0.0] * len(current_fill_ratios)
        for i in range(len(current_fill_ratios)):
            if i in ignore_squares:
                continue
            changes[i] = abs(current_fill_ratios[i] - self.previous_fill_ratios[i])
        self.previous_fill_ratios = current_fill_ratios
        changes = sorted(enumerate(changes), key=lambda x: x[1], reverse=True)
        return changes[0][0]


class FrameSource(Enum):
    CAM = 1
    IP_CAM = 2
    IMG = 3


class RobotController:
    def __init__(self, camera_index=0, ip_camera_url=None, image_path=None):
        self.state = State()
        self.motion_detector = MotionDetector()
        self.board_reader = BoardReader()
        if image_path is not None:
            self.frame_source = FrameSource.IMG
            self.image_path = image_path
        elif ip_camera_url is not None:
            self.frame_source = FrameSource.IP_CAM
            self.ip_camera_url = ip_camera_url
        else:
            self.frame_source = FrameSource.CAM
            self.camera_index = camera_index

    def start_capture_loop(self):
        self.init_capture()

        while True:
            frame = self.get_frame()
            frame = self.process_frame(frame)

            # Display the resulting frame
            cv2.imshow("Video Feed", frame)

            self.take_action()

            # Break the loop on 'q' key press
            if cv2.waitKey(1) == ord("q"):
                break

        # Release the capture and close windows
        self.destroy_capture()
        cv2.destroyAllWindows()

    def init_capture(self):
        if self.frame_source == FrameSource.CAM:
            self.cap = cv2.VideoCapture(self.camera_index)
        elif self.frame_source == FrameSource.IP_CAM:
            self.cap = cv2.VideoCapture(self.ip_camera_url)
        elif self.frame_source == FrameSource.IMG:
            self.image = cv2.imread(self.image_path)

        if self.frame_source in (FrameSource.CAM, FrameSource.IP_CAM):
            if not self.cap.isOpened():
                raise ValueError("Error: Could not open video source.")

    def destroy_capture(self):
        if self.frame_source in (FrameSource.CAM, FrameSource.IP_CAM):
            self.cap.release()

    def get_frame(self):
        if self.frame_source == FrameSource.CAM:
            ret, frame = self.cap.read()
            if not ret:
                raise ValueError("Error: Could not read frame from camera.")
            return frame
        elif self.frame_source == FrameSource.IP_CAM:
            ret, frame = self.cap.read()
            if not ret:
                raise ValueError("Error: Could not read frame from IP camera.")
            return frame
        elif self.frame_source == FrameSource.IMG:
            return self.image.copy()

    def process_frame(self, frame: cv2.typing.MatLike) -> cv2.typing.MatLike:
        # Example processing: convert to grayscale
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Motion detection
        self.motion_detector.detect_motion(frame)
        self.state.detected_motion = (
            self.motion_detector.time_since_last_motion() < 1.0
        )  # 1 second threshold

        self.board_reader.read_board(frame)

        return gray_frame

    def take_action(self):
        if self.state.detected_motion:
            # Detected motion, not moving
            return

        # No motion detected, safe to move


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="Tic-Tac-Toe Robot Controller",
    )
    parser.add_argument(
        "--camera-index",
        type=int,
        default=0,
        help="Index of the camera to use (default: 0)",
    )
    parser.add_argument(
        "--ip-camera-url",
        type=str,
        default=None,
        help="URL of the IP camera to use (default: None)",
    )
    parser.add_argument(
        "--image-path",
        type=str,
        default=None,
        help="Path to an image file to use instead of a video source (default: None)",
    )
    args = parser.parse_args()

    # Example usage
    # python3 app.py --image-path board_images/filled.png
    # or just the following to use the default camera
    # python3 app.py
    controller = RobotController(
        camera_index=args.camera_index,
        ip_camera_url=args.ip_camera_url,
        image_path=args.image_path,
    )
    controller.start_capture_loop()
