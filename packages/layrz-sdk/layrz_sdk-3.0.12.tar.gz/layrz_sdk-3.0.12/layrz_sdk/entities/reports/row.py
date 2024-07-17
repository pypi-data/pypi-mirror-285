"""Report row"""

from typing import List

from .col import ReportCol


class ReportRow:
  """
  Report row definition

  Available attributes
  --------------------
    content (list(ReportCol)): Cols to display
    height (float): Height of the cell, in points (pt)
    compact (bool): Compact mode
  """

  def __init__(
    self,
    content: List[ReportCol],
    height: float = None,
    compact: bool = False,
  ) -> None:
    """Constructor"""
    self.content = content
    self.compact = compact

    if height is not None:
      raise DeprecationWarning('height is deprecated.')

  @property
  def _readable(self) -> str | None | bool:
    """Readable property"""
    return f'ReportRow(content={self.content})'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
