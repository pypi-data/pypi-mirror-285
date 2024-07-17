"""Broadcast result Status"""

from enum import Enum


class BroadcastStatus(Enum):
  """Broadcast result status"""

  OK = 'OK'
  BADREQUEST = 'BADREQUEST'
  INTERNALERROR = 'INTERNALERROR'
  UNAUTHORIZED = 'UNAUTHORIZED'
  UNPROCESSABLE = 'UNPROCESSABLE'
  DISCONNECTED = 'DISCONNECTED'

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
