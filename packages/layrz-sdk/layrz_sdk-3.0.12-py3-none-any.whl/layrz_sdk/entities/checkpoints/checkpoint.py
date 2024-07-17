"""Checkpoints entitites"""

from datetime import datetime
from typing import List

from .waypoint import Waypoint


class Checkpoint:
  """
  Checkpoint entity definition
  ---
  Attributes
    - pk : Checkpoint activation ID
    - asset_id : Asset ID
    - waypoints : List of waypoints of the checkpoint
    - start_at : Start date
    - end_at : End date
  """

  def __init__(
    self,
    pk: int,
    asset_id: int,
    waypoints: List[Waypoint],
    start_at: datetime,
    end_at: datetime,
  ) -> None:
    """Constructor"""
    self.pk = pk
    self.asset_id = asset_id
    self.waypoints = waypoints
    self.start_at = start_at
    self.end_at = end_at

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return (
      f'Checkpoint(pk={self.pk}, asset_id={self.asset_id}, waypoints={self.waypoints}, '
      + f'start_at={self.start_at}, end_at={self.end_at})'
    )

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
