"""Report header"""

import warnings

from ..formatting.text_align import TextAlignment


class ReportHeader:
  """
  Report header definition
  ---
  Attributes
    - content : Display name
    - width : Column width in points (pt)
              Deprecated, now uses the `autofit()` method of `xlsxwriter`
    - color : Cell color
    - text_color : Text color
                   Deprecated, The text color now will use the luminance of the background color to determine the
                   text color
    - align : Text Alignment
    - bold : Should the text be bold
  """

  def __init__(
    self,
    content: str,
    width: int = None,
    color: str = '#ffffff',
    text_color: str = None,
    align: TextAlignment = TextAlignment.CENTER,
    bold: bool = False,
  ) -> None:
    self.content = content

    if width is not None:
      warnings.warn('width is deprecated, use width instead', DeprecationWarning, stacklevel=2)

    self.color = color

    if text_color is not None:
      warnings.warn('text_color is deprecated, use color instead', DeprecationWarning, stacklevel=2)

    self.align = align
    self.bold = bold

  @property
  def _readable(self) -> str | None | bool:
    """Readable property"""
    return f'ReportHeader(content={self.content})'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
