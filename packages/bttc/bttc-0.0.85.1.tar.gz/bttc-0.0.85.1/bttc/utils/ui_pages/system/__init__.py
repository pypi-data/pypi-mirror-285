"""Operations on system pages."""
import logging
import time

from bttc.utils.ui_pages import ui_core
from bttc.utils.ui_pages.system import constants


def set_do_not_disturb(dut, setting: bool = True):
  """Turns on/off "Do not disturb" (DnD) setting."""
  setting_text = 'On' if setting else 'Off'
  disturb_text = 'Do Not Disturb'
  uip = ui_core.UIPage.from_device(dut)
  for _ in range(3):
    logging.info('Openning setting page...')
    time.sleep(1)
    dut.adb.shell(constants.CMD_LAUNCH_UI_SOUND_SETTINGS)
    uip.refresh()
    if uip.get_node_by_content_desc(disturb_text):
      break

  if not uip.get_node_by_content_desc('Sound & vibration'):
    # Gets back to setting page `Sound & vibration`
    uip.back()

  current_dnd_setting = uip.get_node_by_text(
      disturb_text).next_ui_node.text

  if current_dnd_setting == setting_text:
    logging.info('Target setting is already "%s"', setting_text)
    return

  # Click on section `Do Not Disturb`
  uip.click_node_by_text(disturb_text, search_clickable=False)

  action_node_text = f'Turn {setting_text.lower()} now'
  uip.click_node_by_text(action_node_text)

  uip.back()
  current_dnd_setting = uip.get_node_by_text(
      disturb_text).next_ui_node.text

  assert current_dnd_setting == setting_text
