# sendevent without using sendevent - keystrokes on Android

### Tested against Windows 10 / Python 3.11 / Anaconda / Bluestacks 5

### pip install sendkeysonroids


## in action

[![YT](https://i.ytimg.com/vi/MifVqKNrxts/maxresdefault.jpg)](https://www.youtube.com/watch?v=MifVqKNrxts)
[https://www.youtube.com/watch?v=MifVqKNrxts]()


```py
from sendkeysonroids import (
    SendEventKeysOnRoids,
    std_key_mapping_dict,
    all_linux_key_events,
)
import shutil

# to see a list of all available keys
print(all_linux_key_events)


# this is the default key mapping
print(std_key_mapping_dict)

# define your key mapping
my_key_mapping_dict = {
    " ": "KEY_SPACE",
    "!": "KEY_LEFTSHIFT + KEY_1",
    "'": "KEY_APOSTROPHE",
    '"': "KEY_LEFTSHIFT + KEY_APOSTROPHE",
    "#": "KEY_LEFTSHIFT + KEY_3",
    "$": "KEY_LEFTSHIFT + KEY_4",
    "%": "KEY_LEFTSHIFT + KEY_5",
    "&": "KEY_LEFTSHIFT + KEY_7",
    "(": "KEY_LEFTSHIFT + KEY_9",
    ")": "KEY_LEFTSHIFT + KEY_0",
    "*": "KEY_LEFTSHIFT + KEY_8",
    "+": "KEY_KPPLUS",
    ",": "KEY_COMMA",
    "-": "KEY_MINUS",
    ".": "KEY_DOT",
    "/": "KEY_SLASH",
    "0": "KEY_0",
    "1": "KEY_1",
    "2": "KEY_2",
    "3": "KEY_3",
    "4": "KEY_4",
    "5": "KEY_5",
    "6": "KEY_6",
    "7": "KEY_7",
    "8": "KEY_8",
    "9": "KEY_9",
    ":": "KEY_LEFTSHIFT + KEY_SEMICOLON",
    ";": "KEY_SEMICOLON",
    "<": "KEY_LEFTSHIFT + KEY_COMMA",
    "=": "KEY_EQUAL",
    ">": "KEY_LEFTSHIFT + KEY_DOT",
    "?": "KEY_QUESTION",
    "@": "KEY_LEFTSHIFT + KEY_2",
    "A": "KEY_LEFTSHIFT + KEY_A",
    "B": "KEY_LEFTSHIFT + KEY_B",
    "C": "KEY_LEFTSHIFT + KEY_C",
    "D": "KEY_LEFTSHIFT + KEY_D",
    "E": "KEY_LEFTSHIFT + KEY_E",
    "F": "KEY_LEFTSHIFT + KEY_F",
    "G": "KEY_LEFTSHIFT + KEY_G",
    "H": "KEY_LEFTSHIFT + KEY_H",
    "I": "KEY_LEFTSHIFT + KEY_I",
    "J": "KEY_LEFTSHIFT + KEY_J",
    "K": "KEY_LEFTSHIFT + KEY_K",
    "L": "KEY_LEFTSHIFT + KEY_L",
    "M": "KEY_LEFTSHIFT + KEY_M",
    "N": "KEY_LEFTSHIFT + KEY_N",
    "O": "KEY_LEFTSHIFT + KEY_O",
    "P": "KEY_LEFTSHIFT + KEY_P",
    "Q": "KEY_LEFTSHIFT + KEY_Q",
    "R": "KEY_LEFTSHIFT + KEY_R",
    "S": "KEY_LEFTSHIFT + KEY_S",
    "T": "KEY_LEFTSHIFT + KEY_T",
    "U": "KEY_LEFTSHIFT + KEY_U",
    "V": "KEY_LEFTSHIFT + KEY_V",
    "W": "KEY_LEFTSHIFT + KEY_W",
    "X": "KEY_LEFTSHIFT + KEY_X",
    "Y": "KEY_LEFTSHIFT + KEY_Y",
    "Z": "KEY_LEFTSHIFT + KEY_Z",
    "[": "KEY_LEFTBRACE",
    "\n": "KEY_ENTER",
    "\t": "KEY_TAB",
    "]": "KEY_RIGHTBRACE",
    "^": "KEY_LEFTSHIFT + KEY_6",
    "_": "KEY_LEFTSHIFT + KEY_MINUS",
    "`": "KEY_GRAVE",
    "a": "KEY_A",
    "b": "KEY_B",
    "c": "KEY_C",
    "d": "KEY_D",
    "e": "KEY_E",
    "f": "KEY_F",
    "g": "KEY_G",
    "h": "KEY_H",
    "i": "KEY_I",
    "j": "KEY_J",
    "k": "KEY_K",
    "l": "KEY_L",
    "m": "KEY_M",
    "n": "KEY_N",
    "o": "KEY_O",
    "p": "KEY_P",
    "q": "KEY_Q",
    "r": "KEY_R",
    "s": "KEY_S",
    "t": "KEY_T",
    "u": "KEY_U",
    "v": "KEY_V",
    "w": "KEY_W",
    "x": "KEY_X",
    "y": "KEY_Y",
    "z": "KEY_Z",
    "{": "KEY_LEFTSHIFT + KEY_LEFTBRACE",
    "}": "KEY_LEFTSHIFT + KEY_RIGHTBRACE",
    "|": "KEY_LEFTSHIFT + KEY_BACKSLASH",
    "~": "KEY_LEFTSHIFT + KEY_GRAVE",
    "ç": "KEY_LEFTALT + KEY_C",
    "Ç": "KEY_LEFTALT + KEY_LEFTSHIFT + KEY_C",
    "ß": "KEY_LEFTALT + KEY_S",
    "ẞ": "KEY_LEFTSHIFT + KEY_LEFTALT + KEY_S",
    "\u0555": "KEY_LEFTCTRL + KEY_A", # use some unicode symbols that you never use, and bind them to a key combination (select all in this case)
    "\u0556": "KEY_LEFTCTRL + KEY_C", # Combinations need to be separated by ' + '
    "\u0557": "KEY_LEFTCTRL + KEY_V",
}
adb_path = shutil.which("adb")
device_serial = "127.0.0.1:5645"  # use None when running directly on Android -> https://github.com/hansalemaos/termuxfree
input_device = "/dev/input/event3"  # use None when running directly on Android
android_automation = SendEventKeysOnRoids(
    adb_path=adb_path,
    device_serial=device_serial,
    input_device=input_device,
    su_exe="su",
    blocksize=720,  # block size when using the dd command, this controls the execution speed of echo_input_text_dd/printf_input_text_dd
    prefered_execution="exec", # faster than eval
    chunk_size=1024, # chunk size to create the file for dd 
    key_mapping_dict=my_key_mapping_dict,
)
# adb_shell = UniversalADBExecutor(adb_path, device_serial)
my_text = "this is a test ÇßßaçÇqßßßßß2ß\u0555\u0556\u0557\u0557"
echo_input_text = android_automation.echo_input_text(text=my_text)
printf_input_text = android_automation.printf_input_text(text=my_text)
echo_input_text_dd = android_automation.echo_input_text_dd(text=my_text)
printf_input_text_dd = android_automation.printf_input_text_dd(text=my_text)
echo_input_keypress = android_automation.echo_input_keypress(key="A", duration=1)
printf_input_keypress = android_automation.printf_input_keypress(key="B", duration=1)

# commands can be executed multiple times
echo_input_text()
printf_input_text()
echo_input_text_dd()
printf_input_text_dd()
echo_input_keypress()
printf_input_keypress()
```

```py
    class SendEventKeysOnRoids(builtins.object)
     |  SendEventKeysOnRoids(adb_path=None, device_serial=None, input_device='/dev/input/event3', su_exe='su', blocksize=72, prefered_execution: Literal['exec', 'eval'] = 'exec', chunk_size=1024, key_mapping_dict=None) -> None
     |
     |  A class to manage and send key events to an Android device. It uses ADB, but also runs directly on the device (rooted and Python installed) -> https://github.com/hansalemaos/termuxfree
     |
     |  This class prepares binary data for key events, converts them into different formats, and executes
     |  corresponding commands on Android devices.
     |
     |  Methods defined here:
     |
     |  __init__(self, adb_path=None, device_serial=None, input_device='/dev/input/event3', su_exe='su', blocksize=72, prefered_execution: Literal['exec', 'eval'] = 'exec', chunk_size=1024, key_mapping_dict=None) -> None
     |      Initializes the SendEventKeysOnRoids class with specified parameters.
     |
     |      Args:
     |          adb_path (str, optional): Path to the ADB executable. Defaults to None.
     |          device_serial (str, optional): Serial number of the target Android device. Defaults to None.
     |          input_device (str, optional): Path to the input device on the Android device. Defaults to "/dev/input/event3".
     |          su_exe (str, optional): Command to gain superuser privileges on the Android device. Defaults to "su". ALWAYS NEEDED!
     |          blocksize (int, optional): Block size for the `dd` command. Defaults to 72. This controls the speed, use steps of 72
     |          prefered_execution (str, optional): Preferred method of command execution ('exec' or 'eval'). Defaults to "exec".
     |          chunk_size (int, optional): Chunk size for splitting data into base64 blocks. Defaults to 1024.
     |          key_mapping_dict (dict, optional): Dictionary mapping keys to Linux key event codes. Defaults to None.
     |
     |      Attributes:
     |          adb_path (str): Path to the ADB executable.
     |          device_serial (str): Serial number of the target Android device.
     |          input_device (str): Path to the input device on the Android device.
     |          su_exe (str): Command to gain superuser privileges on the Android device.
     |          blocksize (int): Block size for the `dd` command.
     |          prefered_execution (str): Preferred method of command execution.
     |          chunk_size (int): Chunk size for splitting data into base64 blocks.
     |          key_mapping_dict (dict): Dictionary mapping keys to Linux key event codes.
     |          all_linux_key_events_data (dict): Prepared binary data for all Linux key events.
     |          adb_shell (UniversalADBExecutor): ADB shell executor instance.
     |
     |  echo_input_keypress(self, key, duration=1, input_device=None)
     |      Generates a command to send a key press event to the specified input device using echo.
     |
     |      Args:
     |          key (str): The key to press.
     |          duration (int, optional): Duration to hold the key press. Defaults to 1 second.
     |          input_device (str, optional): Path to the input device on the Android device. Defaults to the class's input_device.
     |
     |      Returns:
     |          CodeExec: An instance of CodeExec class to execute the generated command.
     |
     |  echo_input_text(self, text, input_device=None)
     |      Generates a command to send text input to the specified input device using echo.
     |
     |      Args:
     |          text (str): The text to send as input.
     |          input_device (str, optional): Path to the input device on the Android device. Defaults to the class's input_device.
     |
     |      Returns:
     |          CodeExec: An instance of CodeExec class to execute the generated command.
     |
     |  echo_input_text_dd(self, text, output_path='/sdcard/echo_input_text_dd.bin', blocksize=None, sleep_after_each_execution=0, exec_or_eval=None, input_device=None)
     |      Generates a command to send text input as binary data using echo and dd commands.
     |
     |      Args:
     |          text (str): The text to send as input.
     |          output_path (str, optional): Path to store the generated binary data on the device. Defaults to "/sdcard/echo_input_text_dd.bin".
     |          blocksize (int, optional): Block size for the `dd` command. Defaults to the class's blocksize, this controls the speed, use steps of 72
     |          sleep_after_each_execution (int, optional): Sleep duration between each command execution. Defaults to 0.
     |          exec_or_eval (str, optional): Preferred method of command execution ('exec' or 'eval'). Defaults to the class's prefered_execution.
     |          input_device (str, optional): Path to the input device on the Android device. Defaults to the class's input_device.
     |
     |      Returns:
     |          CodeExec: An instance of CodeExec class to execute the generated command.
     |
     |  printf_input_keypress(self, key, duration=1, input_device=None)
     |      Generates a command to send a key press event to the specified input device using printf.
     |
     |      Args:
     |          key (str): The key to press.
     |          duration (int, optional): Duration to hold the key press. Defaults to 1 second.
     |          input_device (str, optional): Path to the input device on the Android device. Defaults to the class's input_device.
     |
     |      Returns:
     |          CodeExec: An instance of CodeExec class to execute the generated command.
     |
     |  printf_input_text(self, text, input_device=None)
     |      Generates a command to send text input to the specified input device using printf.
     |
     |      Args:
     |          text (str): The text to send as input.
     |          input_device (str, optional): Path to the input device on the Android device. Defaults to the class's input_device.
     |
     |      Returns:
     |          CodeExec: An instance of CodeExec class to execute the generated command.
     |
     |  printf_input_text_dd(self, text, output_path='/sdcard/printf_input_text_dd.bin', blocksize=None, sleep_after_each_execution=0, exec_or_eval=None, input_device=None)
     |      Generates a command to send text input as binary data using printf and dd commands.
     |
     |      Args:
     |          text (str): The text to send as input.
     |          output_path (str, optional): Path to store the generated binary data on the device. Defaults to "/sdcard/printf_input_text_dd.bin".
     |          blocksize (int, optional): Block size for the `dd` command. Defaults to the class's blocksize.
     |          sleep_after_each_execution (int, optional): Sleep duration between each command execution. Defaults to 0.
     |          exec_or_eval (str, optional): Preferred method of command execution ('exec' or 'eval'). Defaults to the class's prefered_execution.
     |          input_device (str, optional): Path to the input device on the Android device. Defaults to the class's input_device.
     |
     |      Returns:
     |          CodeExec: An instance of CodeExec class to execute the generated command.
     |

```