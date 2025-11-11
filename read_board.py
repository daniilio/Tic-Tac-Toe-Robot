"""
============================================================
Tic-Tac-Toe Board State Reader
============================================================

    Script for capturing an image of a Tic-Tac-Toe board and 
    analyzing the state of the game.

Author: Daniil Trukhin, ...
Date:   November 10, 2025
============================================================
"""

import cv2
import numpy as np

def main():
    board_image = cv2.imread("tictactoe.png")
    if board_image is None:
        print("Error: Could not open image.")
        return
    
    # save copy of the original image
    board_image_copy = board_image.copy()

    grey_scale = cv2.cvtColor(board_image, cv2.COLOR_BGR2GRAY)
    # reduce noise
    grey_scale = cv2.medianBlur(grey_scale, 5)

    # detect circles
    circles = cv2.HoughCircles(
        grey_scale,
        cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=100,
        param1=100,
        param2=40,
        minRadius=30,
        maxRadius=60
    )

    if circles is not None:
        circles = np.uint16(np.around(circles))
        for (x, y, r) in circles[0, :]:
            # draw circle outline
            cv2.circle(board_image_copy, (x, y), r, (0, 255, 0), 2)
            # draw centre point
            cv2.circle(board_image_copy, (x, y), 2, (0, 0, 255), 3)

    edges = cv2.Canny(grey_scale, 50, 150)

    lines = cv2.HoughLinesP(
        edges,        # image
        1,            # rho
        np.pi/180,    # theta
        50,           # threshold
        None,         # placeholder for lines
        80,           # minLineLength
        10            # maxLineGap
    )

    diagonal_lines = []

    height, width = grey_scale.shape
    margin = width // 12  # adjust based on your image

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]

            # ignore lines too close to edges (likely grid)
            if (x1 < margin or x1 > width - margin or x2 < margin or x2 > width - margin):
                continue
            if (y1 < margin or y1 > height - margin or y2 < margin or y2 > height - margin):
                continue

            if x2 - x1 == 0:
                slope = float('inf')
            else:
                slope = (y2 - y1) / (x2 - x1)
            
            # Keep only lines with slope roughly +1 or -1
            if 0.75 < abs(slope) < 1.25:
                diagonal_lines.append((x1, y1, x2, y2))

    if diagonal_lines:
        for i in range(len(diagonal_lines)):
            for j in range(i + 1, len(diagonal_lines)):
                (x1, y1, x2, y2) = diagonal_lines[i]
                (x3, y3, x4, y4) = diagonal_lines[j]

                # compute angle between lines
                v1 = np.array([x2 - x1, y2 - y1])
                v2 = np.array([x4 - x3, y4 - y3])
                angle = np.degrees(np.arccos( np.dot(v1, v2) / ( np.linalg.norm(v1) * np.linalg.norm(v2) ) ) )

                if 80 < angle < 100:  # roughly perpendicular
                    cv2.line(board_image_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.line(board_image_copy, (x3, y3), (x4, y4), (0, 255, 0), 2)
                    
                    # draw intersection
                    a1, b1, c1 = y2 - y1, x1 - x2, (y2 - y1)*x1 + (x1 - x2)*y1
                    a2, b2, c2 = y4 - y3, x3 - x4, (y4 - y3)*x3 + (x3 - x4)*y3
                    det = a1*b2 - a2*b1
                    if det != 0:
                        ix = int((b2*c1 - b1*c2) / det)
                        iy = int((a1*c2 - a2*c1) / det)
                        cv2.circle(board_image_copy, (ix, iy), 5, (0,0,255), -1)

    # display the result
    cv2.imshow("Tic-Tac-Toe Board", board_image_copy)

    while True:
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break

    # Close display window
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
