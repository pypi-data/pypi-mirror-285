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

"""Module to hold implementation of Youtube Music Player Agent."""
import logging
import time

from mobly.controllers import android_device
from bttc import mc_data
from bttc.utils.media_player import media_player_agent_facade
from bttc.utils.ui_pages import ui_core
from typing import Any, TypeAlias


AndroidDevice: TypeAlias = android_device.AndroidDevice
PlaybackState = mc_data.PlaybackState
MAIN_PAGE_BROWSE_CONTENT_RID = (
    'com.google.android.apps.youtube.music:id/browse_content')
MAIN_PAGE_AVATOR_MENU_BUTTON_RID = (
    'com.google.android.apps.youtube.music:id/avatar_menu_button')
PLAY_PAGE_TIME_RID = (
    'com.google.android.apps.youtube.music:id/time_bar')

YT_MUSIC_PACKAGE = 'com.google.android.apps.youtube.music'


class YTPlayerAgent(media_player_agent_facade.MediaPlayerAgent):
  """Youtube Music Player Agent class."""

  def __init__(self, device: AndroidDevice):
    self.log = logging.getLogger(self.__class__.__name__)
    self._ad = device
    self._uip = ui_core.UIPage.from_device(self._ad)

  @property
  def ad(self):
    return self._ad

  @property
  def uip(self):
    return self._uip

  def _wait_playback_state(
      self, state: PlaybackState, retry_num: int = 5):
    while True:
      if self.ad.mc.get_yt_music_playback_state() == state:
        break

      if retry_num == 0:
        raise Exception(f'Failed to wait for {state}!')

      self.log.info('Waiting for %s...retry=%s', state, retry_num)
      time.sleep(2)
      retry_num -= 1

  def is_main_page(self):
    """Checks if current activity is main page."""
    return self._ad.ui(resourceId=MAIN_PAGE_AVATOR_MENU_BUTTON_RID).exists

  def is_play_page(self, wait_time_sec: int = 5):
    """Checks if current activity is play page."""
    if self._ad.ui(resourceId=PLAY_PAGE_TIME_RID).exists:
      return True

    time.sleep(wait_time_sec)
    return self._ad.ui(resourceId=PLAY_PAGE_TIME_RID).exists

  def initialize(self):
    """Initializes the media player agent."""
    self._ad.adb.shell(f'pm clear {YT_MUSIC_PACKAGE}')
    self._ad.adb.shell(
        f'pm grant {YT_MUSIC_PACKAGE} android.permission.POST_NOTIFICATIONS')
    self._ad.adb.shell(f'am start -S {YT_MUSIC_PACKAGE}')
    retry_count = 5
    is_done = False
    while not (is_done := self.is_main_page()) and retry_count > 0:
      self.log.info('Entering YTM page...retry=%s', retry_count)
      self._ad.adb.shell(f'am start {YT_MUSIC_PACKAGE}')
      retry_count -= 1
      time.sleep(2)

    if not is_done:
      self.uip.refresh()
      raise Exception(
          'Failed to initialize YTM player agent:'
          f'\n{self.uip.parsed_ui.ui_xml.toxml()}\n')

    self._ad.ui(
        textMatches='Device files only|DEVICE FILES ONLY').click.wait(10)
    self._ad.ui(textMatches='Allow|ALLOW').click.wait(10)

  def free(self):
    """Frees the media player agent resource."""
    self._ad.adb.shell(
        ['am', 'kill', 'com.google.android.apps.youtube.music'])
    self._ad.ke.key_home()

  def get_metadata(self) -> Any:
    """Gets metadata of current track."""
    self.log.warning('Not supported to get metadata!')

  def play(self):
    """Plays media."""
    if self.is_main_page():
      self.log.info('Random select music to play...')
      self.uip.refresh()
      nodes = self.uip.get_all_nodes_by_attrs({'NAF': 'true'}, from_all=True)
      if len(nodes) < 3:
        raise Exception(
            f'Unexpected UI page content:\n'
            f'{self.uip.parsed_ui.ui_xml.toxml()}\n')
      for ni in range(2, 4):
        try:
          self.uip.click(nodes[ni])
          self._wait_playback_state(PlaybackState.PLAYING)
          break
        except Exception:
          self.uip.back()
          continue
    elif self.is_play_page():
      self.log.info('Under play page and continue playing...')
      self._ad.mc.play()

    self._wait_playback_state(PlaybackState.PLAYING)
    self.uip.refresh()

  def pause(self):
    """Pauses media."""
    if not self.is_play_page():
      raise Exception(
          f'Not in playing page:\n{self.uip.parsed_ui.ui_xml.toxml()}\n')
    self._ad.mc.pause()
    self._wait_playback_state(PlaybackState.PAUSED)
    self.uip.refresh()

  def next_track(self):
    """Goes to next track."""
    if not self.is_play_page():
      raise Exception(
          f'Not in playing page:\n{self.uip.parsed_ui.ui_xml.toxml()}\n')
    self._ad.mc.next()
    self._wait_playback_state(PlaybackState.PLAYING)
    self.uip.refresh()

  def previous_track(self):
    """Goes to previous track."""
    if not self.is_play_page():
      raise Exception(
          f'Not in playing page:\n{self.uip.parsed_ui.ui_xml.toxml()}\n')
    self._ad.mc.previous()
    self._wait_playback_state(PlaybackState.PLAYING)
    self.uip.refresh()
