"""Chart alignment"""

from enum import Enum


class ChartAlignment(Enum):
  """
  Chart Alignment
  """

  CENTER = 'center'
  LEFT = 'left'
  RIGHT = 'right'

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'ChartAlignment.{self.value}'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
