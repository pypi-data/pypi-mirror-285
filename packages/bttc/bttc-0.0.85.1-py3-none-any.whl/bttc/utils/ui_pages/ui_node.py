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
"""UI Node is used to compose the UI pages."""
from __future__ import annotations

import collections
import re
from typing import Any, Dict, List, Optional
from xml.dom import minidom


def find_point_in_bounds(bounds_string):
  """Finds a point that resides within the given bounds.

  Args:
    bounds_string: string, In the format of the UI element bound.

  Returns:
    A tuple of integers, representing X and Y coordinates of a point within
    the given boundary.
  """
  return parse_bound(bounds_string).calculate_middle_point()


def parse_bound(bounds_string):
  """Parse UI bound string.

  Args:
    bounds_string: string, In the format of the UI element bound. e.g
      '[0,0][1080,2160]'

  Returns:
    Bounds, The bound of UI element.
  """
  bounds_pattern = re.compile(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]')
  points = bounds_pattern.match(bounds_string).groups()
  points = list(map(int, points))
  return Bounds(Point(*points[:2]), Point(*points[-2:]))


class Point(collections.namedtuple('Point', ['x', 'y'])):

  def __repr__(self):
    return '{x},{y}'.format(x=self.x, y=self.y)


class Bounds(collections.namedtuple('Bounds', ['start', 'end'])):

  def __repr__(self):
    return '[{start}][{end}]'.format(start=str(self.start), end=str(self.end))

  def calculate_middle_point(self):
    return Point((self.start.x + self.end.x) // 2,
                 (self.start.y + self.end.y) // 2)


class NodeError(Exception):
  """UI node related error."""

  def __init__(self, node, msg):
    new_msg = f'{node}: {msg}'
    super().__init__(new_msg)


class UINode:
  """UI Node to hold element of UI page.

  If both x and y axis are given in constructor, this node will use (x, y)
  as coordinates. Otherwise, the attribute `bounds` of node will be used to
  calculate the coordinates.

  Attributes:
    node: XML node element.
    x: x point of UI page.
    y: y point of UI page.
    next_ui_node: Next neighboring node.
    parent_ui_node: Parent UI node.
  """

  STR_FORMAT = "RID='{rid}'/CLASS='{clz}'/TEXT='{txt}'/CD='{ctx}'"
  PREFIX_SEARCH_IN = 'c:'

  def __init__(self, node: minidom.Element,
               x: Optional[int] = None, y: Optional[int] = None,
               parent_ui_node: UINode | None = None) -> None:
    self.node = node
    self.parent_ui_node = parent_ui_node
    self.next_ui_node: UINode | None = None
    if x and y:
      self.x = x
      self.y = y
    else:
      try:
        self.x, self.y = find_point_in_bounds(
            self.attributes['bounds'].value)
      except AttributeError as ex:
        attribute_value = self.attributes['bounds'].value
        raise NodeError(
            node,
            f'Unexpected attribute "bounds" as "{attribute_value}"!') from ex

  def __hash__(self) -> int:
    return id(self.node)

  @property
  def clz(self) -> str:
    """Returns the class of node."""
    return self.attributes['class'].value

  @property
  def text(self) -> str:
    """Gets text of node.

    Returns:
      The text of node.
    """
    return self.attributes['text'].value

  @property
  def content_desc(self) -> str:
    """Gets content description of node.

    Returns:
      The content description of node.
    """
    return self.attributes['content-desc'].value

  @property
  def resource_id(self) -> str:
    """Gets resource id of node.

    Returns:
      The resource id of node.
    """
    return self.attributes['resource-id'].value

  @property
  def attributes(self) -> Dict[str, Any]:
    """Gets attributes of node.

    Returns:
      The attributes of node.
    """
    if hasattr(self.node, 'attributes'):
      return collections.defaultdict(
          lambda: None,
          getattr(self.node, 'attributes'))
    else:
      return collections.defaultdict(lambda: None)

  @property
  def checked(self) -> bool:
    """Gets attribute `checked` of node.

    Returns:
      True iff checked="true".
    """
    checked_attr = self.attributes.get('checked')
    return checked_attr.value == 'true' if checked_attr else False

  @property
  def clickable(self) -> bool:
    """Gets attribute `clickable` of node.

    Returns:
      True if clickable="true".
    """
    clickable_attr = self.attributes.get('clickable')
    return clickable_attr.value == 'true' if clickable_attr else False

  @property
  def enabled(self) -> bool:
    """Gets attribute `enabled` of node.

    Returns:
      True if enabled="true".
    """
    enabled_attr = self.attributes.get('enabled')
    return enabled_attr.value == 'true' if enabled_attr else False

  @property
  def focused(self) -> bool:
    """Gets attribute `focused` of node.

    Returns:
      True iff focused="true".
    """
    focused_attr = self.attributes.get('focused')
    return focused_attr.value == 'true' if focused_attr else False

  @property
  def child_nodes(self) -> List[UINode]:
    """Gets child node(s) of current node.

    Returns:
      The child nodes of current node if any.
    """
    return [UINode(n, parent_ui_node=self) for n in self.node.childNodes]

  def match_attrs_by_kwargs(self, **kwargs) -> bool:
    """Matches given attribute key/value pair with current node.

    Args:
      **kwargs: Key/value pair as attribute key/value.
        e.g.: resource_id='abc'

    Returns:
      True iff the given attributes match current node.
    """
    if 'clz' in kwargs:
      kwargs['class'] = kwargs['clz']
      del kwargs['clz']

    return self.match_attrs(kwargs)

  def match_attrs(self, attrs: Dict[str, Any]) -> bool:
    """Matches given attributes with current node.

    This method is used to compare the given `attrs` with attributes of
    current node. Only the keys given in `attrs` will be compared. e.g.:
    ```
    # ui_node has attributes {'name': 'john', 'id': '1234'}
    >>> ui_node.match_attrs({'name': 'john'})
    True

    >>> ui_node.match_attrs({'name': 'ken'})
    False
    ```

    If you don't want exact match and want to check if an attribute value
    contain specific substring, you can leverage special prefix
    `PREFIX_SEARCH_IN` to tell this method to use `in` instead of `==` for
    comparison. e.g.:
    ```
    # ui_node has attributes {'name': 'john', 'id': '1234'}
    >>> ui_node.match_attrs({'name': ui_node.PREFIX_SEARCH_IN + 'oh'})
    True

    >>> ui_node.match_attrs({'name': 'oh'})
    False
    ```

    Args:
      attrs: Attributes to compare with.

    Returns:
      True iff the given attributes match current node.
    """
    for k, v in attrs.items():
      if k not in self.attributes:
        return False

      if v and v.startswith(self.PREFIX_SEARCH_IN):
        v = v[len(self.PREFIX_SEARCH_IN):]
        if not v or v not in self.attributes[k].value:
          return False
      elif v != self.attributes[k].value:
        return False

    return True

  def __str__(self) -> str:
    """The string representation of this object.

    Returns:
      The string representation including below information:
      - resource id
      - class
      - text
      - content description.
    """
    rid = self.resource_id.strip()
    clz = self.clz.strip()
    txt = self.text.strip()
    ctx = self.content_desc.strip()
    return f"RID='{rid}'/CLASS='{clz}'/TEXT='{txt}'/CD='{ctx}'"
