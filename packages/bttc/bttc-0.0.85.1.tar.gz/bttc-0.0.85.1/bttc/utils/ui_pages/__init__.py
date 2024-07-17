"""UI related operations/functions."""
from __future__ import annotations
import dataclasses
import logging
import os
import shlex
from typing import TypeAlias

from mobly.controllers import android_device
from xml.dom import minidom

from bttc.utils.ui_pages import errors
from bttc.utils.ui_pages import ui_node


AndroidDevice: TypeAlias = android_device.AndroidDevice


# Dataclass for return of UI parsing result.
@dataclasses.dataclass
class ParsedUI:
  """Dataclass for return of UI parsing result."""

  ui_xml: minidom.Document
  clickable_nodes: list[ui_node.UINode]
  enabled_nodes: list[ui_node.UINode]
  all_nodes: list[ui_node.UINode]

  @classmethod
  def from_ui_xml(cls, ui_xml: minidom.Document) -> ParsedUI:
    """Parsing input XML object to form target dataclass."""
    clickable_nodes = []
    enabled_nodes = []
    all_nodes = []
    nodes = [ui_node.UINode(node) for node in ui_xml.documentElement.childNodes]

    next_node = None
    prev_node = None
    while nodes:
      try:
        next_node = nodes.pop(0)
        if prev_node:
          prev_node.next_ui_node = next_node

        prev_node = next_node
        rid = next_node.resource_id.strip()
        clz = next_node.clz.strip()
      except AttributeError:
        logging.warning(
            'Ignoring node without resource id nor class:\n%s\n',
            next_node.node.toxml() if next_node else '?',
        )
        continue

      if rid or clz:
        if next_node.clickable:
          clickable_nodes.append(next_node)
        if next_node.enabled:
          enabled_nodes.append(next_node)

      all_nodes.append(next_node)
      for child_node in next_node.child_nodes:
        nodes.append(child_node)

    return ParsedUI(
        ui_xml, clickable_nodes, enabled_nodes, all_nodes)

  @classmethod
  def from_ui_xml_str(cls, ui_xml_str: str) -> ParsedUI:
    """Parsing input XML string to form target dataclass."""
    return cls.from_ui_xml(minidom.parseString(ui_xml_str))


def get_display_size(device: AndroidDevice) -> tuple[int, int]:
  """Gets the display size of the device.

  Returns:
    tuple(width, height) of the display size.

  Raises:
    errors.ContextError: Obtained unexpected output of
      display size from adb.
  """
  # e.g.: Physical size: 384x384
  output = device.adb.shell(shlex.split('wm size')).decode()
  size_items = output.rsplit(' ', 1)[-1].split('x')
  if len(size_items) == 2:
    return (int(size_items[0]), int(size_items[1]))

  raise errors.UIError(f'Illegal output of display size: {output}')


def get_ui_xml(
    device: AndroidDevice, xml_out_dir: str | None = None,
    dump_xml_retry_num: int = 5) -> minidom.Document:
  """Gets current activity xml object."""
  # Clean exist dump xml file in host if any to avoid
  # parsing the previous dumped xml file.
  dump_xml_name = 'window_dump.xml'
  xml_out_dir = xml_out_dir if xml_out_dir else device.log_path
  xml_path = os.path.join(xml_out_dir, dump_xml_name)
  if os.path.isfile(xml_path):
    os.remove(xml_path)

  ui_xml_content = device.ui.dump() or ''
  if not ui_xml_content:
    raise Exception('Failed to get UI xml content!')

  with open(xml_path, 'w') as fw:
    device.log.debug(
        'Dumped UI content by Snippet UiAutomator...(size=%s)',
        len(ui_xml_content))
    lines = [line.strip() for line in ui_xml_content.split('\n')]
    fw.write(''.join(lines))

  return minidom.parse(xml_path)


def parse_ui(
    device: AndroidDevice, xml_path: str | None = None) -> ParsedUI:
  """Parses the current UI page.

  Args:
    xml_path: Target XML file path. If this argument is given, this method
      will parse this XML file instead of dumping XML file through adb.

  Returns:
    Parsed tuple as [
        <UI XML object>,
        <List of clickable nodes>,
        <List of enabled nodes>,
    ]

  """
  if xml_path and os.path.isfile(xml_path):
    ui_xml = minidom.parse(xml_path)
  else:
    ui_xml = get_ui_xml(device)

  return ParsedUI.from_ui_xml(ui_xml)
