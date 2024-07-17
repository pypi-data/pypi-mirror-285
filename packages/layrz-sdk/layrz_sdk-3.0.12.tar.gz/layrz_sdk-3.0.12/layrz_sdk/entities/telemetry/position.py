"""Position entity"""


class Position:
  """
  Geographic position definition
  ---
  Attributes
    - latitude : Latitude (in decimal degrees)
    - longitude : Longitude (in decimal degrees)
    - altitude : Altitude (in meters)
    - hdop : Horizontal dilution of precision
    - speed : Speed (in Kilometers per hour)
    - direction : Direction or heading (in degrees)
    - satellites : Number of satellites
  """

  def __init__(
    self,
    latitude: float = None,
    longitude: float = None,
    altitude: float = None,
    hdop: float = None,
    speed: float = None,
    direction: float = None,
    satellites: int = None,
  ) -> None:
    """Constructor"""
    self.latitude = latitude
    self.longitude = longitude
    self.altitude = altitude
    self.hdop = hdop
    self.speed = speed
    self.direction = direction
    self.satellites = satellites

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return (
      f'Position(latitude={self.latitude}, longitude={self.longitude}, altitude={self.altitude}, '
      + f'speed={self.speed}, direction={self.direction}, hdop={self.hdop}, satellites={self.satellites})'
    )

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
