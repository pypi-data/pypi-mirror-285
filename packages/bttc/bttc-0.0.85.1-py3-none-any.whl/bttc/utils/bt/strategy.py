"""Module for BT working strategy."""

from typing import Protocol
from bttc import constants


BluetoothProfile = constants.BluetoothProfile


class UnsupportedProfileConnectionError(Exception):
  """Error casued by unsupported connection of profile."""

  def __init__(self, profile: BluetoothProfile):
    super().__init__()
    self._profile = profile

  def __str__(self):
    return f'Connection with profile={self._profile.name} is not supported yet!'


class ConnectionStrategy(Protocol):
  """Bluetooth profile connection strategy."""

  def is_connected(self) -> bool:
    """Checks the connection of target profile.

    Returns:
      True iff and target profile is connected.
    """
    ...

  def connect(self, timeout_sec: int = 30) -> bool:
    """Builds connection of target profile.

    Args:
      timeout_sec: Number of seconds to wait for connection.

    Returns:
      True iff the connection is carried out successfully.
    """
    ...
