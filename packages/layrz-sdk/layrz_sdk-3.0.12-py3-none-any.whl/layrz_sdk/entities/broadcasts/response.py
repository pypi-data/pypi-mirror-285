"""Broadcast Result Response data"""

from typing import Dict, List


class BroadcastResponse:
  """
  Broadcast response data
  ---
  Attributes
    - json (dict|list): Parsed data
    - raw (str): Raw data
  """

  def __init__(self, json: Dict | List, raw: str) -> str | None | bool:
    self.json = json
    self.raw = raw

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'BroadcastResponse(json={self.json}, raw={self.raw})'

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
