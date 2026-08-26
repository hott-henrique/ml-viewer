from __future__ import annotations

import random
import typing as t

from application.managers.environment.types import StepResult


Board = tuple[int, ...]  # 9 cells: 0 empty, 1 agent (X), -1 opponent (O)

_WIN_LINES = (
  (0, 1, 2),
  (3, 4, 5),
  (6, 7, 8),
  (0, 3, 6),
  (1, 4, 7),
  (2, 5, 8),
  (0, 4, 8),
  (2, 4, 6),
)


def _winner(board: Board) -> int | None:
  for a, b, c in _WIN_LINES:
    s = board[a] + board[b] + board[c]
    if s == 3:
      return 1
    if s == -3:
      return -1
  return None


def _is_full(board: Board) -> bool:
  return all(cell != 0 for cell in board)


class TicTacToeEnv:
  """Tic-tac-toe vs a random opponent. Agent plays X (1); opponent plays O (-1)."""

  def __init__(self, **params: t.Any) -> None:
    self._params = dict(params)
    self._board: Board = (0,) * 9
    self._rng = random.Random()

  @property
  def id(self) -> str:
    return "tic_tac_toe"

  def reset(self, *, seed: int | None = None) -> Board:
    if seed is not None:
      self._rng.seed(seed)
    self._board = (0,) * 9
    return self._board

  def legal_actions(self, state: t.Hashable | None = None) -> list[int]:
    board = self._board if state is None else t.cast(Board, state)
    return [i for i, cell in enumerate(board) if cell == 0]

  def step(self, action: t.Hashable) -> StepResult:
    idx = int(t.cast(int, action))
    board = list(self._board)

    if idx < 0 or idx > 8 or board[idx] != 0:
      raise ValueError(f"Illegal tic-tac-toe action: {action!r}")

    board[idx] = 1
    self._board = tuple(board)

    w = _winner(self._board)
    if w == 1:
      return StepResult(state=self._board, reward=1.0, terminated=True, truncated=False)
    if _is_full(self._board):
      return StepResult(state=self._board, reward=0.0, terminated=True, truncated=False)

    opp_moves = self.legal_actions(self._board)
    if opp_moves:
      opp = self._rng.choice(opp_moves)
      board = list(self._board)
      board[opp] = -1
      self._board = tuple(board)

    w = _winner(self._board)
    if w == -1:
      return StepResult(state=self._board, reward=-1.0, terminated=True, truncated=False)
    if _is_full(self._board):
      return StepResult(state=self._board, reward=0.0, terminated=True, truncated=False)

    return StepResult(state=self._board, reward=0.0, terminated=False, truncated=False)


TIC_TAC_TOE_REGISTRY_INSTANCE = {
  "module": "application.managers.environment.definitions.TicTacToe",
  "class": "TicTacToeEnv",
  "title": {"en_US": "Tic-Tac-Toe", "pt_BR": "Jogo da Velha"},
  "description": {
    "en_US": "Classic 3x3 tic-tac-toe against a random opponent. Agent plays X.",
    "pt_BR": "Jogo da velha 3x3 clássico contra oponente aleatório. O agente joga X.",
  },
  "params": [],
}
