"""HTML chart"""

from typing import Any, List

from .exceptions import ChartException


class HTMLChart:
  """
  HTML chart configuration
  """

  def __init__(self, content: str = '<p>N/A</p>', title: str = 'Chart') -> None:
    """
    Constructor

    Args
    ----
      content (str): HTML content of the chart.
      title (str): Title of the chart.
      align (ChartAlignment): Alignment of the chart.
    """
    if not isinstance(content, str):
      raise ChartException('content must be an instance of str')
    self.content = content

    if not isinstance(title, str):
      raise ChartException('title must be an instance of str')
    self.title = title

  def render(self) -> Any:
    """
    Render chart to a Javascript Library.
    Currently only available for HTML.
    """
    return {'library': 'HTML', 'configuration': self._render_html()}

  def _render_html(self) -> Any:
    """
    Converts the configuration of the chart to HTML render engine.
    """
    config = {'content': self.content, 'title': self.title}

    return config
