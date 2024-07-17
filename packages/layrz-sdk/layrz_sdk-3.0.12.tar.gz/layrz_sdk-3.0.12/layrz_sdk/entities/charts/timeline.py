"""Timeline chart entities"""

from datetime import datetime
from typing import Any, List

from .alignment import ChartAlignment
from .exceptions import ChartException


class TimelineSerieItem:
  """
  Chart Data Serie Item for Timeline Charts
  """

  def __init__(self, name: str, start_at: datetime, end_at: datetime, color: str) -> None:
    """
    Constructor
    ----
    Arguments
      - name : Name of the item.
      - start_at : Start date of the item.
      - end_at : End date of the item.
      - color : Color of the item.
    """
    if not isinstance(name, str):
      raise ChartException('name must be an instance of str')
    self.name = name

    if not isinstance(start_at, datetime):
      raise ChartException('start_at must be an instance of datetime')
    self.start_at = start_at

    if not isinstance(end_at, datetime):
      raise ChartException('end_at must be an instance of datetime')
    self.end_at = end_at

    if not isinstance(color, str):
      raise ChartException('color must be an instance of str')
    self.color = color


class TimelineSerie:
  """
  Chart Data Serie for Timeline charts
  """

  def __init__(self, data: List[TimelineSerieItem], label: str) -> None:
    """
    Constructor
    ----
    Arguments
      - data : List of data points.
      - label : Label of the serie.
    """
    for i, datum in enumerate(data):
      if not isinstance(datum, TimelineSerieItem):
        raise ChartException(f'Y Axis serie {i} must be an instance of ChartDataSerie')
    self.data = data

    if not isinstance(label, str):
      raise ChartException('label must be an instance of str')
    self.label = label


class TimelineChart:
  """
  Timeline chart configuration
  """

  def __init__(
    self,
    series: List[TimelineSerie],
    title: str = 'Chart',
    align: ChartAlignment = ChartAlignment.CENTER,
  ) -> None:
    """
    Constructor
    ----
    Arguments
      - series : Defines the series of the chart, uses the TimelineSerie class.
                 Please read the documentation to more information.
      - title : Title of the chart.
      - align : Alignment of the chart.
    """
    for i, serie in enumerate(series):
      if not isinstance(serie, TimelineSerie):
        raise ChartException(f'Y Axis serie {i} must be an instance of TimelineSerie')
    self.series = series

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

    for serie in self.series:
      data = []

      for item in serie.data:
        data.append(
          {
            'x': item.name,
            'y': [item.start_at.timestamp() * 1000, item.end_at.timestamp() * 1000],
            'fillColor': item.color,
          }
        )

      series.append({'name': serie.label, 'data': data})

    config = {
      'series': series,
      'title': {
        'text': self.title,
        'align': self.align.value,
        'style': {'fontFamily': 'Fira Sans Condensed', 'fontSize': '20px', 'fontWeight': 'normal'},
      },
      'chart': {
        'type': 'rangeBar',
        'animations': {'enabled': False},
        'toolbar': {'show': False},
        'zoom': {'enabled': False},
      },
      'xaxis': {'type': 'datetime'},
      'plotOptions': {
        'bar': {
          'horizontal': True,
        }
      },
      'dataLabels': {'enabled': True},
    }

    return config
