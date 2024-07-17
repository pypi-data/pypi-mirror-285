"""Waypoint entity"""

from datetime import datetime

from layrz_sdk.entities.general.geofence import Geofence


class Waypoint:
  """
  Checkpoint waypoint entity definition
  ---
  Attributes
    - pk : Waypoint ID
    - geofence : Related geofence
    - start_at : Date of start this waypoint stage
    - end_at : Date of end this waypoint stage
    - sequence_real : Real sequence performed
    - sequence_ideal : Ideal/defined sequence
  """

  def __init__(
    self,
    pk: int,
    geofence: Geofence,
    start_at: datetime,
    end_at: datetime,
    sequence_real: int,
    sequence_ideal: int,
  ) -> None:
    """Constructor"""
    self.pk = pk
    self.geofence = geofence
    self.start_at = start_at
    self.end_at = end_at
    self.sequence_real = sequence_real
    self.sequence_ideal = sequence_ideal

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return (
      f'Waypoint(pk={self.pk}, geofence={self.geofence}, start_at={self.start_at}, '
      + f'end_at={self.end_at}, sequence_real={self.sequence_real}, sequence_ideal={self.sequence_ideal})'
    )

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
