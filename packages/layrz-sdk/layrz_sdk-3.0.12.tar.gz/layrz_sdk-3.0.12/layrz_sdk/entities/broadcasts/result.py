"""Broadcast result"""

from datetime import datetime

from .request import BroadcastRequest
from .response import BroadcastResponse
from .status import BroadcastStatus


class BroadcastResult:
  """
  Broadcast result
  ---
  Attributes
    - service_id : Service ID
    - asset_id : Asset ID
    - status : Status
    - request : Request data sent to the service
    - response : Response data came from the service
    - submitted_at : Date of submission
  """

  def __init__(
    self,
    service_id: int,
    asset_id: int,
    status: BroadcastStatus,
    request: BroadcastRequest,
    response: BroadcastResponse,
    submitted_at: datetime,
  ) -> str | None | bool:
    self.service_id = service_id
    self.asset_id = asset_id
    self.status = status
    self.request = request
    self.response = response
    self.submitted_at = submitted_at

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return (
      f'BroadcastResult(service_id={self.service_id}, asset_id={self.asset_id}, status={self.status}, '
      + f'request={self.request}, response={self.response}, submitted_at={self.submitted_at})'
    )

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
