"""Chart Data Serie"""

from typing import Any

from .data_type import ChartDataType
from .exceptions import ChartException
from .serie_type import ChartDataSerieType


class ChartDataSerie:
  """
  Chart Serie
  """

  def __init__(
    self,
    data: Any,
    color: str = '#000000',
    label: str = '',
    serie_type: ChartDataSerieType = ChartDataSerieType.LINE,
    data_type: ChartDataType = ChartDataType.NUMBER,
    dashed: bool = False,
  ) -> None:
    """
    Constructor

    Args
    ----
      data : List of data points.
      color : Color of the serie.
      label : Label of the serie.
      serie_type : Type of the serie. Only used for mixed range charts.
      data_type : Type of the data.
      dashed : If the serie should be dashed.
    """
    self.data = data

    if not isinstance(color, str):
      raise ChartException('color must be an instance of str')
    self.color = color

    if not isinstance(label, str):
      raise ChartException('label must be an instance of str')
    self.label = label

    if not isinstance(data_type, ChartDataType):
      raise ChartException('data_type must be an instance of ChartDataType')
    self.data_type = data_type

    if not isinstance(serie_type, ChartDataSerieType):
      raise ChartException('serie_type must be an instance of ChartDataSerieType')
    self.serie_type = serie_type or ChartDataSerieType.NONE

    if not isinstance(dashed, bool):
      raise ChartException('dashed must be an instance of bool')
    self.dashed = dashed
