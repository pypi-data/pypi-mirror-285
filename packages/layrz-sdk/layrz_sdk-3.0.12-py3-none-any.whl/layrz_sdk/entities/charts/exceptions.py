"""Chart exceptions"""


class ChartException(BaseException):
  """
  Chart Exception
  """

  def __init__(self, message: str) -> None:
    """Constructor"""
    self._message = message

  @property
  def message(self) -> str | None | bool:
    """Message"""
    return self._message

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'ChartException: {self._message}'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
