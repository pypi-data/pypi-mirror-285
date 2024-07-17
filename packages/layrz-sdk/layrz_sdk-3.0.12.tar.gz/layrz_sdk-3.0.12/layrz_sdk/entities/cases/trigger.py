"""Trigger entity"""


class Trigger:
  """
  Trigger entity definition
  ---
  Attributes
    - pk : Trigger ID
    - name : Trigger name
    - code : Trigger code
  """

  def __init__(self, pk: int, name: str, code: str) -> None:
    """Constructor"""
    self.pk = pk
    self.name = name
    self.code = code

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'Trigger(pk={self.pk}, name="{self.name}", code="{self.code}")'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
