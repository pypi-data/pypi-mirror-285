"""Charts entities"""

from .data_type import ChartDataType


class ChartConfiguration:
  """
  Chart configuration
  """

  def __init__(self, name: str, description: str) -> None:
    """Constructor"""
    self.name = name
    self.description = description

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'ChartConfiguration(name="{self.name}")'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable


class AxisConfig:
  """Axis configuration"""

  def __init__(
    self,
    label: str = '',
    measure_unit: str = '',
    min_value: float = None,
    max_value: float = None,
    data_type: ChartDataType = ChartDataType.DATETIME,
  ) -> None:
    """
    Constructor
    ---
    Arguments
      - label : Label of the axis
      - color : Color of the axis
      - min_value : Minimum value of the axis
      - max_value : Maximum value of the axis
    """
    self.label = label
    self.measure_unit = measure_unit
    self.min_value = min_value
    self.max_value = max_value
    self.data_type = data_type
