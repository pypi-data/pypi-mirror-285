"""Report page"""

from typing import List

from .header import ReportHeader
from .row import ReportRow


class ReportPage:
  """
  Report page definition
  ---
  Attributes
    - name : Name of the page. Length should be less than 60 characters
    - headers : Headers of the page
    - rows : Rows of the page
  """

  def __init__(
    self,
    name: str,
    headers: List[ReportHeader],
    rows: List[ReportRow],
    freeze_header: bool = False,
  ) -> None:
    self.name = name
    self.headers = headers
    self.rows = rows
    self.freeze_header = freeze_header

  @property
  def _readable(self) -> str | None | bool:
    """Readable property"""
    return f'ReportPage(name={self.name}, headers={self.headers}, rows={self.rows})'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable


class CustomReportPage:
  """
  Custom report page
  Basically it's a wrapper of the `xlswriter` worksheet that uses a function to construct the page
  ---
  Attributes:
    - name : Name of the page. Length should be less than 60 characters
  Methods:
  - builder(Worksheet) -> None : Function to build the page
                                 The builder receives a `Worksheet` object as an argument and shouldn't
                                 return anything.
  """

  def __init__(self, name: str, builder: callable) -> None:
    """Constructor"""
    self.name = name

    if not callable(builder):
      raise ValueError('builder should be a callable')
    self.builder = builder
