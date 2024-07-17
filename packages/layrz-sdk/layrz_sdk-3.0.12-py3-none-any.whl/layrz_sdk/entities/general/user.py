"""User entity"""


class User:
  """
  User entity definition
  ---
  Attributes
    pk : User ID
    name : User name
  """

  def __init__(self, pk: int, name: str) -> None:
    """Constructor"""
    self.pk = pk
    self.name = name

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'User(pk={self.pk}, name={self.name})'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
