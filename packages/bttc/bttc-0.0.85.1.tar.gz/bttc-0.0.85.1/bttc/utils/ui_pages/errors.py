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

"""Module for errors thrown from ui_pages."""

from typing import List, Optional
from xml.dom import minidom
from bttc.utils.ui_pages import ui_node


class Error(Exception):
  pass


class UIError(Error):
  """UI page related error."""
  pass


class UnknownPageError(Error):
  """UI page error for unknown XML content.

  Attributes:
    ui_xml: Parsed XML object.
    clickable_nodes: List of UINode with attribute `clickable="true"`
    enabled_nodes: List of UINode with attribute `enabled="true"`
    all_nodes: List of all UINode
  """

  def __init__(self,
               ui_xml: minidom.Document,
               clickable_nodes: Optional[List[ui_node.UINode]] = None,
               enabled_nodes: Optional[List[ui_node.UINode]] = None,
               all_nodes: Optional[List[ui_node.UINode]] = None):
    xml_content = ui_xml if isinstance(ui_xml, str) else ui_xml.toxml()
    new_msg = f'Unknown ui_xml:\n{xml_content}\n'
    self.ui_xml = ui_xml
    self.enabled_nodes = enabled_nodes
    self.clickable_nodes = clickable_nodes
    self.all_nodes = all_nodes
    super().__init__(new_msg)
