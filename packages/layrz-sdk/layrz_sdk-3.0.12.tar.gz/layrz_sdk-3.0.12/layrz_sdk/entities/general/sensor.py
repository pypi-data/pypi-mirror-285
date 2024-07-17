"""Sensor entity"""


class Sensor:
  """
  Sensor entity
  ---
  Attributes
    pk : Sensor ID
    name : Name of the sensor
    slug : Slug of the sensor
  """

  def __init__(self, pk: int, name: str, slug: str) -> None:
    """Constructor"""
    self.pk = pk
    self.name = name
    self.slug = slug

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'Sensor(pk={self.pk}, name={self.name}, slug={self.slug})'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
