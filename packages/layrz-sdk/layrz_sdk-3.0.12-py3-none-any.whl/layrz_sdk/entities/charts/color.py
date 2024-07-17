"""Chart alignment"""

from enum import Enum
from typing import Any


class ChartColor(Enum):
  """Chart color list, ideal to use to colorize the series"""

  RED = '#F44336'
  BLUE = '#2196F3'
  GREEN = '#4CAF50'
  PURPLE = '#9C27B0'
  ORANGE = '#FF9800'
  PINK = '#E91E63'
  TEAL = '#009688'
  AMBER = '#FFC107'
  CYAN = '#00BCD4'
  INDIGO = '#3F51B5'
  LIME = '#CDDC39'

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'ChartColor.{self.value}'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable


def get_color_list() -> Any:
  """Get all colors"""
  return [color.value for color in ChartColor]
