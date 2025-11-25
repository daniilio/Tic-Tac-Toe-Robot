import cv2
from main.app import BoardReader
import time

board_reader = BoardReader()
cap = cv2.VideoCapture(4)
if not cap.isOpened():
    print("Camera 4 not opened, trying 0")
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise SystemExit("Could not open any camera")

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        # small wait before retrying
        if cv2.waitKey(100) & 0xFF == ord("q"):
            break
        continue

    # show raw feed for debugging
    cv2.imshow("Raw Camera", frame)

    # run board detection / visualization (BoardReader should imshow its annotated window)
    board_reader.read_board(frame)

    # refresh windows and allow quitting with 'q'
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

#