import random
from app import BoardReader
import cv2
import time

# change test_trajectory_real to test_trajectory_sim for simulation mode
# import test_trajectory_real as ttr
import test_trajectory_sim as ttr


X = 1
O = 2
EMPTY = 3


class TicTacToeGame:
    """
    A Tic-Tac-Toe game controller that manages game flow, board state,
    human move detection via camera input, and robot move execution(To be implemented).

    Human and robot players are represented as X=1, O=2, EMPTY=3.
    """

    def __init__(self, robot_playing=True):
        self.board = []
        self.next_player = X
        self.robot_player = X
        self.human_player = O

        if robot_playing:
            self.robot, self.rtb_model = ttr.new_robot()
            # set the robot to READY position
            ttr.set_to_ready_position(self.robot, self.rtb_model)
        else:
            self.robot = None
            self.rtb_model = None

        self.board_reader = BoardReader()

        self.cap = cv2.VideoCapture(4)
        if not self.cap.isOpened():
            print("Error: Could not open camera.")
            return None


    def get_user_move5(self) -> int:
        """
        Get user move 5 times in 1 second.
        """
        for _ in range(5):
            user_move = self.get_user_move()
            if user_move != -1:
                return user_move
            time.sleep(0.2)
        return -1

    def get_user_move(self) -> int:
        """
        Read the user's move from the camera.
        If invalid return -1, else return the move user made (0-8).

        This function:
        1. Captures one frame from the camera.
        2. Uses BoardReader to detect the board.
        3. Converts detected marks to our internal encoding (X=1, O=2, EMPTY=3).
        4. Compares with self.board and checks:
           - Only one cell changed.
           - That cell changed from EMPTY to human_player.
        5. Returns the move index (0-8) if valid, otherwise -1.
        """

        # i moved this outside because opening the camera everytime could be slow
        # # ---------- Capture one frame from default camera ----------
        # cap = cv2.VideoCapture(0)
        # if not cap.isOpened():
        #     print("Error: Could not open camera.")
        #     return -1

        ret, frame = self.cap.read()
        # cap.release()


        if not ret or frame is None:
            print("Error: Could not read frame from camera.")
            return -1
        # Optional: Visualize the captured image
        # else:
        #     cv2.imshow("Captured Frame", frame)
        #     cv2.waitKey(0)   # Press any key to close all windows
        #     cv2.destroyAllWindows()

        # ---------- Use BoardReader to detect squares and marks ----------
        squares = self.board_reader.find_squares(frame)
        if len(squares) != 9:
            print(f"Error: Expected 9 squares, but got {len(squares)}.")
            return -1

        marks = self.board_reader.detect_marks(frame, squares)
        if len(marks) != 9:
            print(f"Error: Expected 9 marks, but got {len(marks)}.")
            return -1

        new_board = []
        for m in marks:
            if m == BoardReader.Marks.X:
                new_board.append(X)
            elif m == BoardReader.Marks.O:
                new_board.append(O)
            else:
                new_board.append(EMPTY)

        print("Old board:")
        self.print_board()
        print("New board from camera:")
        self.print_board(new_board)

        # Safety check: make sure current internal board is valid
        if len(self.board) != 9:
            print("Error: internal board is not initialized correctly.")
            return -1

        # ---------- Compare new_board with self.board ----------
        diff_indices = []
        for i, (old, new) in enumerate(zip(self.board, new_board)):
            if old != new:
                diff_indices.append(i)

        # We expect exactly one changed cell
        if len(diff_indices) != 1:
            print(f"Invalid move: expected exactly 1 changed cell, got {len(diff_indices)}.")
            return -1

        move_idx = diff_indices[0]
        old_val = self.board[move_idx]
        new_val = new_board[move_idx]

        # The changed cell must be from EMPTY to human_player
        if old_val != EMPTY:
            print(f"Invalid move: cell {move_idx} was not EMPTY before (old={old_val}).")
            return -1

        if new_val != self.human_player:
            print(
                f"Invalid move: cell {move_idx} is {new_val}, "
                f"but human player is {self.human_player}."
            )
            return -1

        # Valid move detected
        print(f"User move detected at index: {move_idx}")
        return move_idx

    def start_game(self, use_camera=True):
        """
        Start a new game.
        """
        self.initialize_game()
        while not self.is_game_over():
            if self.next_player == self.human_player:
                print("======The current board status is:======")
                self.print_board()
                user_move = -1
                if use_camera:
                    user_move = self.get_user_move5()
                    input("Press the enter key to confirm your move")
                if user_move == -1:
                    print("Cannot detect a correct move from camera.")

                    # Let the user input a move from the console
                    while True:
                        print("Please make a move.")
                        print("======The current board status is:======")
                        self.print_board()
                        print("The indices of the board are:")
                        print("0|1|2")
                        print("3|4|5")
                        print("6|7|8")
                        user_input = input("Enter a number between 0-8: ")

                        try:
                            move = int(user_input)
                        except ValueError:
                            print("Please enter an integer between 0 and 8.")
                            continue

                        if move < 0 or move > 8:
                            print("Number must be between 0 and 8.")
                            continue

                        if self.board[move] != EMPTY:
                            print("That cell is not empty. Choose another one.")
                            continue

                        user_move = move
                        break
                self.board[user_move] = self.human_player

            elif self.next_player == self.robot_player:
                robot_move = self.get_random_move()
                if self.robot_player == X:
                    if self.robot is not None:
                        # TODO: check the indexing here
                        robot_move_traj = robot_move + 1  # different indexing from trajectory generation

                        # set to drawing mode
                        ttr.run_trajectory(self.robot, f"READY_to_DRAWING_MODE")
                        # move to the correct mode 
                        ttr.run_trajectory(self.robot, f"DRAWING_MODE_to_MODE_{robot_move_traj}")
                        # draw the cross
                        ttr.run_trajectory(self.robot, f"MODE_{robot_move_traj}_to_CROSS_{robot_move_traj}_to_MODE_{robot_move_traj}")
                        # move back to drawing mode
                        ttr.run_trajectory(self.robot, f"MODE_{robot_move_traj}_to_DRAWING_MODE")
                        # move from the drawing mode to READY mode
                        ttr.run_trajectory(self.robot, f"DRAWING_MODE_to_READY")

                # ASSUME ROBOT IS X
                # if self.robot_player == O:
                #     if self.robot is not None:
                #         self.robot.drawO(robot_move)
                self.board[robot_move] = self.robot_player
                print("Robot makes move: ", robot_move)
                if self.is_game_over():
                    break
            self.next_player = 3 - self.next_player
        
        self.cap.release()

    def initialize_game(self):
        """
        Initialize a new game.
        """
        self.board = [EMPTY] * 9
        if self.robot is not None:
            ttr.run_trajectory(self.robot, "READY_to_BOARD_to_READY")

        print("Human Player is O and Robot Player is X")

        # print("Choose the side you wanna play: X or O")
        # while 1:
        #     user_input = input()
        #     if user_input == 'X' or user_input == 'x':
        #         self.human_player = X
        #         self.robot_player = O
        #         break
        #     elif user_input == 'O' or user_input == 'o':
        #         self.human_player = O
        #         self.robot_player = X
        #         break
        #     else:
        #         print("Invalid input. Please input 'X' or 'O'.")

    def get_random_move(self):
        """
        Get a random move from an empty position.
        """
        empty_positions = [i for i, v in enumerate(self.board) if v == EMPTY]

        if not empty_positions:
            return None

        return random.choice(empty_positions)

    def is_game_over(self):
        """
        Return true iff a winner is found or no empty positions.
        """
        winner = self.find_winner()
        if winner != EMPTY:
            if self.robot_player == winner:
                print("Robot wins!")
            if self.human_player == winner:
                print("Congratulations! You win!")
            return True

        empty_positions = [i for i, v in enumerate(self.board) if v == EMPTY]

        if not empty_positions:
            print("Draw")
            return True

        return False

    def find_winner(self):
        """
        Return the winner of the game. If nobody wins, return EMPTY.
        """

        # the following comments describe the strike system used to generate the trajectories

        winner_positions = {
            # rows
            (0, 1, 2): ("HORIZONTAL", 3),
            (3, 4, 5): ("HORIZONTAL", 6),
            (6, 7, 8): ("HORIZONTAL", 9),

            # columns
            (0, 3, 6): ("VERTICAL", 1),
            (1, 4, 7): ("VERTICAL", 2),
            (2, 5, 8): ("VERTICAL", 3),

            # diagonals
            (0, 4, 8): ("DIAGONAL", 9),
            (2, 4, 6): ("DIAGONAL", 7),
        }

        winner = EMPTY
        for (i, j, k), (strike_type, strike_mode) in winner_positions.items():
            if self.board[i] == self.board[j] == self.board[k] != EMPTY:
                winner = self.board[i]

                # set to drawing mode
                ttr.run_trajectory(self.robot, f"READY_to_DRAWING_MODE")
                # move to the correct mode 
                ttr.run_trajectory(self.robot, f"DRAWING_MODE_to_MODE_{strike_mode}")
                # draw the strike
                ttr.run_trajectory(self.robot, f"MODE_{strike_mode}_to_{strike_type}_{strike_mode}")
                # move back to drawing mode
                ttr.run_trajectory(self.robot, f"{strike_type}_{strike_mode}_to_DRAWING_MODE")
                # move from the drawing mode to READY mode
                ttr.run_trajectory(self.robot, f"DRAWING_MODE_to_READY")

        return winner

    def print_board(self, new_board=None):
        """
        Print the current board in a 3x3 grid.
        self.board is a list of length 9 with values in {X, O, EMPTY}.
        """
        if new_board is None:
            board = self.board
        else:
            board = new_board

        symbol_map = {
            X: "X",
            O: "O",
            EMPTY: " ",
        }

        for row in range(3):
            # Get symbols for this row
            s0 = symbol_map[board[row * 3 + 0]]
            s1 = symbol_map[board[row * 3 + 1]]
            s2 = symbol_map[board[row * 3 + 2]]

            # Print like: O|  |
            print(f"{s0}|{s1}|{s2}")


if __name__ == "__main__":
    game = TicTacToeGame(robot_playing=True)
    game.start_game(use_camera=False)
    # game.start_game(use_camera=True)

