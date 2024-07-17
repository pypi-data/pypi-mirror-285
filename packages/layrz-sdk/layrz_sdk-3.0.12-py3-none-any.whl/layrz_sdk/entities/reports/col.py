"""Report col"""

import warnings
from enum import Enum
from typing import Any

from ..formatting.text_align import TextAlignment


class ReportDataType(Enum):
  """
  Report date type
  """

  STR = 'str'
  INT = 'int'
  FLOAT = 'float'
  DATETIME = 'datetime'
  BOOL = 'bool'
  CURRENCY = 'currency'

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'ReportDataType.{self.value}'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable


class ReportCol:
  """
  Report col definition
  ---
  Attributes
    - content : Display content
    - color : Cell color
    - text_color : Text color
                   Deprecated, The text color now will use the luminance of the background color to determine the
                   text color
    - align : Text Alignment
    - data_type : Data type
    - datetime_format : Date time format
    - currency_symbol : Currency symbol
  """

  def __init__(
    self,
    content: Any,
    color: str = '#ffffff',
    text_color: str = None,
    align: TextAlignment = TextAlignment.LEFT,
    data_type: ReportDataType = ReportDataType.STR,
    datetime_format: str = '%Y-%m-%d %H:%M:%S',
    currency_symbol: str = '',
    bold: bool = False,
  ) -> None:
    self.content = content
    self.color = color

    if text_color is not None:
      warnings.warn('text_color is deprecated, use color instead', DeprecationWarning, stacklevel=2)

    self.align = align
    self.data_type = data_type
    self.datetime_format = datetime_format
    self.currency_symbol = currency_symbol
    self.bold = bold

  @property
  def _readable(self) -> str | None | bool:
    """Readable property"""
    return f'ReportCol(content={self.content})'

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
