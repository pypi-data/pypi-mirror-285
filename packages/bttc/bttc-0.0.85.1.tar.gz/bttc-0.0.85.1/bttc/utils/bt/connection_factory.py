"""Connection factory to retrieve connection strategy object."""

from typing import TypeAlias

from mobly.controllers import android_device

from bttc import constants
from bttc.profiles.a2dp import a2dp_strategy
from bttc.utils.bt import strategy


BluetoothProfile = constants.BluetoothProfile
Device: TypeAlias = android_device.AndroidDevice


def get_connection_strategy(
    bt_profile: BluetoothProfile,
    primary_ad: Device,
    secondary_ad: Device,
) -> strategy.ConnectionStrategy:
  """Gets the connection strategy.

  Args:
    bt_profile: Bluetooth profile.
    primary_ad: Primary Android device.
    secondary_ad: Secondary Android device.

  Returns:
    The connection strategy object.

  Raises:
    strategy.UnsupportedProfileConnectionError: When the BT profile is not
      supported yet.
  """
  if bt_profile == constants.BluetoothProfile.A2DP_SINK:
    return a2dp_strategy.A2DPConnectionStrategy(
        a2dp_sink_ad=primary_ad, a2dp_source_ad=secondary_ad)

  raise strategy.UnsupportedProfileConnectionError(bt_profile)
