"""Utils for Dialer Simulator app."""

import re
from typing import TypeAlias

from mobly.controllers import android_device
from bttc.profiles.hfp import hfp_devices
from bttc.utils.ui_pages import ui_core


DIALER_PACKAGE_NAME = 'com.google.android.dialer'
Device: TypeAlias = android_device.AndroidDevice


class Error(android_device.Error):
  """Error when an operation of this utilities fails."""


class DialerSimulator:
  """Class for Dialer Simulator app.

  The Dialer Simulator is used only on dogfood version.
  """

  def __init__(self, device: Device) -> None:
    self._device = device
    self._verify_dialer_version()

  def _verify_dialer_version(self) -> None:
    """Verifies that dialer app whether is dogfood version.

    Raises:
      Error: Dialer is not installed or not dogfood version.
    """
    output = self._device.adb.shell(
        ['dumpsys', 'package', DIALER_PACKAGE_NAME, '|', 'grep', '-E',
         '"versionName=(.+)"', '||', 'echo  ']).decode('utf-8').strip()
    version = re.findall(r'versionName=(.+)', output)
    if not version:
      raise Error(self._device, 'Dialer app is not installed.')
    self._device.log.debug('Dialer Simulator Version: %s', version)
    if 'dogfood' not in version[0]:
      raise Error(
          self._device,
          f'Dialer app is not dogfood version: {version}')

  def execute_command(self, *cmd_args: str) -> None:
    """Executes a command.

    Args:
      *cmd_args: Arguments for the command.
    """
    command = ['am', 'broadcast', '-n',
               ('com.google.android.dialer/com.android.dialer.simulator.'
                'impl.SimulatorBroadcastReceiver_Receiver')] + list(cmd_args)
    self._device.adb.shell(command)

  def make_incoming_call(self) -> None:
    """Makes an incoming call."""
    self.stop_dialer()
    self.execute_command(
        '--es', 'command', 'IncomingCall', '--es', 'number', '1234567890',
        '--ei', 'presentation', '1', '--es', 'cnap', 'SomeCnap')

  def make_outgoing_call(
      self, phone_number: str = '1234567890', allow_multiple_call: bool = False) -> None:
    """Makes an outgoing call."""
    if not allow_multiple_call:
      self._device.log.info('Stoping dialer...')
      self.stop_dialer()

    self.execute_command(
        '--es', 'command', 'OutgoingCall', '--es', 'number', phone_number,
        '--ei', 'presentation', '1', '--es', 'cnap', 'SomeCnap')

  def stop_dialer(self) -> None:
    """Stops Dialer app."""
    self._device.adb.shell(['am', 'force-stop', DIALER_PACKAGE_NAME])


def make_3way_call(
    device: Device,
    outgoing_call_number1: str = '9876543210',
    outgoing_call_number2: str = '9876543211'):
  """Makes 3way conference call."""
  uip = ui_core.UIPage.from_device(device)
  dut_with_dialer_simulator = hfp_devices.AndroidPhoneWithDialerSimulator(device)
  device.log.info('Making first outgoing call to "%s"...', outgoing_call_number1)
  dut_with_dialer_simulator.ds.make_outgoing_call(
      phone_number=outgoing_call_number1, allow_multiple_call=True)

  # Phone call is in background
  if uip.get_node_by_content_desc('Ongoing phone call', wait_sec=3):
    uip.click_node_by_content_desc('Ongoing phone call')

  device.log.info('Onholding the first outgoing call...')
  uip.refresh()
  uip.click_node_by_content_desc('Show more')
  uip.click_node_by_content_desc('Hold call')

  device.log.info('Making second outgoing call to "%s"...', outgoing_call_number2)
  dut_with_dialer_simulator.ds.make_outgoing_call(
      phone_number=outgoing_call_number2, allow_multiple_call=True)

  device.log.info('Merging the second outgoing call...')
  uip.refresh()
  uip.click_node_by_content_desc('Show more')
  uip.click_node_by_content_desc('Merge calls')
  assert uip.get_node_by_text('Conference call')

  return dut_with_dialer_simulator
