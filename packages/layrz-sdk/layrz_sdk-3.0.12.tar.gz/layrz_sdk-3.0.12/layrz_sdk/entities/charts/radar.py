"""Radar chart"""

from typing import Any, List

from .alignment import ChartAlignment
from .exceptions import ChartException
from .serie import ChartDataSerie
from .serie_type import ChartDataSerieType


class RadarChart:
  """
  Radar chart configuration

  """

  def __init__(
    self,
    x_axis: ChartDataSerie,
    y_axis: List[ChartDataSerie],
    title: str = 'Chart',
    align: ChartAlignment = ChartAlignment.CENTER,
  ) -> None:
    """
    Constructor
    ----
    Arguments
      - x_axis : Defines the X Axis of the chart, uses the ChartDataSerie class.
                 Please read the documentation to more information.
      - y_axis : Defines the Y Axis of the chart, uses the ChartDataSerie class.
                 Please read the documentation to more information.
      - title : Title of the chart
      - align : Alignment of the title
    """
    for i, serie in enumerate(y_axis):
      if not isinstance(serie, ChartDataSerie):
        raise ChartException(f'Y Axis serie {i} must be an instance of ChartDataSerie')
    self.y_axis = y_axis

    if not isinstance(x_axis, ChartDataSerie):
      raise ChartException('X Axis must be an instance of ChartDataSerie')
    self.x_axis = x_axis

    if not isinstance(title, str):
      raise ChartException('title must be an instance of str')
    self.title = title

    if not isinstance(align, ChartAlignment):
      raise ChartException('align must be an instance of ChartAlignment')
    self.align = align

  def render(self) -> Any:
    """
    Render chart to a Javascript Library.
    Currently only available for ApexCharts.
    """
    return {'library': 'APEXCHARTS', 'configuration': self._render_apexcharts()}

  def _render_apexcharts(self) -> Any:
    """
    Converts the configuration of the chart to Javascript library ApexCharts.
    """

    series = []
    colors = []

    for serie in self.y_axis:
      modified_serie = {'name': serie.label, 'data': serie.data}

      if serie.serie_type is not ChartDataSerieType.NONE:
        modified_serie['type'] = serie.serie_type.value

      series.append(modified_serie)
      colors.append(serie.color)

    config = {
      'series': series,
      'colors': colors,
      'xaxis': {
        'categories': self.x_axis.data,
        'type': self.x_axis.data_type.value,
        'title': {
          'text': self.x_axis.label,
          'style': {'fontFamily': 'Fira Sans Condensed', 'fontSize': '20px', 'fontWeight': 'normal'},
        },
      },
      'title': {
        'text': self.title,
        'align': self.align.value,
        'style': {'fontFamily': 'Fira Sans Condensed', 'fontSize': '20px', 'fontWeight': 'normal'},
      },
      'chart': {
        'type': 'radar',
        'animations': {'enabled': False},
        'toolbar': {'show': False},
        'zoom': {'enabled': False},
      },
      'dataLabels': {'enabled': True},
      'plotOptions': {'bar': {'horizontal': True, 'borderRadius': 4}},
    }

    return config
