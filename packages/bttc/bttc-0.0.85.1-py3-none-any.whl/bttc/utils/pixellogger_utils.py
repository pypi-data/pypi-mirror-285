"""Utility to handle pixelloger operations."""

import dataclasses
import datetime
import functools
import logging
import pathlib
import time
from typing import Callable, TypeAlias

from bttc.utils import retry
from mobly.controllers import android_device


_PIXELLOGGER_TIMEOUT = datetime.timedelta(seconds=600)
_LS_AUDIO_DUMP_LOGGER_STATUS_PROPERTY_NAME = 'vendor.audiodump.enable'
_QC_MASK = 'BT_Audio.cfg'
_LS_MASK = 'Lassen default + audio + TCP'
_PIXELLOGGER_COMMON_CMD = (
    'am broadcast -n com.android.pixellogger/.receiver.AlwaysOnLoggingReceiver '
    '-a com.android.pixellogger.service.logging.LoggingService.'
    'ACTION_CONFIGURE_ALWAYS_ON_LOGGING -e intent_key_enable')
ANDROID_DEVICE: TypeAlias = android_device.AndroidDevice


@dataclasses.dataclass(frozen=True)
class PixelLoggerParams:
  """Pixellogger parameters for control pixellogger apps."""
  name: str
  start: str
  stop: str
  status: str
  log_path: str
  timeout: datetime.timedelta


@functools.cache
def get_pixel_logger_params(chipset_info: str) -> PixelLoggerParams | None:
  if 'Qualcomm' in chipset_info:
    return PixelLoggerParams(
        name='Qualcomm',
        start=(
            f'{_PIXELLOGGER_COMMON_CMD} "true" '
            f'-e intent_key_config "{_QC_MASK}" '
            '--ei intent_key_max_log_size_mb 100 '
            '--ei intent_key_max_number_of_files 100'),
        stop=f'{_PIXELLOGGER_COMMON_CMD} "false"',
        status='vendor.sys.modem.diag.mdlog_on',
        log_path='/data/vendor/radio/diag_logs/logs',
        timeout=_PIXELLOGGER_TIMEOUT,
    )
  elif 'Samsung' in chipset_info:
    return PixelLoggerParams(
        name='Lassen',
        start=(
            f'{_PIXELLOGGER_COMMON_CMD} "true" '
            f'-e intent_key_config "{_LS_MASK}" '
            '--ei intent_key_max_log_size_mb 100 '
            '--ei intent_key_max_number_of_files 100'),
        stop=f'{_PIXELLOGGER_COMMON_CMD} "false"',
        status='vendor.sys.modem.logging.status',
        log_path='/data/vendor/radio/logs/always-on',
        timeout=_PIXELLOGGER_TIMEOUT,
    )
  else:
    logging.warning(
        'PixelLogger disabled - Unknown chipset: "%s"', chipset_info)
    return None


class Broker:
  """Broker to handle operations of pixellogger.

  Attributes:
    ad: Android device.
  """

  def __init__(self, ad: ANDROID_DEVICE):
    self._ad = ad
    self._pixellogger_params = get_pixel_logger_params(self.ad.gm.chipset)

  @property
  def ad(self) -> ANDROID_DEVICE:
    return self._ad

  @property
  def pixellogger_params(self) -> PixelLoggerParams | None:
    return self._pixellogger_params

  def _clear_qxdm_log(self) -> None:
    """Clears Pixellogger from embedded log path."""
    assert self.pixellogger_params is not None
    self.ad.log.info('Clearing saved QXDM log...')
    target_path = pathlib.PurePosixPath(self.pixellogger_params.log_path, '*')
    self.ad.adb.shell(f'rm -rf {str(target_path)}')
    self.ad.log.info('QXDM log has Cleared.')

  def _is_audiodump_logger_running(self) -> bool:
    """Gets the status of AudioDump Logger.

    Returns:
      True if the AudioDump Logger is runninng.
    Raises:
      RuntimeError: If AudioDump Logger stuck at unexpected status.
    """
    assert self.pixellogger_params is not None
    timeout = datetime.datetime.now() + self._pixellogger_params.timeout
    while datetime.datetime.now() < timeout:
      prop = self.ad.gm.props['vendor.audiodump.enable']
      if not prop:
        return False
      if prop == 'running':
        return True
      elif prop == 'off':
        return False
      time.sleep(1)
    raise RuntimeError(
        f'AudioDump Logger stuck at {prop} status '
        f'over {self._pixellogger_params.timeout.total_seconds()} seconds.')

  def _start_audiodump_logger(self) -> None:
    """Starts AudioDump Logger."""
    assert self.pixellogger_params is not None
    if self._is_audiodump_logger_running():
      self._stop_audiodump_logger()
      self._clear_qxdm_log()
    self.ad.log.info('Starting AudioDump Logger...')
    # Set logging config file to BT/USB/Headset
    self.ad.adb.shell(
        'setprop vendor.audiodump.log.config peripheral_device')
    self.ad.adb.shell('setprop vendor.audiodump.output.dir ' +
                      self._pixellogger_params.log_path)
    self.ad.adb.shell('setprop vendor.audiodump.log.ondemand true')
    self._wait_logger_action_ready(self._is_audiodump_logger_running,
                                   'AudioDump Logger', 'start')

  def _stop_audiodump_logger(self) -> None:
    """Stops AudioDump Logger."""
    if self._is_audiodump_logger_running():
      self.ad.log.info('Stopping AudioDump Logger...')
      self.ad.adb.shell('setprop vendor.audiodump.log.ondemand false')
      self._wait_logger_action_ready(
          self._is_audiodump_logger_running,
          'AudioDump Logger', 'stop')
    else:
      self._ad.log.info('AudioDump Logger has stopped')

  def _wait_logger_action_ready(self, check_func: Callable[[], bool],
                                logger_name: str, action: str) -> None:
    """Waits Logger action ready.

    Args:
      check_func: Function to query the status of Logger.
      logger_name: Logger name.
      action: Start or stop action.

    Raises:
      RuntimeError: If Logger failed to action.
    """
    assert self.pixellogger_params is not None
    timeout = datetime.datetime.now() + self.pixellogger_params.timeout
    while datetime.datetime.now() < timeout:
      time.sleep(1)
      if action == 'start':
        if check_func():
          self.ad.log.info(f'{logger_name} has started')
          return
      else:
        if not check_func():
          self.ad.log.info(f'{logger_name} has stopped')
          return
    raise RuntimeError(
        f'Timed out while waiting for {logger_name} to {action} '
        f'over {self._pixellogger_params.timeout.total_seconds()} seconds.')

  def is_running(self) -> bool:
    """Gets the status of Pixellogger.

    Returns:
      True if the Pixellogger is runninng.
    """
    if self.pixellogger_params:
      return 'true' in self.ad.gm.props[self.pixellogger_params.status]

    return False

  def stop(self):
    """Stops the pixellogger."""
    assert self.pixellogger_params is not None
    self.ad.log.info('Stopping Pixellogger...')
    self.ad.adb.shell(self.pixellogger_params.stop)
    self._wait_logger_action_ready(
        self.is_running, 'Pixellogger', 'stop')

    if self.pixellogger_params.name == 'Lassen':
      self._stop_audiodump_logger()

  @retry.retry_on_exception(
      retry_value=RuntimeError,
      retry_intervals=retry.FuzzedExponentialIntervals(
          initial_delay_sec=1, num_retries=2))
  def start(self) -> bool:
    """Starts the pixellogger."""
    if not self.pixellogger_params:
      logging.warning(
          'Skip starting Pixel Logger because chipset="%s" is not supported!',
          self.ad.gm.chipset)
      return False

    if self.is_running():
      self.stop()
      self._clear_qxdm_log()

    self.ad.log.info('Starting Pixellogger...')
    self.ad.adb.shell(self.pixellogger_params.start)
    self._wait_logger_action_ready(
        self.is_running, 'Pixellogger', 'start')

    if self.pixellogger_params.name == 'Lassen':
      self._start_audiodump_logger()

    return self.is_running()
