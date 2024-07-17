"""Geofence entity"""

from enum import Enum


class Geofence:
  """
  Geofence entity definition
  ---
  Attributes
    - pk : Geofence ID
    - name : Geofence name
    - color : Geofence color in Hex format
  """

  def __init__(self, pk: int, name: str, color: str) -> None:
    """Constructor"""
    self.pk = pk
    self.name = name
    self.color = color

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'Geofence(pk={self.pk}, name={self.name}, color={self.color})'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable


class PresenceType(Enum):
  """Presence type enum"""

  ENTRANCE = 'ENTRANCE'
  EXIT = 'EXIT'

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'PresenceType.{self.value}'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
