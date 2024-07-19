# Interacting with uiautomator events

### Tested against Windows 10 / Python 3.11 / Anaconda / BlueStacks 5

### pip install uiautomatoreventparser

```PY
from uiautomatoreventparser import UiautomatorEventParser
import shutil

adb_path = shutil.which("adb")
device_serial = "127.0.0.1:5645"  # use None when running directly on Android -> https://github.com/hansalemaos/termuxfree


adb_auto = UiautomatorEventParser(
    adb_path=adb_path,
    device_serial=device_serial,
    su_exe="su",
    timeout=30,
    kill_uiautomator_cmd=f"su -c 'pkill uiautomator'",
    kill_uiautomator_and_process_cmd=f"su -c 'pkill uiautomator'\nexit\n",
    print_exceptions=True,
    kwargs_for_UniversalADBExecutor=None,
)
adb_auto.non_shell_adb_commands_without_s_serial(
    [
        "connect",
        device_serial,
    ],
)


from sendkeysonroids import (
    SendEventKeysOnRoids,
    std_key_mapping_dict,
    all_linux_key_events,
)

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
    "\u0555": "KEY_LEFTSHIFT + KEY_TAB",  # use some unicode symbols that you never use, and bind them to a key combination (select all in this case)
}
input_device = "/dev/input/event3"
android_automation = SendEventKeysOnRoids(
    adb_path=adb_path,
    device_serial=device_serial,
    input_device=input_device,
    su_exe="su",
    blocksize=144,
    prefered_execution="exec",
    chunk_size=1024,
    key_mapping_dict=my_key_mapping_dict,
)

press_tab_key = android_automation.printf_input_text_dd(text="\t")
press_enter_key = android_automation.printf_input_text_dd(text="\n")


def function_after_each_result(**kwargs):
    # Available variables
    # dict_keys(
    #     [
    #         "self",
    #         "func",
    #         "timeout",
    #         "kill_uiautomator_cmd",
    #         "print_exceptions",
    #         "kill_uiautomator_and_process_cmd",
    #         "nonblocking_subprocess",
    #         "parsed_lines_so_far",
    #         "current_line",
    #         "cachedict",
    #         "timeout_final",
    #         "continue_execution",
    #         "current_line_as_bytes",
    #         "current_line_bytes_split",
    #         "len_of_current_line_bytes_split",
    #         "current_index_of_splitline",
    #         "tmpfi",
    #         "missing_categories",
    #     ]
    # )
    #print(kwargs.keys())
    parsed_lines_so_far = kwargs.get("parsed_lines_so_far")
    nonblocking_subprocess = kwargs.get("nonblocking_subprocess")
    current_line = kwargs.get("current_line")
    if "Termux" in parsed_lines_so_far[current_line]["Text"]:
        press_enter_key()
        print(parsed_lines_so_far[current_line]["Text"])
        nonblocking_subprocess.stdinwrite("su -c 'pkill uiautomator'\nexit\n")
        nonblocking_subprocess.kill()
        return False
    else:
        press_tab_key()
    return True


parsed_lines = adb_auto.start_uiautomator_parsing(
    func=function_after_each_result,
    timeout=None,
    kill_uiautomator_cmd=None,
    print_exceptions=None,
    kill_uiautomator_and_process_cmd=None,
)
```
