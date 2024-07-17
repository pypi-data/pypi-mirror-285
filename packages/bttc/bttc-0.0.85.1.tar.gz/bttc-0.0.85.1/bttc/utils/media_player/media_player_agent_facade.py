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

"""Media player agent facade for Media player operations."""

from typing import Any, Protocol


class MediaPlayerAgent(Protocol):
  """Media player agent base class."""

  def initialize(self):
    """Initializes the media player agent."""
    pass

  def free(self):
    """Frees the media player agent resource."""
    pass

  def get_metadata(self) -> Any:
    """Gets metadata of current track."""
    pass

  def play(self):
    """Plays media."""
    pass

  def pause(self):
    """Pauses media."""
    pass

  def next_track(self):
    """Goes to next track."""
    pass

  def previous_track(self):
    """Goes to previous track."""
    pass
