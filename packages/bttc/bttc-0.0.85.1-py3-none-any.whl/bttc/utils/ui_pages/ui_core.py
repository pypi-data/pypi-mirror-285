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

"""UI core module for UI page operations."""
from __future__ import annotations
import itertools
import logging
import shlex
import time
from typing import Any, Callable, Generator, Iterable, TypeAlias

from mobly.controllers import android_device

from bttc.utils import ui_pages
from bttc.utils.ui_pages import errors
from bttc.utils.ui_pages import ui_node
from bttc.utils.ui_pages import utils


AndroidDevice: TypeAlias = android_device.AndroidDevice

# Return type of node generator.
NodeGenerator = Generator[ui_node.UINode, None, None]

# Return type of otpional UINode.
OptUINode: TypeAlias = ui_node.UINode | None


class UIPage:
  """Object to represent the current UI page."""

  def __init__(
      self,
      device: AndroidDevice,
      parsed_ui: ui_pages.ParsedUI | None = None) -> None:
    self.log = logging.getLogger(self.__class__.__name__)
    self._ad = device
    self._parsed_ui = parsed_ui
    if self._parsed_ui is None:
      self.refresh()

  @property
  def ad(self):
    return self._ad

  @property
  def clickable_nodes(self):
    return self._parsed_ui.clickable_nodes

  @property
  def enabled_nodes(self):
    return self._parsed_ui.enabled_nodes

  @property
  def all_nodes(self):
    return self._parsed_ui.all_nodes

  @property
  def parsed_ui(self):
    return self._parsed_ui

  @property
  def ui_device(self) -> Any:
    """Gets UI device object of service "uiautomator"."""
    registered_services = self.ad.services.list_live_services()
    if 'uiautomator' in registered_services:
      ui_device = getattr(
          self.ad, 'ui',
          getattr(self.ad, 'uia', None))

      if not ui_device:
        raise errors.ContextError(
            self,
            'Please use public service name "ui" or "uia" for "uiautomator"!')
      return ui_device

    return None

  @property
  def xml_content(self) -> str:
    """Gets XML content of current page."""
    if self.parsed_ui.ui_xml is None:
      return 'xml_content is None!'

    return (
        self.parsed_ui.ui_xml if isinstance(self.parsed_ui.ui_xml, str)
        else self.parsed_ui.ui_xml.toxml())

  @classmethod
  def from_device(cls, device: AndroidDevice) -> UIPage:
    """Get UI page object from device."""
    return UIPage(device=device)

  def _get_node_search_space(
      self, from_all: bool = False) -> Iterable[ui_node.UINode]:
    """Gets the search space of node."""
    if from_all:
      return itertools.chain(
          self.all_nodes, self.clickable_nodes, self.enabled_nodes)
    else:
      return itertools.chain(self.clickable_nodes, self.enabled_nodes)

  def back(self) -> UIPage:
    """Gets back to previous page.

    Returns:
      The transformed page object.
    """
    if self.ui_device:
      self.log.debug('Back to previous page by uiautomator...')
      self.ui_device.press.back()
      return self.refresh()

    self.log.debug('Back to previous page by keycode "BACK"...')
    self.ad.ke.key_back()
    return self.refresh()

  def refresh(self) -> UIPage:
    """Refreshes current page with obtained latest page.

    Args:
      new_page: The page with latest data for current page to be refreshed.

    Returns:
      The current refreshed UI page object.
    """
    self._parsed_ui = ui_pages.parse_ui(self._ad)
    return self

  def get_node_by_content_desc(self,
                               content_desc: str,
                               from_all: bool = False,
                               use_re: bool = False,
                               wait_sec: int = 5) -> OptUINode:
    """Gets the first node with desired content description.

    Args:
      content_desc: Content description used for search.
      from_all: True to search from all nodes; False to search only the
        clickable or enabled nodes.
      use_re: Use regular expression iff True.
      wait_sec: Waiting time for target node in seconds.

    Returns:
      Return the first node found with expected content description
      iff it exists. Otherwise, None is returned.
    """
    match_strategy = (
        utils.RETextMatchStrategy(content_desc)
        if use_re else utils.PlainTextMatchStrategy(content_desc))

    for _ in range(wait_sec):
      for node in self._get_node_search_space(from_all):
        if match_strategy.match(node.content_desc):
          return node

      time.sleep(1)
      self.refresh()

    return None

  def get_node_by_func(self,
                       func: Callable[[ui_node.UINode], bool],
                       from_all: bool = False) -> OptUINode:
    """Gets the first node found by given function.

    Args:
      func: The function to search target node.
      from_all: True to search from all nodes; False to search only the
        clickable or enabled nodes.

    Returns:
      The node found by given function.
    """
    for node in self._get_node_search_space(from_all):
      if func(node):
        return node

    return None

  def get_node_by_text(self,
                       text: str,
                       from_all: bool = False,
                       search_clickable: bool = False,
                       use_re: bool = False,
                       wait_sec: int = 5) -> OptUINode:
    """Gets the first node with desired text.

    Args:
      text: Text used for search.
      from_all: True to search from all nodes; False to search only the
        clickable or enabled nodes.
      search_clickable: True to search node with attribute clickable="true"
      use_re: True will treat input text as regular expression to search node.
      wait_sec: Waiting time for target node in seconds.

    Returns:
      Return the first node found with expected text iff it exists.
      Otherwise, None is returned.
    """
    match_strategy = (
        utils.RETextMatchStrategy(text)
        if use_re else utils.PlainTextMatchStrategy(text))
    for _ in range(wait_sec):
      for node in self._get_node_search_space(from_all):
        if search_clickable and not node.clickable:
          continue

        if match_strategy.match(node.text):
          return node
      self.refresh()
      time.sleep(1)

    return None

  def _yield_node_by_rid(self,
                         rid: str,
                         from_all: bool = False) -> NodeGenerator:
    """Generates node with desired resource id."""
    for node in self._get_node_search_space(from_all):
      if ('resource-id' in node.attributes and
          node.attributes['resource-id'].value == rid):
        yield node

  def get_all_nodes_by_rid(self,
                           rid: str,
                           from_all: bool = False) -> list[ui_node.UINode]:
    """Gets all nodes with desired resource id.

    Args:
      rid: Resource id used for search.
      from_all: True to search from all nodes; False to search only the
        clickable or enabled nodes.

    Returns:
      The list of nodes found with expected resource id.
    """
    found_node_set = set(self._yield_node_by_rid(rid, from_all))
    return list(found_node_set)

  def get_node_by_rid(self,
                      rid: str,
                      from_all: bool = False) -> ui_node.UINode | None:
    """Gets the first node with desired resource id.

    Args:
      rid: Resource id used for search.
      from_all: True to search from all nodes; False to search only the
        clickable or enabled nodes.

    Returns:
      Return the first node found with expected resource id iff it exists.
      Otherwise, None.
    """
    try:
      return next(self._yield_node_by_rid(rid, from_all))
    except StopIteration:
      return None

  def get_node_by_class(self,
                        class_name: str,
                        from_all: bool = False) -> ui_node.UINode | None:
    """Gets the first node with desired class.

    Args:
      class_name: Name of class as attribute.
      from_all: True to search from all nodes; False to search only the
        clickable or enabled nodes.

    Returns:
      Return the first node found with desired class iff it exists.
      Otherwise, None.
    """
    for node in self._get_node_search_space(from_all):
      if node.clz == class_name:
        return node

    return None

  def get_node_by_attrs(self,
                        attrs: dict[str, Any],
                        from_all: bool = False) -> OptUINode:
    """Gets the first node with the given attributes.

    Args:
      attrs: Attributes used to search target node.
      from_all: True to search from all nodes; False to search only the
        clickable or enabled nodes.

    Returns:
      Return the first UI node with expected attributes iff it exists.
      Otherwise, None is returned.
    """
    for node in self._get_node_search_space(from_all):
      if node.match_attrs(attrs):
        return node

    return None

  def get_all_nodes_by_attrs(
      self,
      attrs: dict[str, Any],
      from_all: bool = False) -> list[ui_node.UINode]:
    """Gets all node(s) with the given attributes.

    Args:
      attrs: Attributes used to search target node.
      from_all: True to search from all nodes; False to search only the
        clickable or enabled nodes.

    Returns:
      Return list of nodes that matched desired attributes.
    """
    node_list = []
    for node in self._get_node_search_space(from_all):
      if node.match_attrs(attrs):
        node_list.append(node)

    return node_list

  @utils.dr_wakeup_before_op
  def swipe(self,
            start_x: int,
            start_y: int,
            end_x: int,
            end_y: int,
            duration_ms: int,
            swipes: int = 1) -> UIPage:
    """Performs the swipe from one coordinate to another coordinate.

    Args:
      start_x: The starting X-axis coordinate.
      start_y: The starting Y-axis coordinate.
      end_x: The ending X-axis coordinate.
      end_y: The ending Y-axis coordinate.
      duration_ms: The millisecond of duration to drag.
      swipes: How many swipe to carry on.

    Returns:
      The transformed UI page.
    """
    for _ in range(swipes):
      self._ad.adb.shell(
          shlex.split(
              f'input swipe {start_x} {start_y} {end_x} {end_y} {duration_ms}'))

    return self.refresh()

  def swipe_left(self,
                 duration_ms: int = 1000,
                 x_start: float = 0.2,
                 x_end: float = 0.9,
                 swipes: int = 1) -> UIPage:
    """Performs the swipe left action.

    Args:
      duration_ms: Number of milliseconds to swipe from start point to end
        point.
      x_start: The range of width as start position
      x_end: The range of width as end position
      swipes: Round to conduct the swipe action.

    Returns:
      The transformed UI page.
    """
    width, height = ui_pages.get_display_size(self._ad)
    self.log.info('Page size=(%d, %d)', width, height)
    return self.swipe(
        width * x_start,
        height * 0.5,
        width * x_end,
        height * 0.5,
        duration_ms=duration_ms,
        swipes=swipes)

  def swipe_right(self,
                  duration_ms: int = 1000,
                  x_start: float = 0.9,
                  x_end: float = 0.2,
                  swipes: int = 1) -> UIPage:
    """Performs the swipe right action.

    Args:
      duration_ms: Number of milliseconds to swipe from start point to end
        point.
      x_start: The range of width as start position
      x_end: The range of width as end position
      swipes: Round to conduct the swipe action.

    Returns:
      The transformed UI page.
    """
    width, height = ui_pages.get_display_size(self._ad)
    return self.swipe(
        width * x_start,
        height * 0.5,
        width * x_end,
        height * 0.5,
        duration_ms=duration_ms,
        swipes=swipes)

  def swipe_down(self,
                 duration_ms: int = 1000,
                 swipes: int = 1,
                 y_start: float = 0.7,
                 y_end: float = 0.2,
                 x_portion: float = 0.3) -> UIPage:
    """Performs the swipe down action.

    Args:
      duration_ms: Number of milliseconds to swipe from start point to end
        point.
      swipes: Round to conduct the swipe action.
      y_start: The portion of start position in terms of y-axis.
      y_end: The portion of end position in terms of y-axis.
      x_portion: The portion of x-axis.

    Returns:
      The transformed UI page.
    """
    width, height = ui_pages.get_display_size(self._ad)
    return self.swipe(
        width * x_portion,
        height * y_start,
        width * x_portion,
        height * y_end,
        duration_ms=duration_ms,
        swipes=swipes)

  def swipe_up(self,
               duration_ms: int = 1000,
               swipes: int = 1,
               y_start: float = 0.2,
               y_end: float = 0.7) -> UIPage:
    """Performs the swipe up action.

    Args:
      duration_ms: Number of milliseconds to swipe from start point to end
        point.
      swipes: Round to conduct the swipe action.
      y_start: The portion of start position in terms of y-axis.
      y_end: The portion of end position in terms of y-axis.

    Returns:
      The transformed UI page.
    """
    width, height = ui_pages.get_display_size(self._ad)
    return self.swipe(
        width * 0.5,
        height * y_start,
        width * 0.5,
        height * y_end,
        duration_ms=duration_ms,
        swipes=swipes)

  def click_on(self, x: int, y: int, duration: int = -1) -> None:
    """Clicks on the given X/Y coordinates.

    Args:
      x: X-axis coordinate
      y: Y-axis coordinate
      duration: tap curation in ms.

    Raises:
      acts.controllers.adb.AdbError: If the adb shell command
        failed to execute.
    """
    duration_str = str(duration) if duration > 0 else ''
    self.ad.adb.shell(shlex.split(f'input tap {x} {y} {duration_str}'))

  @utils.dr_wakeup_before_op
  def click(self,
            node: ui_node.UINode,
            do_get_page: bool = True,
            duration: int = -1) -> UIPage | None:
    """Clicks the given UI node.

    Args:
      node: Node to click on.
      do_get_page: Gets the latest page after clicking iff True.
      duration: tap curation in ms.

    Returns:
      The transformed UI page is returned iff `do_get_page` is True.
      Otherwise, None is returned.
    """
    self.click_on(node.x, node.y, duration=duration)
    if do_get_page:
      self.refresh()

    return self

  def click_node_by_rid(self,
                        node_rid: str,
                        do_get_page: bool = True) -> UIPage:
    """Clicks on node its resource id.

    Args:
      node_rid: Resource ID of node to search and click on.
      do_get_page: Gets the latest page after clicking iff True.

    Returns:
      The transformed page.

    Raises:
      errors.UIError: Fail to get target node.
    """
    node = self.get_node_by_rid(node_rid)
    if node is None:
      raise errors.UIError(f'Fail to find the node with resource id={node_rid}')

    return self.click(node, do_get_page)

  def click_node_by_text(self,
                         text: str,
                         do_get_page: bool = True,
                         use_re: bool = False,
                         search_clickable: bool = True,
                         wait_sec: int = 5) -> UIPage:
    """Clicks on node by its text.

    Args:
      text: Text of node to search and click on.
      do_get_page: Gets the latest page after clicking iff True.
      use_re: True will treat input text as regular expression to search node.
      search_clickable: True to search node with attribute clickable="true".
      wait_sec: Waiting time for target node in seconds.

    Returns:
      The transformed page.

    Raises:
      errors.UIError: Fail to get target node.
    """
    node = self.get_node_by_text(
        text, use_re=use_re, search_clickable=search_clickable,
        wait_sec=wait_sec)
    if node is None:
      raise errors.UIError(f'Fail to find the node with text={text} ({self})')

    self.click(node, do_get_page)
    self.refresh()
    return self

  def click_node_by_content_desc(self,
                                 text: str,
                                 do_get_page: bool = True) -> UIPage:
    """Clicks on node by its content description.

    Args:
      text: Content description of node to search and click on.
      do_get_page: Gets the latest page after clicking iff True.

    Returns:
      The transformed page.

    Raises:
      errors.UIError: Fail to get target node.
    """
    node = self.get_node_by_content_desc(text)
    if node is None:
      raise errors.UIError(
          f'Fail to find the node with content description={text}')

    return self.click(node, do_get_page)

  def click_node_by_class(self,
                          class_value: str,
                          do_get_page: bool = True) -> UIPage:
    """Clicks on node by its class attribute value.

    Args:
      class_value: Value of class attribute.
      do_get_page: Gets the latest page after clicking iff True.

    Returns:
      The transformed page.

    Raises:
      errors.UIError: Fail to get target node.
    """
    node = self.get_node_by_class(class_value)
    if node is None:
      raise errors.UIError(f'Fail to find the node with class={class_value}')

    return self.click(node, do_get_page)
