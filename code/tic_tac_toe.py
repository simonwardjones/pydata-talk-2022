"""tic_tac_toe_board"""


import pathlib
import random
from abc import ABC
from dataclasses import dataclass
from enum import Enum
from itertools import chain, islice
from typing import Counter, Iterable, NamedTuple, Protocol

BOARD_TEMPLATE = """
┏━━━┳━━━┳━━━┓
┃ {} ┃ {} ┃ {} ┃
┣━━━╋━━━╋━━━┫
┃ {} ┃ {} ┃ {} ┃
┣━━━╋━━━╋━━━┫
┃ {} ┃ {} ┃ {} ┃
┗━━━┻━━━┻━━━┛
"""
SUPERSCRIPT_NUMBERS = "¹²³⁴⁵⁶⁷⁸⁹"
X_SYMBOL = "X"
O_SYMBOL = "O"


DATA_DIR = pathlib.Path(__file__).parent / "data"


class Move(NamedTuple):
    player: str
    position: int


class Command(Enum):
    undo = "undo"
    redo = "redo"
    quit = "quit"


class Board:
    def __init__(self):
        self.moves = []
        self.undo_moves = []
        self.state = [None] * 9

    def _rows(self) -> Iterable[Iterable[str | None]]:
        """Returns a iterable of rows of the board."""
        return (islice(self.state, i, i + 3) for i in range(0, 9, 3))

    def _columns(self) -> Iterable[Iterable[str | None]]:
        """Return a iterable of columns from rows"""
        return zip(*self._rows())

    def _diagonals(self) -> Iterable[Iterable[str | None]]:
        """Return an iterable of diagonals"""
        return ((self.state[i] for i in ids) for ids in [[0, 4, 8], [2, 4, 6]])

    def winner(self) -> str | None:
        """Return the winner of the game."""
        for group in chain(self._rows(), self._columns(), self._diagonals()):
            group_counter = Counter(group)
            if None not in group_counter and len(group_counter) == 1:
                return group_counter.most_common(1)[0][0]
        return None

    def has_winner(self) -> bool:
        """Return True if there is a winner."""
        return self.winner() is not None

    def is_full(self) -> bool:
        """Return True if the board is full."""
        return all(pos is not None for pos in self.state)

    def __repr__(self) -> str:
        """Return a string representation of the board."""

        return BOARD_TEMPLATE.format(
            *[
                SUPERSCRIPT_NUMBERS[i] if val is None else val
                for i, val in enumerate(self.state)
            ]
        )

    def get_available_positions(self) -> list[int]:
        """Return a list of available positions."""
        return [i + 1 for i, val in enumerate(self.state) if val is None]

    def make_move(self, move: Move):
        """Make a move on the board."""
        # track the move
        self.moves.append(move)
        self.undo_moves = []
        self.state[move.position - 1] = move.player

    def undo_move(self):
        """Undo the last move on the board."""
        if self.can_undo():
            # track the move
            move = self.moves.pop()
            self.undo_moves.append(move)
            self.state[move.position - 1] = None

    def redo_move(self):
        """Redo the last move on the board."""
        if self.can_redo():
            # track the move
            move = self.undo_moves.pop()
            self.moves.append(move)
            self.state[move.position - 1] = move.player

    def can_undo(self) -> bool:
        """Return True if there is a move to undo."""
        return len(self.moves) > 0

    def can_redo(self) -> bool:
        """Return True if there is a move to redo."""
        return len(self.undo_moves) > 0


@dataclass
class Player(ABC):
    symbol: str

    def get_action(self, ui: "UI", board: Board) -> Move | Command:
        """Return a move or a command."""
        raise NotImplementedError


class CLIPlayer(Player):
    def get_action(self, ui: "UI", board: Board) -> Command | Move:
        allowed_inputs = [str(pos) for pos in board.get_available_positions()]
        if board.can_undo():
            allowed_inputs.append("u")
        if board.can_redo():
            allowed_inputs.append("r")
        allowed_inputs.append("q")
        while True:
            value = ui.get_user_input(
                prompt=f"Player {self.symbol}, please enter your move (1-9): ",
                allowed_inputs=allowed_inputs,
            )
            if value == "u":
                return Command.undo
            elif value == "r":
                return Command.redo
            elif value == "q":
                return Command.quit

            return Move(self.symbol, int(value))


class RandomComputerPlayer(Player):
    def get_action(self, ui: "UI", board: Board) -> Command | Move:
        while True:
            value = ui.get_user_input(
                prompt=f"Press enter for Computer's move:",
                allowed_inputs=["", "u", "r", "q"],
            )
            if value == "u":
                return Command.undo
            elif value == "r":
                return Command.redo
            elif value == "q":
                return Command.quit

            random_position = random.choice(board.get_available_positions())
            return Move(self.symbol, random_position)


class UI(Protocol):
    def display_rules(self) -> None:
        raise NotImplementedError()

    def display_message(self, message: str) -> None:
        raise NotImplementedError()

    def get_user_input(self, prompt: str, allowed_inputs: list[str]) -> str:
        raise NotImplementedError()

    def get_number_of_players(self) -> int:
        raise NotImplementedError()


class CLI:
    def get_user_input(
        self, prompt: str, allowed_inputs: list[str] | None = None
    ) -> str:
        while True:
            value = input(prompt)
            if allowed_inputs is None or value in allowed_inputs:
                return value
            else:
                self.display_message(f"Invalid input")

    def get_number_of_players(self) -> int:
        n_players = self.get_user_input(
            prompt="Please select the number of players (1 or 2):",
            allowed_inputs=["1", "2"],
        )
        return int(n_players)

    def display_rules(self) -> None:
        self.display_message("Welcome to Tic Tac Toe!")
        self.display_message("Press u/U to undo a move.")
        self.display_message("Press r/R to redo a move.")
        self.display_message("Press q/Q to quit.")

    def display_message(self, message: str) -> None:
        print(message)


@dataclass
class TicTacToe:
    board: Board
    ui: UI
    current_player: int = 0

    def increment_player(self):
        self.current_player = (self.current_player + 1) % len(self.players)

    def set_players(self):
        n_players = int(
            self.ui.get_user_input(
                prompt="Please select the number of players (1 or 2):",
                allowed_inputs=["1", "2"],
            )
        )
        if n_players == 1:
            self.players = (
                CLIPlayer(X_SYMBOL),
                RandomComputerPlayer(O_SYMBOL),
            )
        else:
            self.players = (CLIPlayer(X_SYMBOL), CLIPlayer(O_SYMBOL))

    def play(self):
        self.ui.display_rules()
        self.set_players()
        while True:
            self.ui.display_message(self.board)
            if self.board.has_winner():
                self.ui.display_message(
                    f"\n 🎉 {self.board.winner()} wins! \n\nGame over."
                )
                return
            elif self.board.is_full():
                self.ui.display_message("It's a draw!")
                return

            player = self.players[self.current_player]
            action = player.get_action(ui=self.ui, board=self.board)

            if isinstance(action, Command):
                if action == Command.undo:
                    self.board.undo_move()
                    self.ui.display_message("Undid last move.")
                elif action == Command.redo:
                    self.board.redo_move()
                    self.ui.display_message("Undid last move.")
                elif action == Command.quit:
                    self.ui.display_message("Quitting game")
                    return
                else:
                    raise ValueError(f"Invalid Command {action}")
            else:
                self.board.make_move(action)
            self.increment_player()


if __name__ == "__main__":
    ui = CLI()
    game = TicTacToe(board=Board(), ui=ui)
    game.play()
