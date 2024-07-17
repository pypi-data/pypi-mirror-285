"""Module to support operations from Bluetooth Device Simulator as broker."""

from typing import Any, Callable, Optional, TypeAlias

from bttc import constants as bt_constants
from bttc.utils.bt import connection_factory
from bttc.utils.bt import strategy
from mobly.controllers import android_device


Device: TypeAlias = android_device.AndroidDevice


def is_secondary_ad_set(
    method: Optional[Callable[..., Any]]) -> Callable[..., Any]:
  """Decorator of function which requires operations from `secondary_ad`.

  This decorator is used to wrap up target function which needs to manipulate
  the `secondary_ad` to guarantee that `secondary_ad` exist.

  Args:
    method: Decorated function which needs to manipulate `secondary_ad`.

  Returns:
    The wrapper of decorated function.
  """

  def _decorator(self, *args, **kwargs) -> Any:
    if self.secondary_ad is not None:
      return method(self, *args, **kwargs)

    raise MissingBtClientDeviceError('The secondary_ad was not set!')

  return _decorator


def is_bluetooth_paired(
    method: Optional[Callable[..., Any]]) -> Callable[..., Any]:
  """Decorator of function which requires primary_ad pairs with secondary_ad.

  This decorator is used to wrap up target function which needs to connect
  primary_ad and secondary_ad to guarantee that primary_ad is paired with
  secondary_ad.

  Args:
    method: Decorated function which needs to connect primary_ad and
      secondary_ad.

  Returns:
    The wrapper of decorated function.
  """

  def _decorator(self, *args, **kwargs) -> Any:
    if self.is_bt_paired():
      return method(self, *args, **kwargs)

    self.primary_ad.log.error(
        'Devices %s and %s are not paired before connection',
        self.primary_ad.serial, self.secondary_ad.serial)
    return False

  return _decorator


def require_sl4a(
    method: Optional[Callable[..., Any]]) -> Callable[..., Any]:
  """Decorator of function which requires SL4A to be available.

  This decorator is used to wrap up target function which will verify if
  primary_ad and secondary_ad are already ready in SL4A service.

  Args:
    method: Decorated function which requires to have both primary_ad and
      secondary_ad ready for SL4A.

  Returns:
    The wrapper of decorated function.
  """
  def _decorator(self, *args, **kwargs) -> Any:
    msg = 'SL4A is required!'
    primary_ad_services = (
        self.primary_ad.services.list_live_services() if self.primary_ad
        else {})
    if 'sl4a' not in primary_ad_services:
      self.primary_ad.log.warning(msg)
      return False

    return method(self, *args, **kwargs)

  return _decorator


class MissingBtClientDeviceError(Exception):
  """Error casued by missing required bluetooth client device."""


class Broker:
  """Decorates an Android device as a Bluetooth Device Simulator.

  With `git_master-bds-dev` build, the android device can act as a bluetooth
  hfp and a2dp sink device.

  Attributes:
    primary_ad: Simulator or BDS device.
    secondary_ad: Connected Android device or DUT device.
    mac_address: MAC address of simulator device (primary_ad).
    a2dp_connect_strategy: A2DP connection strategy object.
  """

  def __init__(self, primary_ad: Device, secondary_ad: Device | None = None):
    self._primary_ad = primary_ad
    self._secondary_ad = secondary_ad
    self._a2dp_connect_strategy: strategy.ConnectionStrategy | None = None

  def _require_sl4a(self, device: Device):
    pass

  @property
  def bds(self) -> Device:
    return self._primary_ad

  @property
  def dut(self) -> Device:
    return self._secondary_ad

  @property
  @is_secondary_ad_set
  def a2dp_connect_strategy(self) -> strategy.ConnectionStrategy:
    """Gets A2DP connect strategy object.

    Returns:
      A2DP connect strategy object.
    """
    if self._a2dp_connect_strategy is None:
      self._a2dp_connect_strategy = connection_factory.get_connection_strategy(
          bt_profile=bt_constants.BluetoothProfile.A2DP_SINK,
          primary_ad=self.primary_ad,
          secondary_ad=self.secondary_ad)

    return self._a2dp_connect_strategy

  @property
  def primary_ad(self) -> Device:
    """Gets the primary device."""
    return self._primary_ad

  @property
  def secondary_ad(self) -> Device | None:
    """Gets secondary Android device."""
    return self._secondary_ad

  @secondary_ad.setter
  def secondary_ad(self, ad: Device):
    """Sets secondary Android device."""
    self._secondary_ad = ad

  def activate_pairing_mode(self):
    """Makes the android hfp device discoverable over Bluetooth."""
    self.primary_ad.log.info('Activating pairing mode of the primary device...')
    self.primary_ad.sl4a.bluetoothMakeDiscoverable()
    self.primary_ad.sl4a.bluetoothStartPairingHelper()

  @require_sl4a
  @is_secondary_ad_set
  def is_bt_paired(self) -> bool:
    """Checks if the secondary device is connected through BT."""
    return self.primary_ad.bt.name in self.secondary_ad.bt.list_paired_devices()

  @require_sl4a
  @is_secondary_ad_set
  def pair(self) -> bool:
    """Builds pairing between BDS (`primary_ad`) and phone (`secondary_ad`)."""
    bds_name = self.primary_ad.bt.name
    phone_name = self.secondary_ad.bt.name
    if self.is_bt_paired():
      self.primary_ad.log.info(
          'BDS (%s) is already paired with Phone as "%s"!',
          bds_name,
          phone_name)
      return True

    self.primary_ad.log.info('Start activating pairing mode...')
    self.activate_pairing_mode()
    self.secondary_ad.log.info('Start scanning new device(s)...')
    scanning_result = self.secondary_ad.mbs.btDiscoverAndGetResults()
    scanned_device_names = {record['Name'] for record in scanning_result}
    if bds_name in scanned_device_names:
      self.secondary_ad.log.info('BDS is discovered! Start pairing...')
      self.secondary_ad.mbs.btPairDevice(self.primary_ad.bt.mac_address)
      return self.is_bt_paired()

    self.secondary_ad.log.warning(
        'Could not found BDS="%s" during scanning process!',
        bds_name)
    return False

  @require_sl4a
  @is_secondary_ad_set
  def unpair(self) -> bool:
    """Unpair BDS (`primary_ad`) with phone (`secondary_ad`)."""
    if self.is_bt_paired():
      self.secondary_ad.mbs.btUnpairDevice(self.primary_ad.bt.mac_address)
      return not self.is_bt_paired()

    return True
