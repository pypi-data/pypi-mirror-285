"""Broadcast Result Request data"""

from typing import Dict, List


class BroadcastRequest:
  """
  Broadcast request data
  ---
  Attributes
    - json : Parsed data
    - raw : Raw data
  """

  def __init__(self, json: Dict | List, raw: str) -> None:
    self.json = json
    self.raw = raw

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'BroadcastRequest(json={self.json}, raw={self.raw})'

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
