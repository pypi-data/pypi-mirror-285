"""Custom Field entitiy"""


class CustomField:
  """
  Custom field definition
  ---
  Attributes
    - name : Name of the custom field
    - value : Value of the custom field
  """

  def __init__(self, name: str, value: str) -> None:
    """Constructor"""
    self.name = name
    self.value = value

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'CustomField(name={self.name}, value={self.value})'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
