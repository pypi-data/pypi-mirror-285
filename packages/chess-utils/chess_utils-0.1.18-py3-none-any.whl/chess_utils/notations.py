from typing import Iterable
import chess

def sans2ucis(sans: Iterable[str]) -> Iterable[str]:
  board = chess.Board()
  for san in sans:
    move = board.parse_san(san)
    yield move.uci()
    board.push(move)

def ucis2sans(ucis: Iterable[str]) -> Iterable[str]:
  """Parses UCIs into SAN. Stops whenever it finds an illegal move/UCI."""
  board = chess.Board()
  for uci in ucis:
    try:
      move = chess.Move.from_uci(uci)
    except chess.InvalidMoveError:
      return
    if move not in board.legal_moves:
      return
    yield board.san(move)
    board.push(move)

def ucis2fens(ucis: Iterable[str], *, board_only: bool = False) -> Iterable[str]:
  """FENs *after* each UCI move (so, one output per input)."""
  board = chess.Board()
  for uci in ucis:
    move = chess.Move.from_uci(uci)
    board.push(move)
    fen = board.board_fen() if board_only else board.fen()
    yield fen

def moves2fens(moves: Iterable[chess.Move], *, board_only: bool = False) -> Iterable[str]:
  """FENs *after* each move (so, one output per input)."""
  board = chess.Board()
  for move in moves:
    board.push(move)
    fen = board.board_fen() if board_only else board.fen()
    yield fen

def sans2fens(sans: Iterable[str], *, board_only: bool = False) -> Iterable[str]:
  """FENs *after* each SAN move (so, one output per input)."""
  board = chess.Board()
  for san in sans:
    move = board.parse_san(san)
    board.push(move)
    fen = board.board_fen() if board_only else board.fen()
    yield fen