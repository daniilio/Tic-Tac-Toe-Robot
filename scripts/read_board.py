# OpenCV code that can read the state of the tic-tac-toe board
from typing import List


def get_board_status(img) -> List[int]:
    """
    Analyze a Tic-Tac-Toe board image and return the state of all 9 grid cells.

    Args:
        img: A string representing an image file path, or alternatively
             a numpy.ndarray/opencv image object.

    Returns:
        List[int]: A list of length 9 representing the board status in row-major order:
                   [c0, c1, c2,
                    c3, c4, c5,
                    c6, c7, c8]
                   where each element is one of {0, 1, 2} corresponding to
                   empty, X, or O respectively.

    """
    pass

