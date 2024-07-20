from typing import Iterable
from haskellian import Iter
from .types import PGNHeaders

def export_headers(headers: PGNHeaders) -> str:
  keys = ['Event', 'Site', 'Date', 'Round', 'White', 'Black', 'Result']
  dct = headers.model_dump(exclude_none=True)
  return '\n'.join(f'[{key} "{value}"]' for key in keys if (value := dct.get(key)) is not None)


def export_pair(entry: tuple[int, tuple[str, ...]]) -> str:
  idx, moves = entry
  return f'{idx + 1}. {" ".join(moves)}'

def export_moves(moves: Iterable[str]) -> str:
  pairs = Iter(moves).batch(2).enumerate().map(export_pair)
  return ' '.join(pairs)

def export_pgn(moves: Iterable[str], headers: PGNHeaders, end_comment: str | None = None) -> str:
  comment = ' {' + end_comment + '}' if end_comment else ''
  return f'{export_headers(headers)}\n\n{export_moves(moves)}{comment} {headers.Result or "*"}\n'