from __future__ import annotations
import re
from ast import literal_eval
from datetime import datetime
import time
from adbshellexecuter import UniversalADBExecutor
from mymulti_key_dict import MultiKeyDict
from functools import cache

date_format = "%m-%d %H:%M:%S.%f"
this_year = datetime.now().year


class Trie:
    def __init__(self):
        self.data = MultiKeyDict({})
        self.compiled_regex = ""
        self._oldhash = 0
        self._isbytes = False

    def _addbytes(self, word):
        ref = self.data
        for char in range(len(word)):
            ref[word[char : char + 1]] = (
                word[char : char + 1] in ref and ref[word[char : char + 1]] or {}
            )
            ref = ref[word[char : char + 1]]
        ref[b""] = 1

    def _add(self, word: str):
        if self._isbytes:
            self._addbytes(word)
        else:
            word2 = list(word)
            word2.append("")
            self.data[word2] = 1

    @cache
    def _quote(self, char):
        return re.escape(char)

    def _pattern(self, pdata):
        data = pdata
        if not self._isbytes:
            if "" in data and len(data) == 1:
                return None
        else:
            if b"" in data and len(data) == 1:
                return None
        alt = []
        cc = []
        q = 0
        for char in sorted(data):
            if isinstance(data[char], dict):
                qu = self._quote(char)
                try:
                    recurse = self._pattern(data[char])
                    alt.append(qu + recurse)
                except Exception:
                    cc.append(qu)
            else:
                q = 1
        cconly = not len(alt) > 0
        if len(cc) > 0:
            if len(cc) == 1:
                alt.append(cc[0])
            else:
                if not self._isbytes:
                    alt.append("[" + "".join(cc) + "]")
                else:
                    alt.append(b"[" + b"".join(cc) + b"]")
        if len(alt) == 1:
            result = alt[0]
        else:
            if not self._isbytes:
                result = "(?:" + "|".join(alt) + ")"
            else:
                result = b"(?:" + b"|".join(alt) + b")"
        if q:
            if cconly:
                if not self._isbytes:
                    result += "?"
                else:
                    result += b"?"
            else:
                if not self._isbytes:
                    result = f"(?:{result})?"
                else:
                    result = b"(?:" + result + b")?"
        return result

    def _get_pattern(self):
        return self._pattern(self.data)

    def compile(
        self,
        add_before="",
        add_after="",
        boundary_right: bool = False,
        boundary_left: bool = False,
        capture: bool = False,
        match_whole_line: bool = False,
        flags: int = re.IGNORECASE,
    ):
        if not self._isbytes:
            anfang = ""
            ende = ""
            if match_whole_line is True:
                anfang += r"^\s*"
            if boundary_right is True:
                ende += r"\b"
            if capture is True:
                anfang += "("
            if boundary_left is True:
                anfang += r"\b"
            if capture is True:
                ende += ")"
            if match_whole_line is True:
                ende += r"\s*$"
        else:
            anfang = b""
            ende = b""
            if match_whole_line is True:
                anfang += rb"^\s*"
            if boundary_right is True:
                ende += rb"\b"
            if capture is True:
                anfang += b"("
            if boundary_left is True:
                anfang += rb"\b"
            if capture is True:
                ende += b")"
            if match_whole_line is True:
                ende += rb"\s*$"
            if not isinstance(add_before, bytes):
                add_before = add_before.encode("utf-8")
            if not isinstance(add_after, bytes):
                add_after = add_after.encode("utf-8")
        if (
            newhash := hash(
                f"""{add_before}{anfang}{self.data.to_dict()}{ende}{add_after}{flags}"""
            )
        ) == self._oldhash:
            return self
        else:
            self.compiled_regex = re.compile(
                add_before + anfang + self._get_pattern() + ende + add_after, flags
            )
            self._oldhash = newhash
        return self

    def regex_from_words(
        self,
        words: list | tuple,
    ):
        if not isinstance(words[0], str):
            self._isbytes = True
            if isinstance(self.compiled_regex, str):
                self.compiled_regex = b""
        for word in words:
            self._add(word)
        return self


def generate_trie_regex(all_categories_eventparser):
    all_categories_eventparser_as_unicode = {
        k: k.decode() for k in all_categories_eventparser
    }
    all_categories_eventparser_list = list(
        all_categories_eventparser_as_unicode.values()
    )
    return (
        all_categories_eventparser_as_unicode,
        all_categories_eventparser_list,
        (
            Trie()
            .regex_from_words(all_categories_eventparser)
            .compile(
                add_before=rb"(?:\]?[\[;]\s+)",
                add_after=rb"(?::\s+)",
                boundary_right=True,
                boundary_left=True,
                capture=True,
                match_whole_line=False,
                flags=0,
            )
        ).compiled_regex,
    )


def parse_timestamp(date_str):
    return float(
        datetime.strptime(date_str.decode(), date_format)
        .replace(year=this_year)
        .timestamp()
    )


@cache
def literal_eval_cached(value):
    try:
        return literal_eval(value)
    except Exception:
        return value.decode("utf-8", "backslashreplace")


def convert_function(key, value):
    if (
        key == "EventType"
        or key == "PackageName"
        or key == "Source"
        or key == "ClassName"
        or key == "Text"
        or key == "ContentDescription"
        or key == "ParcelableData"
    ):
        return value.decode("utf-8", "backslashreplace")
    if value == b"false":
        return False
    if value == b"true":
        return True
    if key == "TimeStamp":
        return parse_timestamp(value)
    if key == "recordCount":
        value = value.strip()
    return literal_eval_cached(value)


class UiautomatorEventParser(UniversalADBExecutor):
    def __init__(
        self,
        adb_path=None,
        device_serial=None,
        su_exe="su",
        timeout=30,
        kill_uiautomator_cmd=f"su -c 'pkill uiautomator'",
        kill_uiautomator_and_process_cmd=f"su -c 'pkill uiautomator'\nexit\n",
        print_exceptions=True,
        all_categories_eventparser=(
            b"AccessibilityDataSensitive",
            b"AccessibilityFocused",
            b"AccessibilityTool",
            b"Action",
            b"Active",
            b"AddedCount",
            b"BeforeText",
            b"BooleanProperties",
            b"Checked",
            b"ClassName",
            b"ConnectionId",
            b"ContentChangeTypes",
            b"ContentDescription",
            b"ContentInvalid",
            b"CurrentItemIndex",
            b"Empty",
            b"Enabled",
            b"EventTime",
            b"EventType",
            b"Focused",
            b"FromIndex",
            b"FullScreen",
            b"ItemCount",
            b"Loggable",
            b"MaxScrollX",
            b"MaxScrollY",
            b"MovementGranularity",
            b"PackageName",
            b"ParcelableData",
            b"Password",
            b"Records",
            b"RemovedCount",
            b"ScrollDeltaX",
            b"ScrollDeltaY",
            b"ScrollX",
            b"ScrollY",
            b"Scrollable",
            b"Sealed",
            b"Source",
            b"SourceDisplayId",
            b"SourceNodeId",
            b"SourceWindowId",
            b"SpeechStateChangeTypes",
            b"Text",
            b"ToIndex",
            b"WindowChangeTypes",
            b"WindowChanges",
            b"WindowId",
            b"TimeStamp",
            b"recordCount",
        ),
        kwargs_for_UniversalADBExecutor=None,
        subproc_kwargs=None,
    ):
        r"""
        Initializes the UiautomatorEventParser with device details and subprocess configuration.

        Args:
            adb_path (str, optional): Path to the adb executable.
            device_serial (str, optional): Serial number of the Android device.
            su_exe (str, optional): Superuser command for privileged actions.
            timeout (int, optional): Timeout for the adb subprocess in seconds.
            kill_uiautomator_cmd (str, optional): Command to kill the uiautomator process.
            kill_uiautomator_and_process_cmd (str, optional): Command to kill uiautomator and exit.
            print_exceptions (bool, optional): Whether to print exceptions to the console.
            all_categories_eventparser (tuple, optional): Tuple of event categories to parse. Change that only if Androids changes the event categories.
            kwargs_for_UniversalADBExecutor (dict, optional): Additional kwargs for the UniversalADBExecutor.
            subproc_kwargs (dict, optional): Additional kwargs for the subprocess configuration.

        """
        if not kwargs_for_UniversalADBExecutor:
            kwargs_for_UniversalADBExecutor = {}
        if not subproc_kwargs:
            self.subproc_kwargs = {}
        else:
            self.subproc_kwargs = subproc_kwargs
        super().__init__(
            adb_path=adb_path,
            device_serial=device_serial,
            **kwargs_for_UniversalADBExecutor,
        )

        (
            self.all_categories_eventparser_as_unicode,
            self.all_categories_eventparser_list,
            self.compiled_regex_categories,
        ) = generate_trie_regex(all_categories_eventparser)
        self.print_exceptions = print_exceptions
        self.su_exe = su_exe
        self.timeout = timeout
        self.kill_uiautomator_cmd = kill_uiautomator_cmd
        self.kill_uiautomator_and_process_cmd = kill_uiautomator_and_process_cmd

    def start_uiautomator_parsing(
        self,
        func,
        timeout=None,
        kill_uiautomator_cmd=None,
        print_exceptions=None,
        kill_uiautomator_and_process_cmd=None,
        subproc_kwargs=None,
    ):
        r"""
        This method controls the subprocess to collect UI Automator events and passes each event to a user-defined
        function for processing.

        Args:
            func (callable): A function to call with parsed event data.
            timeout (int, optional): Timeout for event parsing; defaults to the instance's timeout.
            kill_uiautomator_cmd (str, optional): Command to terminate the UI Automator process; defaults to the instance's command.
            print_exceptions (bool, optional): Flag to print exceptions during execution; defaults to the instance's setting.
            kill_uiautomator_and_process_cmd (str, optional): Command to kill the UI Automator process and clean up; defaults to the instance's command.
            subproc_kwargs (dict, optional): Additional kwargs for subprocess execution.

        Returns:
            dict: A dictionary containing the parsed lines from the UI Automator events.

        """
        subproc_kwargs = subproc_kwargs or self.subproc_kwargs
        kill_uiautomator_and_process_cmd = (
            kill_uiautomator_and_process_cmd or self.kill_uiautomator_and_process_cmd
        )
        timeout = timeout or self.timeout
        kill_uiautomator_cmd = kill_uiautomator_cmd or self.kill_uiautomator_cmd
        if print_exceptions is None:
            print_exceptions = self.print_exceptions

        nonblocking_subprocess = self.create_non_blocking_proc(
            debug=False,
            ignore_exceptions=True,
            **{**subproc_kwargs, "bufsize": 0},
        )
        nonblocking_subprocess.print_stdout = False
        nonblocking_subprocess.print_stderr = False
        nonblocking_subprocess.stop_thread2 = True
        nonblocking_subprocess.stdinwrite(
            f"{kill_uiautomator_cmd}\nuiautomator events\n"
        )
        parsed_lines_so_far = {}
        current_line = 0
        cachedict = {}
        parsed_lines_so_far[current_line] = {}
        timeout_final = timeout + time.time()
        continue_execution = True
        while time.time() <= timeout_final:
            try:
                while nonblocking_subprocess.stdout_results:
                    if time.time() > timeout_final:
                        break
                    try:
                        current_line_as_bytes = (
                            nonblocking_subprocess.stdout_results.pop()
                        )
                        current_line_bytes_split = self.compiled_regex_categories.split(
                            b"; TimeStamp: "
                            + current_line_as_bytes[:18]
                            + b"; "
                            + current_line_as_bytes[19:]
                        )[1:]
                        parsed_lines_so_far[current_line] = {}
                        len_of_current_line_bytes_split = len(current_line_bytes_split)
                        for current_index_of_splitline in range(
                            len_of_current_line_bytes_split
                        ):
                            if current_index_of_splitline % 2 == 0:
                                if (
                                    len_of_current_line_bytes_split
                                    > current_index_of_splitline + 1
                                ):
                                    tmpfi = current_line_bytes_split[
                                        current_index_of_splitline + 1
                                    ].strip(b"[] ")
                                    parsed_lines_so_far[current_line][
                                        self.all_categories_eventparser_as_unicode[
                                            current_line_bytes_split[
                                                current_index_of_splitline
                                            ]
                                        ]
                                    ] = cachedict.setdefault(
                                        tmpfi,
                                        convert_function(
                                            self.all_categories_eventparser_as_unicode[
                                                current_line_bytes_split[
                                                    current_index_of_splitline
                                                ]
                                            ],
                                            tmpfi,
                                        ),
                                    )
                        for missing_categories in self.all_categories_eventparser_list:
                            if (
                                missing_categories
                                not in parsed_lines_so_far[current_line]
                            ):
                                parsed_lines_so_far[current_line][
                                    missing_categories
                                ] = ""
                        continue_execution = func(**locals())
                        if not continue_execution:
                            return parsed_lines_so_far
                        current_line += 1
                    except Exception as e:
                        if print_exceptions:
                            print(e)
                    except KeyboardInterrupt:
                        return parsed_lines_so_far
            except Exception as e:
                if print_exceptions:
                    print(e)
            except KeyboardInterrupt:
                return parsed_lines_so_far
        try:
            nonblocking_subprocess.stdinwrite(kill_uiautomator_and_process_cmd)
            nonblocking_subprocess.kill()
        except Exception as e:
            if print_exceptions:
                print(e)
        return parsed_lines_so_far
