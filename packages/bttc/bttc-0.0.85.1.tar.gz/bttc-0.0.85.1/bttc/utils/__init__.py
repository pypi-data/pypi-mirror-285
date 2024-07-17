"""Miscellaneous utilities."""
import logging
import time


def wait_until(timeout_sec,
               condition_func,
               func_args,
               expected_value=None,
               expected_func=None,
               exception=None,
               interval_sec=0.5):
  """Waits until a function returns a expected value or timeout is reached.

  Example usage:
    ```
    def is_bluetooth_enabled(device) -> bool:
      do something and return something...

    # Waits and checks if Bluetooth is turned on.
    bt_test_utils.wait_until(
        timeout_sec=10,
        condition_func=is_bluetooth_enabled,
        func_args=[dut],
        expected_value=True,
        exception=signals.TestFailure('Failed to turn on Bluetooth.'),
        interval_sec=1)
    ```

  Args:
    timeout_sec: float, max waiting time in seconds.
    condition_func: function, when the condiction function returns the expected
        value, the waiting mechanism will be interrupted.
    func_args: tuple or list, the arguments for the condition function.
    expected_value: A expected value that the condition function returns.
    expected_func: A callable function to examine the returned value of
        `condition_func`. If it returns True value, it meas we meet expected
        value or state.
    exception: Exception, an exception will be raised when timed out if needed.
    interval_sec: float, interval time between calls of the condition function
        in seconds.

  Returns:
    True if the function returns the expected value else False.
  """
  start_time = time.time()
  end_time = start_time + timeout_sec
  while time.time() < end_time:
    returned_value = condition_func(*func_args)
    if expected_value is not None and expected_value == returned_value:
      return True
    if expected_func is not None and expected_func(returned_value):
      return True

    time.sleep(interval_sec)
  args_string = ', '.join(list(map(str, func_args)))
  logging.warning(
      'Timed out after %.1fs waiting for "%s(%s)" to be "%s".',
      timeout_sec, condition_func.__name__, args_string, expected_value)
  if exception:
    raise exception
  return False
