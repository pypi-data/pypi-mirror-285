"""Bar chart"""

from typing import Any, List

from .alignment import ChartAlignment
from .configuration import AxisConfig
from .exceptions import ChartException
from .render_technology import ChartRenderTechnology
from .serie import ChartDataSerie
from .serie_type import ChartDataSerieType


class BarChart:
  """
  Bar chart configuration
  """

  def __init__(
    self,
    x_axis: ChartDataSerie,
    y_axis: List[ChartDataSerie],
    title: str = 'Chart',
    align: ChartAlignment = ChartAlignment.CENTER,
    x_axis_config: AxisConfig = None,
    y_axis_config: AxisConfig = None,
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
      - x_axis_config : Configuration of the X Axis
      - y_axis_config : Configuration of the Y Axis
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

    if x_axis_config is None:
      x_axis_config = AxisConfig()

    if not isinstance(x_axis_config, AxisConfig):
      raise ChartException('x_axis_config must be an instance of AxisConfig')
    self.x_axis_config = x_axis_config

    if y_axis_config is None:
      y_axis_config = AxisConfig()

    if not isinstance(y_axis_config, AxisConfig):
      raise ChartException('y_axis_config must be an instance of AxisConfig')
    self.y_axis_config = y_axis_config

  def render(
    self,
    technology: ChartRenderTechnology = ChartRenderTechnology.SYNCFUSION_FLUTTER_CHARTS,
  ) -> Any:
    """
    Render chart to a graphic Library.
    We have two graphic libraries: GRAPHIC and APEXCHARTS.

    GRAPHIC is a Flutter chart library. To return this option, use the parameter use_new_definition=True.
    APEXCHARTS is a Javascript chart library. This is the default option.
    """
    if technology == ChartRenderTechnology.GRAPHIC:
      return {
        'library': 'GRAPHIC',
        'chart': 'BAR',
        'configuration': self._render_graphic(),
      }

    if technology == ChartRenderTechnology.SYNCFUSION_FLUTTER_CHARTS:
      return {
        'library': 'SYNCFUSION_FLUTTER_CHARTS',
        'chart': 'BAR',
        'configuration': self._render_syncfusion_flutter_charts(),
      }

    if technology == ChartRenderTechnology.APEX_CHARTS:
      return {
        'library': 'APEXCHARTS',
        'chart': 'BAR',
        'configuration': self._render_apexcharts(),
      }

    return {
      'library': 'FLUTTER',
      'chart': 'TEXT',
      'configuration': [f'Unsupported rendering technology {technology.name}'],
    }

  def _render_syncfusion_flutter_charts(self) -> Any:
    """
    Converts the configuration of the chart to Syncfusion Flutter Charts.
    """
    series = []

    for serie in self.y_axis:
      values = []
      for i, value in enumerate(serie.data):
        x_axis = self.x_axis.data[i]
        values.append({'xAxis': x_axis, 'yAxis': value})

      series.append(
        {
          'label': serie.label,
          'color': serie.color,
          'values': values,
        }
      )

    return {
      'series': series,
      'xAxis': {
        'label': self.x_axis_config.label,
        'measureUnit': self.x_axis_config.measure_unit,
        'dataType': self.x_axis_config.data_type.value,
        'minValue': self.x_axis_config.min_value,
        'maxValue': self.x_axis_config.max_value,
      },
      'yAxis': {
        'label': self.y_axis_config.label,
        'measureUnit': self.y_axis_config.measure_unit,
        'dataType': self.y_axis_config.data_type.value,
        'minValue': self.y_axis_config.min_value,
        'maxValue': self.y_axis_config.max_value,
      },
    }

  def _render_graphic(self) -> Any:
    """
    Converts the configuration of the chart to Flutter library graphic.
    """

    series = []

    for serie in self.y_axis:
      for i, value in enumerate(serie.data):
        x_axis = self.x_axis.data[i]
        series.append(
          {
            'label': serie.label,
            'color': serie.color,
            'category': x_axis,
            'value': value,
          }
        )

    return series

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
        'title': {'text': self.x_axis.label},
      },
      'title': {
        'text': self.title,
        'align': self.align.value,
        'style': {'fontFamily': 'Fira Sans Condensed', 'fontSize': '20px', 'fontWeight': 'normal'},
      },
      'plotOptions': {'bar': {'horizontal': True, 'borderRadius': 4}},
      'dataLabels': {'enabled': False},
      'chart': {
        'type': 'bar',
        'animations': {'enabled': False},
        'toolbar': {'show': False},
        'zoom': {'enabled': False},
      },
    }

    return config
