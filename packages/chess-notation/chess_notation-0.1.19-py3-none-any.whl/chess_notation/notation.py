from typing import NamedTuple, get_args, Iterable, Sequence
import random
import chess
from .language import Language, LANGUAGES, translate
from .styles import Styles, style, UNIQ_PAWN_CAPTURES, UNIQ_PIECE_CAPTURES, \
  Check, Mate, Castle, PawnCapture, PieceCapture, CapturedPiece

class Notation(NamedTuple):
  language: Language
  styles: Styles

def random_notation() -> Notation:
  lang = random.choice(LANGUAGES)
  check = random.choice(get_args(Check))
  mate = random.choice(get_args(Mate))
  castle = random.choice(get_args(Castle))
  pawn = random.choice(get_args(PawnCapture))
  piece = random.choice(get_args(PieceCapture))
  styles = Styles(castle=castle, check=check, mate=mate, pawn_capture=pawn, piece_capture=piece)
  return Notation(language=lang, styles=styles)

def uniq_random_notation(languages: Sequence[Language] = ['EN']) -> Notation:
  """Random notation using informational-unique styles (i.e. styles that can't be univocally mapped to each other)"""
  styles = Styles(
    pawn_capture=random.choice(UNIQ_PAWN_CAPTURES),
    piece_capture=random.choice(UNIQ_PIECE_CAPTURES)
  )
  lang = random.choice(languages)
  return Notation(language=lang, styles=styles)

def simple_styled(sans: Iterable[str], notation: Notation) -> Iterable[str]:
  for move in sans:
    yield translate(style(move, notation.styles), notation.language)

def captured_piece(board: chess.Board, move: chess.Move) -> CapturedPiece | None:
  """The piece captured by `move` on `board` (or `None`)"""
  type = board.piece_type_at(move.to_square)
  if type is not None:
    return chess.piece_symbol(type).upper() # type: ignore

def validated_styled(sans: Iterable[str], notation: Notation) -> Iterable[str]:
  board = chess.Board()
  for san in sans:
    move = board.parse_san(san)
    piece = captured_piece(board, move)
    board.push(move)
    yield translate(style(san, notation.styles, piece), notation.language)

def styled(sans: Iterable[str], notation: Notation) -> Iterable[str]:
  if notation.styles.pawn_capture == 'PxN' or notation.styles.piece_capture == 'NxN':
    yield from validated_styled(sans, notation)
  else:
    yield from simple_styled(sans, notation)