"""Radial Bar chart"""

from typing import Any, List

from .alignment import ChartAlignment
from .exceptions import ChartException
from .render_technology import ChartRenderTechnology
from .serie import ChartDataSerie


class RadialBarChart:
  """
  Radial Bar chart configuration
  """

  def __init__(
    self,
    series: List[ChartDataSerie],
    title: str = 'Chart',
    align: ChartAlignment = ChartAlignment.CENTER,
  ) -> None:
    """
    Constructor
    ----
    Arguments
      series : Defines the series of the chart, uses the ChartDataSerie class.
               Please read the documentation to more information.
      title : Title of the chart.
      align : Alignment of the chart.
    """
    for i, serie in enumerate(series):
      if not isinstance(serie, ChartDataSerie):
        raise ChartException(f'Y Axis serie {i} must be an instance of ChartDataSerie')
    self.series = series

    if not isinstance(title, str):
      raise ChartException('title must be an instance of str')
    self.title = title

    if not isinstance(align, ChartAlignment):
      raise ChartException('align must be an instance of ChartAlignment')
    self.align = align

  def render(
    self,
    technology: ChartRenderTechnology = ChartRenderTechnology.SYNCFUSION_FLUTTER_CHARTS,
  ) -> Any:
    """
    Render chart to a graphic Library.
    We have two graphic libraries: GRAPHIC and CANVASJS.

    GRAPHIC is a Flutter chart library. To return this option, use the parameter use_new_definition=True.
    CANVASJS is a Javascript chart library. This is the default option.
    """
    if technology == ChartRenderTechnology.GRAPHIC:
      return {
        'library': 'GRAPHIC',
        'chart': 'RADIALBAR',
        'configuration': self._render_graphic(),
      }

    if technology == ChartRenderTechnology.APEX_CHARTS:
      return {
        'library': 'APEXCHARTS',
        'chart': 'RADIALBAR',
        'configuration': self._render_apexcharts(),
      }

    if technology == ChartRenderTechnology.SYNCFUSION_FLUTTER_CHARTS:
      return {
        'library': 'SYNCFUSION_FLUTTER_CHARTS',
        'chart': 'RADIALBAR',
        'configuration': self._render_syncfusion_flutter_charts(),
      }

    return {
      'library': 'FLUTTER',
      'chart': 'TEXT',
      'configuration': [f'Unsupported {technology}'],
    }

  def _render_syncfusion_flutter_charts(self) -> Any:
    """
    Converts the configuration of the chart to Syncfusion Flutter Charts.
    """
    series = []

    for serie in self.series:
      series.append(
        {
          'label': serie.label,
          'color': serie.color,
          'value': serie.data[0],
        }
      )

    return {'series': series}

  def _render_graphic(self) -> Any:
    """
    Converts the configuration of the chart to a Flutter library Graphic.
    """
    series = []

    for serie in self.series:
      series.append(
        {
          'group': serie.label,
          'color': serie.color,
          'value': serie.data[0],
        }
      )

    return series

  def _render_apexcharts(self) -> Any:
    """
    Converts the configuration of the chart to Javascript library ApexCharts.
    """

    series = []
    colors = []
    labels = []

    for serie in self.series:
      series.append(serie.data[0])
      colors.append(serie.color)
      labels.append(serie.label)

    config = {
      'series': series,
      'colors': colors,
      'labels': labels,
      'title': {
        'text': self.title,
        'align': self.align.value,
        'style': {'fontFamily': 'Fira Sans Condensed', 'fontSize': '20px', 'fontWeight': 'normal'},
      },
      'chart': {
        'type': 'radialBar',
        'animations': {'enabled': False},
        'toolbar': {'show': False},
        'zoom': {'enabled': False},
      },
      'dataLabels': {'enabled': True},
    }

    return config
