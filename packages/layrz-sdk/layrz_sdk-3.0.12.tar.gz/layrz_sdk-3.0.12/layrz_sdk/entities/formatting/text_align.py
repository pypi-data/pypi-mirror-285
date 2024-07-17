"""Text alignment"""

from enum import Enum


class TextAlignment(Enum):
  """Text alignment enum definition"""

  CENTER = 'center'
  LEFT = 'left'
  RIGHT = 'right'
  JUSTIFY = 'justify'

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'TextAlignment.{self.value}'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
