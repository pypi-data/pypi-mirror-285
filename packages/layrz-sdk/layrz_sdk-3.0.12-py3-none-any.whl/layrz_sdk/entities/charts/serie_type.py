"""Chart Serie type"""

from enum import Enum


class ChartDataSerieType(Enum):
  """
  Chart data serie type
  """

  NONE = None
  LINE = 'line'
  AREA = 'area'
  SCATTER = 'scatter'

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'BroadcastStatus.{self.value}'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
