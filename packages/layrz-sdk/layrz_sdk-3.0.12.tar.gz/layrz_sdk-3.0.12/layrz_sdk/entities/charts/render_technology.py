"""Chart rendering technology / library"""

from enum import Enum


class ChartRenderTechnology(Enum):
  """
  Chart Alignment
  """

  CANVAS_JS = 'CANVAS_JS'
  GRAPHIC = 'GRAPHIC'
  SYNCFUSION_FLUTTER_CHARTS = 'SYNCFUSION_FLUTTER_CHARTS'
  FLUTTER_MAP = 'FLUTTER_MAP'
  APEX_CHARTS = 'APEX_CHARTS'
  FLUTTER = 'FLUTTER'

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'ChartRenderTechnology.{self.value}'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
