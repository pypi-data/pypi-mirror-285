"""Chart Data type"""

from enum import Enum


class ChartDataType(Enum):
  """
  Chart Data Type
  """

  STRING = 'STRING'
  DATETIME = 'DATETIME'
  NUMBER = 'NUMBER'

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'ChartDataType.{self.value}'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
