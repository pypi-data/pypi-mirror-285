"""Scatter chart"""

from typing import Any, List

from .alignment import ChartAlignment
from .configuration import AxisConfig
from .exceptions import ChartException
from .render_technology import ChartRenderTechnology
from .serie_type import ChartDataSerieType


class ScatterSerieItem:
  """
  Chart Data Serie Item for Scatter Charts
  """

  def __init__(self, x: float, y: float) -> None:
    """
    Constructor

    Args
    ----
      x : X value of the item.
      y : Y value of the item.
    """
    self.x = x
    self.y = y


class ScatterSerie:
  """
  Chart Data Serie for Timeline charts
  """

  def __init__(
    self,
    data: List[ScatterSerieItem],
    color: str,
    label: str,
    serie_type: ChartDataSerieType = ChartDataSerieType.SCATTER,
  ) -> None:
    """
    Constructor
    ----
    Arguments
      data : List of data points.
      color : Color of the serie.
      label : Label of the serie.
    """
    for i, datum in enumerate(data):
      if not isinstance(datum, ScatterSerieItem):
        raise ChartException(f'Y Axis serie {i} must be an instance of ChartDataSerie')
    self.data = data

    if not isinstance(color, str):
      raise ChartException('color must be an instance of str')
    self.color = color

    if not isinstance(label, str):
      raise ChartException('label must be an instance of str')
    self.label = label

    if not isinstance(serie_type, ChartDataSerieType):
      raise ChartException('serie_type must be an instance of ChartDataSerieType')
    self.serie_type = serie_type


class ScatterChart:
  """
  Scatter chart configuration
  """

  def __init__(
    self,
    series: List[ScatterSerie],
    title: str = 'Chart',
    align: ChartAlignment = ChartAlignment.CENTER,
    x_axis_config: AxisConfig = None,
    y_axis_config: AxisConfig = None,
  ) -> None:
    """
    Constructor
    ----
    Arguments
      series : Defines the series of the chart, uses the ScatterSerie class.
               Please read the documentation to more information.
      title : Title of the chart.
      align : Alignment of the chart.
    """
    for i, serie in enumerate(series):
      if not isinstance(serie, ScatterSerie):
        raise ChartException(f'Y Axis serie {i} must be an instance of ScatterSerie')
    self.series = series

    if not isinstance(title, str):
      raise ChartException('title must be an instance of str')
    self.title = title

    if not isinstance(align, ChartAlignment):
      raise ChartException('align must be an instance of ChartAlignment')
    self.align = align

    if x_axis_config is None:
      x_axis_config = AxisConfig(label='', measure_unit='')

    if not isinstance(x_axis_config, AxisConfig):
      raise ChartException('x_axis_config must be an instance of AxisConfig')
    self.x_axis_config = x_axis_config

    if y_axis_config is None:
      y_axis_config = AxisConfig(label='', measure_unit='')

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
        'chart': 'SCATTER',
        'configuration': self._render_graphic(),
      }

    if technology == ChartRenderTechnology.SYNCFUSION_FLUTTER_CHARTS:
      return {
        'library': 'SYNCFUSION_FLUTTER_CHARTS',
        'chart': 'SCATTER',
        'configuration': self._render_syncfusion_flutter_charts(),
      }

    if technology == ChartRenderTechnology.APEX_CHARTS:
      return {
        'library': 'APEXCHARTS',
        'chart': 'SCATTER',
        'configuration': self._render_apexcharts(),
      }

    return {
      'library': 'FLUTTER',
      'chart': 'TEXT',
      'configuration': [f'Unsupported {technology}'],
    }

  def _render_syncfusion_flutter_charts(self) -> Any:
    """
    Converts the configuration of the chart to Flutter library Graphic.
    """
    series = []
    for serie in self.series:
      data = []

      type_serie = 'SCATTER'
      if serie.serie_type == ChartDataSerieType.SCATTER:
        type_serie = 'SCATTER'
      elif serie.serie_type == ChartDataSerieType.LINE:
        type_serie = 'LINE'
      elif serie.serie_type == ChartDataSerieType.AREA:
        type_serie = 'AREA'
      else:
        continue

      for item in serie.data:
        if not isinstance(item.x, (int, float)):
          continue
        if not isinstance(item.y, (int, float)):
          continue

        data.append(
          {
            'xAxis': item.x,
            'yAxis': item.y,
          }
        )

      series.append(
        {
          'label': serie.label,
          'color': serie.color,
          'values': data,
          'type': type_serie,
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
    Converts the configuration of the chart to Flutter library Graphic.
    """
    series = []
    for serie in self.series:
      data = []

      type_serie = 'SCATTER'
      if serie.serie_type == ChartDataSerieType.SCATTER:
        type_serie = 'SCATTER'
      elif serie.serie_type == ChartDataSerieType.LINE:
        type_serie = 'LINE'
      elif serie.serie_type == ChartDataSerieType.AREA:
        type_serie = 'AREA'
      else:
        continue

      for item in serie.data:
        data.append(
          {
            'x_axis': item.x,
            'y_axis': item.y,
          }
        )

      series.append(
        {
          'group': serie.label,
          'color': serie.color,
          'values': data,
          'type': type_serie,
        }
      )

    return series

  def _render_apexcharts(self) -> Any:
    """
    Converts the configuration of the chart to Javascript library ApexCharts.
    """

    series = []
    colors = []

    for serie in self.series:
      data = []

      for item in serie.data:
        data.append([item.x, item.y])

      series.append(
        {
          'name': serie.label,
          'data': data,
          'type': serie.serie_type.value,
        }
      )
      colors.append(serie.color)

    config = {
      'series': series,
      'colors': colors,
      'title': {
        'text': self.title,
        'align': self.align.value,
        'style': {'fontFamily': 'Fira Sans Condensed', 'fontSize': '20px', 'fontWeight': 'normal'},
      },
      'chart': {
        'type': 'scatter',
        'animations': {'enabled': False},
        'toolbar': {'show': False},
        'zoom': {'enabled': False},
      },
      'dataLabels': {'enabled': True},
    }

    return config
