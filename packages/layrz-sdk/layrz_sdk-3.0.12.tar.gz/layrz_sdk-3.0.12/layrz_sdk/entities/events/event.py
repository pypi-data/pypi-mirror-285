"""Event entity"""

from datetime import datetime

from layrz_sdk.entities.cases.trigger import Trigger
from layrz_sdk.entities.general.geofence import Geofence, PresenceType
from layrz_sdk.entities.telemetry.message import Message


class Event:
  """
  Event entity definition

  Available attributes
  --------------------
    pk : Event ID
    trigger : Trigger object that triggered the event
    asset_id : ID of the Asset owner of the event
    message : Telemetry information of the event
    activated_at : Reception/triggered at
    geofence : Geofence where the event occurred
    presence_type : Presence type of the event
  """

  def __init__(
    self,
    pk: int,
    trigger: Trigger,
    asset_id: int,
    message: Message,
    activated_at: datetime,
    geofence: Geofence | None = None,
    presence_type: PresenceType | None = None,
  ) -> None:
    """Constructor"""
    self.pk = pk
    self.trigger = trigger
    self.asset_id = asset_id
    self.message = message
    self.activated_at = activated_at
    self.geofence = geofence
    self.presence_type = presence_type

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return (
      f'Event(pk={self.pk}, trigger={self.trigger}, asset_id={self.asset_id}, '
      + f'message={self.message}, activated_at={self.activated_at})'
    )

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
