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

"""Module to hold data used in general utility module `genral_utils`."""

import dataclasses
import functools
import enum


@dataclasses.dataclass
class ActivityRecord:
  """Dataclass to represent UI Activity. e.g.:
  'com.google.android.apps.youtube.music/.activities.MusicActivity'
  """

  full_activity_path: str

  @property
  def package(self) -> str:
    """The package part of activity.

    Take activity below for example:
    'com.google.android.apps.youtube.music/.activities.MusicActivity'

    The package of it will be:
    'com.google.android.apps.youtube.music'
    """
    return self.full_activity_path.split('/')[0]


@dataclasses.dataclass
class AudioStreamVolume:
  """The dataclass to hold parsing result of volume from `dumpsys audio`.

  One stream volume record for example:
  ```
  - STREAM_VOICE_CALL:
    Muted: false
    Muted Internally: false
    Min: 1
    Max: 7
    streamVolume:5
    Current: 1 (earpiece): 5, 80 (bt_a2dp): 5, 40000000 (default): 5
    Devices: earpiece(1)
    Volume Group: AUDIO_STREAM_VOICE_CALL
  ```

  Attributes:
    name: Name of audio stream.
    is_muted: True iff the audio is muted.
    min_level: Minimum of volume level.
    max_level: Maximum of volume level.
    stream_volume_level: Stream volume level.
    current: Current device.
    devices: Device information.
  """

  name: str
  is_muted: bool = False
  min_level: int = -1
  max_level: int = -1
  stream_volume_level: int = -1
  current: int = -1
  devices: str | None = None


@dataclasses.dataclass(frozen=True)
class VolumeBound:
  """Class to store volume boundary value.

  Attributes:
    key: The volume type (key).
    stream_type: The stream type defined in the android api.
    min: The min volume value.
    max: The max volume value.
  """
  key: str
  stream_type: str
  min: int
  max: int


@dataclasses.dataclass(frozen=True)
class VolumeSetting:
  """Dataclass to store current volume setting.

  Attributes:
    level: volume level
    stream_type: The stream type defined in the android api.
    is_max: True to be max level.
    is_min: True to be min level.
  """
  level: int
  is_max: bool = False
  is_min: bool = False


@enum.unique
class VolumeType(enum.Enum):
  """Volume type enumeration."""
  BluetoothSco = enum.auto()
  BluetoothScoBtA2dp = enum.auto()
  Music = enum.auto()
  MusicSpeaker = enum.auto()
  MusicBleHeadset = enum.auto()
  MusicBtA2dp = enum.auto()
  System = enum.auto()
  Voice = enum.auto()
  VoiceEarpiece = enum.auto()
  Ring = enum.auto()
  RingSpeaker = enum.auto()
  Alarm = enum.auto()
  AlarmSpeaker = enum.auto()

  @functools.cached_property
  def m(self):
    """Gets metadata."""
    if self == self.Alarm:
      return VolumeBound('volume_alarm', '', 0, 25)
    elif self == self.BluetoothSco:
      return VolumeBound('volume_bluetooth_sco', '', 0, 25)
    elif self == self.BluetoothScoBtA2dp:
      return VolumeBound('volume_bluetooth_sco_bt_a2dp', '', 0, 25)
    elif self == self.Music:
      return VolumeBound('volume_music', '', 0, 25)
    elif self == self.MusicSpeaker:
      return VolumeBound('volume_music_speaker', '3', 0, 25)
    elif self == self.MusicBleHeadset:
      return VolumeBound('volume_music_ble_headset', '', 0, 25)
    elif self == self.MusicBtA2dp:
      return VolumeBound('volume_music_bt_a2dp', '', 0, 25)
    elif self == self.Ring:
      return VolumeBound('volume_ring', '', 0, 25)
    elif self == self.System:
      return VolumeBound('volume_system', '', 0, 25)
    elif self == self.Voice:
      return VolumeBound('volume_voice', '', 0, 25)
    elif self == self.VoiceEarpiece:
      return VolumeBound('volume_voice_earpiece', '0', 1, 7)
    elif self == self.RingSpeaker:
      return VolumeBound('volume_ring_speaker', '2', 0, 7)
    elif self == self.AlarmSpeaker:
      return VolumeBound('volume_alarm_speaker', '4', 1, 7)

    raise ValueError(f'Unknown enum type: {self}')
