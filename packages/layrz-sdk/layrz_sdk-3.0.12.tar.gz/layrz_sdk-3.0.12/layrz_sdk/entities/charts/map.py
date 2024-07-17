"""Map chart"""

from enum import Enum
from typing import Any, List, Tuple

from .exceptions import ChartException
from .render_technology import ChartRenderTechnology


class MapCenterType(Enum):
  """
  Map Chart center type
  """

  FIXED = 'FIXED'
  CONTAIN = 'CONTAIN'

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'BroadcastStatus.{self.value}'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable


class MapPoint:
  """Map point configuration"""

  def __init__(
    self,
    latitude: float,
    longitude: float,
    label: str,
    color: str,
  ) -> None:
    """
    Constructor
    ---
    Arguments
      latitude : Latitude of the point
      longitude : Longitude of the point
      label : Label of the point
      color : Color of the point
    """
    if not isinstance(latitude, float):
      raise ChartException('latitude must be an instance of float')
    self.latitude = latitude

    if not isinstance(longitude, float):
      raise ChartException('longitude must be an instance of float')
    self.longitude = longitude

    if not isinstance(label, str):
      raise ChartException('label must be an instance of str')
    self.label = label

    if not isinstance(color, str):
      raise ChartException('color must be an instance of str')
    self.color = color


class MapChart:
  """
  Map chart configuration
  """

  def __init__(
    self,
    points: List[MapPoint],
    title: str = 'Chart',
    center: MapCenterType = MapCenterType.CONTAIN,
    center_latlng: List[float] | Tuple[float] = None,
  ) -> None:
    """
    Constructor
    Args
    ----
      points : Points of the chart
      title : Title of the chart
      align : Alignment of the title
    """
    for i, point in enumerate(points):
      if not isinstance(point, MapPoint):
        raise ChartException(f'Point {i} must be an instance of MapPoint')
    self.points = points

    if not isinstance(title, str):
      raise ChartException('title must be an instance of str')
    self.title = title

    if not isinstance(center, MapCenterType):
      raise ChartException('center must be an instance of MapCenterType')
    self.center = center

    if self.center == MapCenterType.FIXED and not isinstance(center_latlng, (List, Tuple)):
      raise ChartException('center_latlng must be an instance of list or tuple')
    self.center_latlng = center_latlng

  def render(self, technology: ChartRenderTechnology = ChartRenderTechnology.FLUTTER_MAP) -> Any:
    """
    Render chart to a graphic Library.
    We have two graphic libraries: FLUTTER_MAP and LEAFLET.

    FLUTTER_MAP is a Flutter chart library. To return this option, use the parameter use_new_definition=True.
    LEAFLET is a Javascript chart library. This is the default option.
    """
    if technology == ChartRenderTechnology.FLUTTER_MAP:
      return {
        'library': 'FLUTTER_MAP',
        'chart': 'MAP',
        'configuration': self._render_flutter_map(),
      }

    return {
      'library': 'FLUTTER',
      'chart': 'TEXT',
      'configuration': [f'Unsupported {technology}'],
    }

  def _render_flutter_map(self) -> Any:
    """
    Converts the configuration to the chart to Flutter Map engine.
    """
    points = []

    for point in self.points:
      points.append(
        {
          'label': point.label,
          'color': point.color,
          'latlng': (point.latitude, point.longitude),
        }
      )

    center = 'CONTAIN'

    if self.center == MapCenterType.FIXED:
      center = 'FIXED'

    config = {
      'points': points,
      'center': center,
    }

    if self.center == MapCenterType.FIXED:
      config['centerLatLng'] = self.center_latlng

    return config

  def _render_leaflet(self) -> Any:
    """
    Converts the configuration of the chart to Leaflet map engine.
    """
    points = []

    for point in self.points:
      points.append({'label': point.label, 'color': point.color, 'latlng': (point.latitude, point.longitude)})

    center = 'CONTAIN'

    if self.center == MapCenterType.FIXED:
      center = 'FIXED'

    config = {
      'points': points,
      'title': self.title,
      'center': center,
    }

    if self.center == MapCenterType.FIXED:
      config['centerLatLng'] = self.center_latlng

    return config
