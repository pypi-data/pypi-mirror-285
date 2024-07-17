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

"""Module to hold data used in Medica control module `mc_utils`."""
import enum


PLAYBACK_STATE_LOG_PATTERN = r'state=PlaybackState {state=[\w(]*(\d)[)]*'
YT_MUSIC_PACKAGE = 'com.google.android.apps.youtube.music'


class MediaKeyCode(enum.Enum):
  """Media key codes."""
  NEXT = 87
  PREVIOUS = 88
  PLAY = 126
  PAUSE = 127


class PlaybackState(enum.Enum):
  """Playback states."""
  NONE = 0
  STOPPED = 1
  PAUSED = 2
  PLAYING = 3
  BUFFERING = 6
  ERROR = 7
  UNRECOGNIZED = -1
