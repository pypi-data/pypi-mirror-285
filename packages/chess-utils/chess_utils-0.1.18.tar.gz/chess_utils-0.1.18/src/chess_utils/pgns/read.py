from typing import Iterable, TextIO, Sequence, overload, Literal
import chess.pgn

def read_pgns(pgn: TextIO) -> Iterable[chess.pgn.Game]:
  """Read all games from a PGN file"""
  while (game := chess.pgn.read_game(pgn)) is not None:
    yield game

def read_sans(game: chess.pgn.Game) -> Sequence[str]:
  """Read all moves from a game"""
  return [node.san() for node in game.mainline()]

def read_game(sans: Sequence[str]) -> chess.pgn.Game:
  """Board after a sequence of moves"""
  game = chess.pgn.Game()
  node = game
  for san in sans:
    node = node.add_main_variation(node.board().parse_san(san))
  return game

def follow_game(sans: Sequence[str]) -> tuple[chess.Board, str | None]:
  """Board after a sequence of moves. Returns the last illegal move if any"""
  board = chess.Board()
  for san in sans:
    try:
      board.push_san(san)
    except chess.IllegalMoveError:
      return board, san
  return board, None