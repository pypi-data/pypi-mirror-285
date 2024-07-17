"""Events entitites"""

from datetime import datetime
from enum import Enum

from .trigger import Trigger


class CaseStatus(Enum):
  """Case status enum"""

  PENDING = 'PENDING'
  FOLLOWED = 'FOLLOWED'
  CLOSED = 'CLOSED'

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'BroadcastStatus.{self.value}'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable


class CaseIgnoredStatus(Enum):
  """
  Case ignore status, will define what kind ignore happened.
  """

  NORMAL = 'NORMAL'
  IGNORED = 'IGNORED'
  PRESSET = 'PRESSET'
  AUTO = 'AUTO'

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return f'BroadcastStatus.{self.value}'

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable


class Case:
  """
  Case entity definition
  ---
  Attributes
    - pk : Case ID
    - trigger : Trigger object that triggered the case
    - asset_id : Asset ID
    - comments list: List of comments submitted when the case was opened.
    - opened_at : Date of case opening
    - closed_at : Date of case closing
    - status : Case status
    - sequence : Case sequence
    - ignored_status : Case ignored status
  """

  def __init__(
    self,
    pk: int,
    trigger: Trigger,
    asset_id: int,
    opened_at: datetime,
    sequence: int = None,
    closed_at: datetime = None,
    comments: list = None,
    status: CaseStatus = CaseStatus.CLOSED,
    ignored_status: CaseIgnoredStatus = CaseIgnoredStatus.NORMAL,
  ) -> None:
    """Constructor"""
    self.pk = pk
    self.trigger = trigger
    self.asset_id = asset_id
    self.comments = comments if comments else []
    self.opened_at = opened_at
    self.closed_at = closed_at
    self.status = status
    self._sequence = sequence
    self.ignored_status = ignored_status

  def get_sequence(self) -> str | None | bool:
    """Sequence getter"""
    if self._sequence is not None:
      return f'{self.trigger.code}/{self._sequence}'
    else:
      return f'GENERIC/{self.pk}'

  def set_sequence(self, sequence: int) -> None:
    """Sequence setter"""
    self._sequence = sequence

  sequence = property(get_sequence, set_sequence)

  @property
  def _readable(self) -> str | None | bool:
    """Readable"""
    return (
      f'Case(pk={self.pk}, trigger={self.trigger}, asset_id={self.asset_id}, '
      + f'comments={len(self.comments)}, opened_at={self.opened_at}, closed_at={self.closed_at})'
    )

  def __str__(self) -> str | None | bool:
    """Readable property"""
    return self._readable

  def __repr__(self) -> str | None | bool:
    """Readable property"""
    return self._readable
