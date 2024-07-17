"""Report formats"""

from enum import Enum


class ReportFormat(Enum):
  """
  Report format definition.
  """

  MICROSOFT_EXCEL = 'MICROSOFT_EXCEL'
  JSON = 'JSON'
  PDF = 'PDF'

  @property
  def _readable(self) -> str:
    """Readable"""
    return f'ReportFormat.{self.value}'

  def __str__(self) -> str:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str:
    """Readable property"""
    return self._readable
