# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Utility to support common Media control operations/methods."""
import re
from typing import TypeAlias, Union

from mobly.controllers import android_device

import bttc
from bttc import core
from bttc import mc_data
from bttc.utils import device_factory


PLAYBACK_STATE_LOG_PATTERN = mc_data.PLAYBACK_STATE_LOG_PATTERN
PlaybackState = mc_data.PlaybackState
BINDING_KEYWORD = 'mc'
AUTO_LOAD = True
ANDROID_DEVICE: TypeAlias = android_device.AndroidDevice


class MCModule(core.UtilBase):
  """Class to hold Media control related functions define in this module."""

  NAME = BINDING_KEYWORD
  DESCRIPTION = 'Utility to support medica control operations.'

  def __init__(self, ad: ANDROID_DEVICE):
    super().__init__(ad)
    self._bind(get_media_playback_state)
    self._bind(play_local_wav_file)

  def get_yt_music_playback_state(self) -> PlaybackState:
    """Gets Youtube Music Playback state."""
    return self.get_media_playback_state(mc_data.YT_MUSIC_PACKAGE)

  def play(self):
    self._ad.ke.key_media_play()

  def pause(self):
    self._ad.ke.key_media_pause()

  def next(self):
    self._ad.ke.key_media_next()

  def previous(self):
    self._ad.ke.key_media_previous()


def _dump_media_session(device: ANDROID_DEVICE, package: str) -> str:
  """Dumps the media session of an android device.

  Args:
    device: Android device.
    package: Package name.

  Returns:
    Dumped output on the device.
  """
  cmd = f'dumpsys media_session | egrep -A10 package={package}'
  return device.adb.shell(cmd).decode('utf-8').strip()


def _is_under_supported_activity(device: ANDROID_DEVICE) -> bool:
  """Checks if current activity is supported for Medica control operations."""
  pass


def bind(
    ad: Union[ANDROID_DEVICE, str],
    init_mbs: bool = False,
    init_sl4a: bool = False,
    init_snippet_uiautomator: bool = False,
    init_tl4a: bool = False) -> ANDROID_DEVICE:
  """Binds the input device with functions defined in module `bt_utils`.

  Sample Usage:
  ```python
  >>> from bttc import bt_utils
  >>> ad = bt_utils.bind('35121FDJG0005P', init_mbs=True, init_sl4a=True)
  >>> ad.bt.is_bluetooth_enabled()
  True
  >>> ad.bt.list_paired_devices()
  ['Galaxy Buds2 Pro', 'Galaxy Buds2 Pro']
  ```

  Args:
    ad: If string is given, it stands for serial of device. Otherwise, it should
        be the Android device object.
    init_mbs: True to initialize the MBS service of given device.
    init_sl4a: True to initialize the SL4A service of given device.

  Returns:
    The device with binded functions defined in `bt_utils`.
  """
  device = device_factory.get(
      ad, init_mbs=init_mbs,
      init_sl4a=init_sl4a,
      init_snippet_uiautomator=init_snippet_uiautomator,
      init_tl4a=init_tl4a)
  device.load_config({BINDING_KEYWORD: MCModule(device)})


def get_media_playback_state(
    device: ANDROID_DEVICE,
    package: str) -> PlaybackState:
  """Gets media playback state of an android device.

  Args:
    device: Android device.
    package: Package name.

  Returns:
    Playback state.
  """
  dump_output = _dump_media_session(device, package)
  match = re.search(PLAYBACK_STATE_LOG_PATTERN, dump_output)
  if match is None:
    device.log.warning(
        'No matches found with regex. pattern=%s, string=%s',
        PLAYBACK_STATE_LOG_PATTERN,
        dump_output)
    return PlaybackState.UNRECOGNIZED

  state = int(match.group(1))
  playback_state = PlaybackState(state)
  device.log.info('Playback state of %s: %s', package, playback_state.name)
  return playback_state


def play_local_wav_file(
    device: ANDROID_DEVICE,
    wav_file_path: str) -> bool:
  """Plays wav file from local file system.

  Args:
    device: Android device.
    wav_file_path: Path of local WAV file to play.

  Returns:
    True iff action is succeeded.

  Raises:
    ValueError: If the given WAV file path does not exist.
    Exception: Failed to play WAF file.
  """
  stdout, _, rt_code = bttc.safe_adb_shell(device)(
      f'file {wav_file_path}')
  if rt_code != 0 or 'cannot open' in stdout.strip():
    raise ValueError(
        f'Fail to read "{wav_file_path}": {stdout.strip()} (rt={rt_code})')

  composed_adb_command = (
      f'am start -a android.intent.action.VIEW -d file://{wav_file_path}'
      ' -t audio/wav')
  stdout, _, rt_code = bttc.safe_adb_shell(device)(composed_adb_command)
  if rt_code != 0:
    raise Exception(
        f'Failed to play "{wav_file_path}": {stdout} (rt={rt_code})')

  return True
