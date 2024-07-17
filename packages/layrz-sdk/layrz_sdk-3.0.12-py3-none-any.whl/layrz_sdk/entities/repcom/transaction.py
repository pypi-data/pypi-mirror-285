"""Transaction entity"""

from datetime import datetime, timedelta

from layrz_sdk.entities.general.asset import Asset


class Transaction:
  """
  Transaction definition
  ---
  Attributes
    pk : Transaction ID
    asset : Asset related to the transaction
    amount : Amount of the transaction
    quantity : Quantity of the transaction
    mileage : Mileage in kilometers
    distance : Distance traveled in kilometers
    engine_time : Time with the engine on
    idle_time : Time with the engine on without movement
    in_geofence : Flag to indicate if transaction occurred inside a geofence
    geofence_name : Name of the geofence where transaction occurred
    received_at : Transaction reception date and time
    is_wildcard : Wildcard indicator for transaction
  """

  def __init__(
    self,
    pk: int,
    asset: Asset,
    amount: float,
    quantity: float,
    mileage: float,
    distance: float,
    engine_time: timedelta,
    idle_time: timedelta,
    in_geofence: bool,
    geofence_name: str,
    received_at: datetime,
    is_wildcard: bool,
  ) -> None:
    """Constructor"""
    self.pk = pk
    self.asset = asset
    self.amount = amount
    self.quantity = quantity
    self.mileage = mileage
    self.distance = distance
    self.engine_time = engine_time
    self.idle_time = idle_time
    self.in_geofence = in_geofence
    self.geofence_name = geofence_name
    self.received_at = received_at
    self.is_wildcard = is_wildcard
