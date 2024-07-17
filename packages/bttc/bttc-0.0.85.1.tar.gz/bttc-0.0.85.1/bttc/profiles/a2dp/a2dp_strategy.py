"""Profile A2DP Strategy module."""

import time

from typing import TypeAlias

from mobly.controllers import android_device

from bttc import constants
from bttc.utils.bt import strategy


BluetoothConnectionPolicy = constants.BluetoothConnectionPolicy
BluetoothConnectionState = constants.BluetoothConnectionState
Device: TypeAlias = android_device.AndroidDevice


class A2DPConnectionStrategy(strategy.ConnectionStrategy):
  """A2DP connection strategy.

  Attributes:
    a2dp_sink_ad: A2DP sink device.
    a2dp_source_ad: A2DP source device.
  """

  def __init__(
      self, a2dp_sink_ad: Device, a2dp_source_ad: Device):
    self._a2dp_sink_ad = a2dp_sink_ad
    self._a2dp_source_ad = a2dp_source_ad

  @property
  def a2dp_sink_ad(self) -> Device:
    return self._a2dp_sink_ad

  @property
  def a2dp_source_ad(self) -> Device:
    return self._a2dp_source_ad

  def connect(self, timeout_sec: int = 30) -> bool:
    """Builds connection of A2DP profile.

    Args:
      timeout_sec: Number of seconds to wait for connection.

    Returns:
      True iff the connection is carried out successfully.
    """
    if self.is_connected():
      self.a2dp_sink_ad.log.info(
          'The A2DP connection between %s and %s is already connected.',
          self.a2dp_sink_ad.serial, self.a2dp_source_ad.serial)
      return True

    pri_ad_local_name = self.a2dp_sink_ad.bt.name
    a2dp_source_mac_address = self.a2dp_source_ad.bt.mac_address
    for policy in [
        BluetoothConnectionPolicy.CONNECTION_POLICY_FORBIDDEN,
        BluetoothConnectionPolicy.CONNECTION_POLICY_ALLOWED]:
      self.a2dp_sink_ad.log.info(
          'Sets profile A2DP on %s for %s to policy %s',
          pri_ad_local_name, a2dp_source_mac_address, policy)
      self.a2dp_sink_ad.sl4a.bluetoothA2dpSinkSetPriority(
          a2dp_source_mac_address, policy.value)

    self.a2dp_sink_ad.sl4a.bluetoothConnectBonded(
        a2dp_source_mac_address)

    end_time = time.monotonic() + timeout_sec
    while time.monotonic() < end_time:
      if self.is_connected():
        self.a2dp_sink_ad.log.info(
            'The A2DP connection between %s and %s is established.',
            self.a2dp_sink_ad.serial, self.a2dp_source_ad.serial)
        return True

      time.sleep(1)

    self.a2dp_sink_ad.log.warning(
        'Failed to connect between %s and %s for profile A2DP!',
        self.a2dp_sink_ad.serial, self.a2dp_source_ad.serial)
    return False

  def is_connected(self) -> bool:
    """Checks the connection of A2DP.

    Returns:
      True iff A2DP is connected.
    """
    current_bt_connection_state = (
        self.a2dp_sink_ad.sl4a.bluetoothA2dpSinkGetConnectionStatus(
            self.a2dp_source_ad.bt.mac_address))
    return current_bt_connection_state == BluetoothConnectionState.CONNECTED
