"""Line chart"""

import logging
from typing import Any, List

from .alignment import ChartAlignment
from .configuration import AxisConfig
from .data_type import ChartDataType
from .exceptions import ChartException
from .render_technology import ChartRenderTechnology
from .serie import ChartDataSerie
from .serie_type import ChartDataSerieType

log = logging.getLogger(__name__)


class LineChart:
  """
  Line chart configuration

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

  def render(self, technology: ChartRenderTechnology) -> Any:
    """
    Render chart to a graphic Library.
    We have two graphic libraries: GRAPHIC and CANVASJS.

    GRAPHIC is a Flutter chart library. To return this option, use the parameter use_new_definition=True.
    CANVASJS is a Javascript chart library. This is the default option.
    """

    if technology == ChartRenderTechnology.GRAPHIC:
      return {
        'library': 'GRAPHIC',
        'chart': 'LINE',
        'configuration': self._render_graphic(),
      }

    if technology == ChartRenderTechnology.SYNCFUSION_FLUTTER_CHARTS:
      return {
        'library': 'SYNCFUSION_FLUTTER_CHARTS',
        'chart': 'LINE',
        'configuration': self._render_syncfusion_flutter_charts(),
      }

    if technology == ChartRenderTechnology.CANVASJS:
      return {
        'library': 'CANVASJS',
        'chart': 'LINE',
        'configuration': self._render_canvasjs(),
      }

    return {
      'library': 'FLUTTER',
      'chart': 'TEXT',
      'configuration': [f'Unsupported {technology}'],
    }

  def _render_syncfusion_flutter_charts(self) -> Any:
    """
    Converts the configuration of the chart to a Flutter library syncfusion_flutter_charts.
    """
    series = []

    for serie in self.y_axis:
      if serie.serie_type not in [ChartDataSerieType.LINE, ChartDataSerieType.AREA]:
        log.warning('Serie type not supported: %s', serie.serie_type)
        continue

      points = []

      for i, value in enumerate(self.x_axis.data):
        x_value = value.timestamp() if self.x_axis.data_type == ChartDataType.DATETIME else value
        if not isinstance(x_value, (int, float)):
          continue

        y_value = serie.data[i]
        if isinstance(y_value, bool):
          if y_value:
            y_value = 1
          else:
            y_value = 0

        if not isinstance(y_value, (int, float)):
          log.debug("Value isn't a number: %s", y_value)
          continue

        points.append(
          {
            'xAxis': x_value,
            'yAxis': y_value,
          }
        )

      series.append(
        {
          'color': serie.color,
          'values': points,
          'label': serie.label,
          'type': 'AREA' if serie.serie_type == ChartDataSerieType.AREA else 'LINE',
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
    Converts the configuration of the chart to a Flutter library Graphic.
    """
    series = []

    for serie in self.y_axis:
      if serie.serie_type not in [ChartDataSerieType.LINE, ChartDataSerieType.AREA]:
        continue

      points = []

      for i, value in enumerate(self.x_axis.data):
        points.append(
          {
            'x_axis': {
              'value': value.timestamp() if self.x_axis.data_type == ChartDataType.DATETIME else value,
              'is_datetime': self.x_axis.data_type == ChartDataType.DATETIME,
            },
            'y_axis': serie.data[i],
          }
        )

      series.append(
        {
          'group': serie.label,
          'color': serie.color,
          'dashed': serie.serie_type == ChartDataSerieType.LINE and serie.dashed,
          'type': 'AREA' if serie.serie_type == ChartDataSerieType.AREA else 'LINE',
          'values': points,
        }
      )

    return series

  def _render_canvasjs(self) -> Any:
    """
    Converts the configuration of the chart to Javascript library CanvasJS.
    """
    datasets = []

    for serie in self.y_axis:
      dataset = {
        'type': 'line',
        'name': serie.label,
        'connectNullData': True,
        'nullDataLineDashType': 'solid',
        'showInLegend': True,
        'color': serie.color,
        'markerSize': 3,
      }

      if serie.serie_type != ChartDataSerieType.NONE:
        dataset['type'] = serie.serie_type.value

      if serie.serie_type == ChartDataSerieType.AREA:
        dataset['fillOpacity'] = 0.3

      if self.x_axis.data_type == ChartDataType.DATETIME:
        dataset['xValueType'] = 'dateTime'
        dataset['xValueFormatString'] = 'YYYY-MM-DD HH:mm:ss TT'

      if serie.serie_type == ChartDataSerieType.LINE and serie.dashed:
        dataset['lineDashType'] = 'dash'
        dataset['markerSize'] = 0

      points = []

      if serie.serie_type == ChartDataSerieType.SCATTER:
        for point in serie.data:
          points.append({'x': point.x, 'y': point.y})
      else:
        for i, value in enumerate(self.x_axis.data):
          points.append(
            {
              'x': (value.timestamp() * 1000) if self.x_axis.data_type == ChartDataType.DATETIME else value,
              'y': serie.data[i],
            }
          )

      dataset['dataPoints'] = points
      datasets.append(dataset)

    return {
      'animationEnabled': False,
      'zoomEnabled': True,
      'title': {
        'text': self.title,
        'fontFamily': 'Fira Sans Condensed',
        'fontSize': 20,
        'horizontalAlign': self.align.value,
      },
      'data': datasets,
      'axisX': {
        'title': self.x_axis.label,
        'titleFontFamily': 'Fira Sans Condensed',
        'titleFontSize': 20,
      },
      'toolTip': {'animationEnabled': False, 'shared': True},
      'legend': {'cursor': 'pointer'},
    }


class AreaChart(LineChart):
  """
  Line chart
  Deprecation warning: This class will be removed in the next version. Use LineChart instead.
  """
