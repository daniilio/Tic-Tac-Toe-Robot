import random

# change test_trajectory_real to test_trajectory_sim for simulation mode
import test_trajectory_sim as ttr
#import test_trajectory_sim as ttr
import targets_joint


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
        else:
            self.robot = None
            self.rtb_model = None



    def get_user_move5(self) -> int:
        """
        Get user move 5 times in 1 second.
        """
        return self.get_user_move()

    def get_user_move(self) -> int:
        ""
        move = input("User, enter a move (0-8)")
        move = int(move)
        if 0 <= move <= 8:
            return move
        return -1

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
                    input("Press the enter key to confirm your move")
                    user_move = self.get_user_move5()
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
                current_joint_pos =  self.rtb_model.q
                print(f"Robot's turn. Moving to {robot_move}, current joint position: {current_joint_pos}")
                if self.robot_player == X:
                    if self.robot is not None:
                        # TODO: check the indexing here
                        robot_move_traj = robot_move + 1  # different indexing from trajectory generation

                        # mode to drawing mode
                        print("Moving to DRAWING mode")
                        ttr.joint_trajectory(self.robot, targets_joint.DRAWING_MODE)

                        # move to the correct mode 
                        print("Moving from DRAWING -> GRID SLOT")
                        ttr.run_trajectory(self.robot, f"DRAWING_MODE_to_MODE_{robot_move_traj}")

                        # draw the cross
                        print("Drawing X on GRID SLOT")
                        ttr.run_trajectory(self.robot, f"MODE_{robot_move_traj}_to_CROSS_{robot_move_traj}_to_MODE_{robot_move_traj}")
                        
                        # move to camera mode
                        ttr.joint_trajectory(self.robot, targets_joint.CAMERA_MODE)

                        current_joint_pos =  self.rtb_model.q
                        print(f"Back to camera mode. Current joint angles: {current_joint_pos}")

                # ASSUME ROBOT IS X
                # if self.robot_player == O:
                #     if self.robot is not None:
                #         self.robot.drawO(robot_move)
                self.board[robot_move] = self.robot_player
                print("Robot makes move: ", robot_move)
                if self.is_game_over(): 
                    break
            self.next_player = 3 - self.next_player

    def initialize_game(self):
        """
        Initialize a new game.
        """
        self.board = [EMPTY] * 9
        if self.robot is not None:
            ttr.set_to_ready_position(self.robot, self.rtb_model)
            ttr.run_trajectory(self.robot, "READY_to_BOARD")
            ttr.set_to_ready_position(self.robot, self.rtb_model)

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
                ttr.joint_trajectory(self.robot, targets_joint.DRAWING_MODE)

                # move to the correct mode 
                ttr.run_trajectory(self.robot, f"DRAWING_MODE_to_MODE_{strike_mode}")

                # draw the strike
                ttr.run_trajectory(self.robot, f"MODE_{strike_mode}_to_{strike_type}_{strike_mode}")
                
                # Game is done, go to robot ready pose for now
                ttr.joint_trajectory(self.robot, targets_joint.READY)

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
    #game.start_game(use_camera=False)
    game.start_game(use_camera=True)

