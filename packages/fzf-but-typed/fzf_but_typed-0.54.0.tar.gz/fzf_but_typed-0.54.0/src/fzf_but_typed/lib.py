from __future__ import annotations

from collections.abc import Iterable, Mapping, ItemsView
from dataclasses import dataclass, field, asdict
from enum import unique, StrEnum, auto as enum_auto, Enum, IntEnum
from pathlib import Path
from typing import NewType, TypeAlias, Protocol
from itertools import starmap
from functools import partial

import shutil
import itertools
import subprocess as sp

__all__ = [
   # Main Content
    'fzf',
    'fzf_iter',
    'fzf_pairs',
    'fzf_mapping',
    'FuzzyFinder',
    'FuzzyFinderBuilder',
    'FuzzyFinderOutput',
    'ExitStatusCode',

   # Search Options
    'SearchOptions',
    'SearchSchemeType',
    'SearchAlgorithm',
    'FieldIndexExpression',

   # Results Options
    'ResultsOptions',
    'SearchTiebreak',

   # Interface Options
    'InterfaceOptions',
    'Key',
    'Event',
    'ActionSimple',
    'ActionWithArgType',
    'ActionArgSeparator',
    'ActionWithArg',
    'Binding',

   # Layout Options
    'TmuxPosition',
    'TmuxSettings',
    'LayoutType',
    'BorderType',
    'Percent',
    'Sides',
    'LayoutInfoStyle',
    'LabelSide',
    'LabelPosition',
    'LayoutOptions',

   # Display Options
    'ColorName',
    'BaseColorScheme',
    'AnsiColor16',
    'AnsiColor256',
    'AnsiColorRgb',
    'AnsiColorDefault',
    'AnsiAttribute',
    'ColorMapping',
    'Color',
    'DisplayOptions',
    'HistoryOptions',

   # Preview Options
    'PreviewLabel',
    'PreviewWindowPosition',
    'PreviewWindowBorderType',
    'PreviewOptions',

   # Scripting Options
    'Port',
    'ScriptingOptions',

   # Directory Traversal Options
    'TraversalBehavior',
    'DirectoryTraversalOptions'
]


class SupportsStr(Protocol):

    def __str__(self) -> str:
        ...


@unique
class SearchSchemeType(StrEnum):
    DEFAULT = "default"
    PATH = "path"
    HISTORY = "history"


@unique
class SearchAlgorithm(StrEnum):
    V1 = 'v1'
    V2 = 'v2'


@dataclass(slots=True, kw_only=True, frozen=True)
class UnboundedRange:
    upper: int | None
    lower: int | None

    def __str__(self) -> str:
        upper_bound = '' if self.upper is None else self.upper
        lower_bound = '' if self.lower is None else self.lower
        return f"{lower_bound}..{upper_bound}"


FieldIndexExpression = int | UnboundedRange


@dataclass(slots=True, kw_only=True)
class SearchOptions:
    extended: bool = True   # --extended --no-extended
    exact: bool = False   # --exact
    case_sensitive: bool = False   # -i +i
    normalize_letters: bool = True   # --literal
    scheme: SearchSchemeType = SearchSchemeType.DEFAULT   # --scheme
    algorithm: SearchAlgorithm = SearchAlgorithm.V2   # --algo
    nth: list[FieldIndexExpression] | None = None   #--nth
    with_nth: list[FieldIndexExpression] | None = None   # --with-nth
    delimiter: str | None = None   # --delimiter
    disabled: bool = False   # --disabled

    def as_args(self) -> list[str]:
        args = []
        args.append("--extended" if self.extended else "--no-extended")
        args.append("--exact" if self.exact else "--no-exact")
        args.append("+i" if self.case_sensitive else "-i")
        args.append("--no-literal" if self.normalize_letters else "--literal")
        args.append(f"--scheme={self.scheme}")
        args.append(f"--algo={self.algorithm}")
        if self.nth is not None:
            args.append(f"--nth={','.join(str(e) for e in self.nth)}")
        if self.with_nth is not None:
            args.append(f"--with-nth={','.join(str(e) for e in self.with_nth)}")
        if self.delimiter is not None:
            args.append(f'--delimiter={self.delimiter}')
        if self.disabled:
            args.append('--disabled')
        return args


@unique
class SearchTiebreak(StrEnum):
    LENGTH = "length"
    CHUNK = "chunk"
    BEGIN = "begin"
    END = "end"
    INDEX = "index"


@dataclass(slots=True, kw_only=True)
class ResultsOptions:
    sort: bool = True   # +s --no-sort
    tail: int | None = None
    track: bool = False   # --track
    tac: bool = False   # --tac
    tiebreak: tuple[SearchTiebreak, ...] = (SearchTiebreak.LENGTH, SearchTiebreak.INDEX)

    def as_args(self) -> list[str]:
        args = [
            "+s" if self.sort else "--no-sort",
            "--track" if self.track else "--no-track",
            "--tac" if self.tac else "--no-tac",
            f"--tiebreak={','.join(self.tiebreak)}",
        ]
        if self.tail is not None:
            args.append(f"--tail={self.tail}")
        return args


@unique
class Key(StrEnum):
    # yapf: disable
    A = "a"; B = "b"; C = "c"; D = "d"
    E = "e"; F = "f"; G = "g"; H = "h"
    I = "i"; J = "j"; K = "k"; L = "l"
    M = "m"; N = "n"; O = "o"; P = "p"
    Q = "q"; R = "r"; S = "s"; T = "t"
    U = "u"; V = "v"; W = "w"; X = "x"
    Y = "y"; Z = "z"

    CTRL_A = "ctrl-a"; CTRL_B = "ctrl-b"; CTRL_C = "ctrl-c"
    CTRL_D = "ctrl-d"; CTRL_E = "ctrl-e"; CTRL_F = "ctrl-f"
    CTRL_G = "ctrl-g"; CTRL_H = "ctrl-h"; CTRL_I = "ctrl-i"
    CTRL_J = "ctrl-j"; CTRL_K = "ctrl-k"; CTRL_L = "ctrl-l"
    CTRL_M = "ctrl-m"; CTRL_N = "ctrl-n"; CTRL_O = "ctrl-o"
    CTRL_P = "ctrl-p"; CTRL_Q = "ctrl-q"; CTRL_R = "ctrl-r"
    CTRL_S = "ctrl-s"; CTRL_T = "ctrl-t"; CTRL_U = "ctrl-u"
    CTRL_V = "ctrl-v"; CTRL_W = "ctrl-w"; CTRL_X = "ctrl-x"
    CTRL_Y = "ctrl-y"; CTRL_Z = "ctrl-z"

    ALT_UPPER_A = "alt-A"; ALT_UPPER_B = "alt-B"; ALT_UPPER_C = "alt-C"
    ALT_UPPER_D = "alt-D"; ALT_UPPER_E = "alt-E"; ALT_UPPER_F = "alt-F"
    ALT_UPPER_G = "alt-G"; ALT_UPPER_H = "alt-H"; ALT_UPPER_I = "alt-I"
    ALT_UPPER_J = "alt-J"; ALT_UPPER_K = "alt-K"; ALT_UPPER_L = "alt-L"
    ALT_UPPER_M = "alt-M"; ALT_UPPER_N = "alt-N"; ALT_UPPER_O = "alt-O"
    ALT_UPPER_P = "alt-P"; ALT_UPPER_Q = "alt-Q"; ALT_UPPER_R = "alt-R"
    ALT_UPPER_S = "alt-S"; ALT_UPPER_T = "alt-T"; ALT_UPPER_U = "alt-U"
    ALT_UPPER_V = "alt-V"; ALT_UPPER_W = "alt-W"; ALT_UPPER_X = "alt-X"
    ALT_UPPER_Y = "alt-Y"; ALT_UPPER_Z = "alt-Z"

    ALT_LOWER_A = "alt-a"; ALT_LOWER_B = "alt-b"; ALT_LOWER_C = "alt-c"
    ALT_LOWER_D = "alt-d"; ALT_LOWER_E = "alt-e"; ALT_LOWER_F = "alt-f"
    ALT_LOWER_G = "alt-g"; ALT_LOWER_H = "alt-h"; ALT_LOWER_I = "alt-i"
    ALT_LOWER_J = "alt-j"; ALT_LOWER_K = "alt-k"; ALT_LOWER_L = "alt-l"
    ALT_LOWER_M = "alt-m"; ALT_LOWER_N = "alt-n"; ALT_LOWER_O = "alt-o"
    ALT_LOWER_P = "alt-p"; ALT_LOWER_Q = "alt-q"; ALT_LOWER_R = "alt-r"
    ALT_LOWER_S = "alt-s"; ALT_LOWER_T = "alt-t"; ALT_LOWER_U = "alt-u"
    ALT_LOWER_V = "alt-v"; ALT_LOWER_W = "alt-w"; ALT_LOWER_X = "alt-x"
    ALT_LOWER_Y = "alt-y"; ALT_LOWER_Z = "alt-z"

    CTRL_ALT_A = "ctrl-alt-a"; CTRL_ALT_B = "ctrl-alt-b"; CTRL_ALT_C = "ctrl-alt-c"
    CTRL_ALT_D = "ctrl-alt-d"; CTRL_ALT_E = "ctrl-alt-e"; CTRL_ALT_F = "ctrl-alt-f"
    CTRL_ALT_G = "ctrl-alt-g"; CTRL_ALT_H = "ctrl-alt-h"; CTRL_ALT_I = "ctrl-alt-i"
    CTRL_ALT_J = "ctrl-alt-j"; CTRL_ALT_K = "ctrl-alt-k"; CTRL_ALT_L = "ctrl-alt-l"
    CTRL_ALT_M = "ctrl-alt-m"; CTRL_ALT_N = "ctrl-alt-n"; CTRL_ALT_O = "ctrl-alt-o"
    CTRL_ALT_P = "ctrl-alt-p"; CTRL_ALT_Q = "ctrl-alt-q"; CTRL_ALT_R = "ctrl-alt-r"
    CTRL_ALT_S = "ctrl-alt-s"; CTRL_ALT_T = "ctrl-alt-t"; CTRL_ALT_U = "ctrl-alt-u"
    CTRL_ALT_V = "ctrl-alt-v"; CTRL_ALT_W = "ctrl-alt-w"; CTRL_ALT_X = "ctrl-alt-x"
    CTRL_ALT_Y = "ctrl-alt-y"; CTRL_ALT_Z = "ctrl-alt-z"

    CTRL_SPACE = "ctrl-space"
    CTRL_DELETE = "ctrl-delete"
    CTRL_BACKSLASH = "ctrl-\\"
    CTRL_CLOSED_BRACE = "ctrl-]"
    CTRL_CARET = "ctrl-^"
    CTRL_SLASH = "ctrl-/"

    F1 = "f1"; F2 = "f2"; F3 = "f3"; F4 = "f4"
    F5 = "f5"; F6 = "f6"; F7 = "f7"; F8 = "f8"
    F9 = "f9"; F10 = "f10"; F11 = "f11"; F12 = "f12"
    # yapf: enable

    ENTER = "enter"
    SPACE = "space"
    BSPACE = "bspace"
    ALT_UP = "alt-up"
    ALT_DOWN = "alt-down"
    ALT_LEFT = "alt-left"
    ALT_RIGHT = "alt-right"
    ALT_ENTER = "alt-enter"
    ALT_SPACE = "alt-space"
    ALT_BSPACE = "alt-bspace"
    TAB = "tab"
    BTAB = "btab"
    ESC = "esc"
    DEL = "del"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    HOME = "home"
    END = "end"
    INSERT = "insert"
    PGUP = "pgup"
    PGDN = "pgdn"
    SHIFT_UP = "shift-up"
    SHIFT_DOWN = "shift-down"
    SHIFT_LEFT = "shift-left"
    SHIFT_RIGHT = "shift-right"
    SHIFT_DELETE = "shift-delete"
    ALT_SHIFT_UP = "alt-shift-up"
    ALT_SHIFT_DOWN = "alt-shift-down"
    ALT_SHIFT_LEFT = "alt-shift-left"
    ALT_SHIFT_RIGHT = "alt-shift-right"
    LEFT_CLICK = "left-click"
    RIGHT_CLICK = "right-click"
    DOUBLE_CLICK = "double-click"
    SCROLL_UP = "scroll_up"
    SCROLL_DOWN = "scroll_down"
    PREVIEW_SCROLL_UP = "preview_scroll_up"
    PREVIEW_SCROLL_DOWN = "preview_scroll_down"
    SHIFT_LEFT_CLICK = "shift_left_click"
    SHIFT_RIGHT_CLICK = "shift_right_click"
    SHIFT_SCROLL_UP = "shift_scroll_up"
    SHIFT_SCROLL_DOWN = "shift_scroll_down"


@unique
class Event(StrEnum):
    START = "start"
    LOAD = "load"
    RESIZE = "resize"
    RESULT = "result"
    CHANGE = "change"
    FOCUS = "focus"
    ONE = "one"
    BACKWARD_EOF = "backward-eof"
    JUMP = "jump"
    JUMP_CANCEL = "jump-cancel"
    CLICK_HEADER = "click-header"


@unique
class ActionSimple(StrEnum):
    ABORT = "abort"
    ACCEPT = "accept"
    ACCEPT_NON_EMPTY = "accept-non-empty"
    BACKWARD_CHAR = "backward-char"
    BACKWARD_DELETE_CHAR = "backward-delete-char"
    BACKWARD_DELETE_CHAR_EOF = "backward-delete-char/eof"
    BACKWARD_KILL_WORD = "backward-kill-word"
    BACKWARD_WORD = "backward-word"
    BEGINNING_OF_LINE = "beginning-of-line"
    CANCEL = "cancel"
    CHANGE_MULTI = "change-multi"
    CLEAR_QUERY = "clear-query"
    CLEAR_SCREEN = "clear-screen"
    CLEAR_SELECTION = "clear-selection"
    CLOSE = "close"
    DELETE_CHAR = "delete-char"
    DELETE_CHAR_EOF = "delete-char/eof"
    DESELECT = "deselect"
    DESELECT_ALL = "deselect-all"
    DISABLE_SEARCH = "disable-search"
    DOWN = "down"
    ENABLE_SEARCH = "enable-search"
    END_OF_LINE = "end-of-line"
    FIRST = "first"
    FORWARD_CHAR = "forward-char"
    FORWARD_WORD = "forward-word"
    HALF_PAGE_DOWN = "half-page-down"
    HALF_PAGE_UP = "half-page-up"
    HIDE_PREVIEW = "hide-preview"
    OFFSET_DOWN = "offset-down"
    OFFSET_UP = "offset-up"
    OFFSET_MIDDLE = "offset-middle"
    IGNORE = "ignore"
    JUMP = "jump"
    JUMP_ACCEPT = "jump-accept"
    KILL_LINE = "kill-line"
    KILL_WORD = "kill-word"
    LAST = "last"
    NEXT_HISTORY = "next-history"
    NEXT_SELECTED = "next-selected"
    PAGE_DOWN = "page-down"
    PAGE_UP = "page-up"
    PREVIEW_BOTTOM = "preview-bottom"
    PREVIEW_DOWN = "preview-down"
    PREVIEW_HALF_PAGE_DOWN = "preview-half-page-down"
    PREVIEW_HALF_PAGE_UP = "preview-half-page-up"
    PREVIEW_PAGE_DOWN = "preview-page-down"
    PREVIEW_PAGE_UP = "preview-page-up"
    PREVIEW_TOP = "preview-top"
    PREVIEW_UP = "preview-up"
    PREV_HISTORY = "prev-history"
    PREV_SELECTED = "prev-selected"
    PRINT_QUERY = "print-query"
    PUT = "put"
    REFRESH_PREVIEW = "refresh-preview"
    REPLACE_QUERY = "replace-query"
    SELECT = "select"
    SELECT_ALL = "select-all"
    SHOW_PREVIEW = "show-preview"
    TOGGLE = "toggle"
    TOGGLE_ALL = "toggle-all"
    TOGGLE_DOWN = "toggle+down"
    TOGGLE_IN = "toggle-in"
    TOGGLE_OUT = "toggle-out"
    TOGGLE_PREVIEW = "toggle-preview"
    TOGGLE_PREVIEW_WRAP = "toggle-preview-wrap"
    TOGGLE_SEARCH = "toggle-search"
    TOGGLE_SORT = "toggle-sort"
    TOGGLE_TRACK = "toggle-track"
    TOGGLE_TRACK = "toggle-track-current"
    TOGGLE_WRAP = "toggle-wrap"
    TOGGLE_UP = "toggle+up"
    TRACK = "track-current"
    TRACK_CURRENT = "track-current"
    UNIX_LINE_DISCARD = "unix-line-discard"
    UNIX_WORD_RUBOUT = "unix-word-rubout"
    UNTRACK_CURRENT = "untrack-current"
    UP = "up"
    YANK = "yank"


@unique
class ActionWithArgType(StrEnum):
    BECOME = "become"
    CHANGE_BORDER_LABEL = "change-border-label"
    CHANGE_HEADER = "change-header"
    CHANGE_MULTI = "change-multi"
    CHANGE_PREVIEW = "change-preview"
    CHANGE_PREVIEW_LABEL = "change-preview-label"
    CHANGE_PREVIEW_WINDOW = "change-preview-window"
    CHANGE_PROMPT = "change-prompt"
    CHANGE_QUERY = "change-query"
    EXECUTE = "execute"
    EXECUTE_SILENT = "execute-silent"
    POS = "pos"
    PREVIEW = "preview"
    PRINT = "print"
    PUT = "put"
    REBIND = "rebind"
    RELOAD = "reload"
    RELOAD_SYNC = "reload-sync"
    TRANSFORM_BORDER_LABEL = "transform-border-label"
    TRANSFORM_HEADER = "transform-header"
    TRANSFORM_PREVIEW_LABEL = "transform-preview-label"
    TRANSFORM_PROMPT = "transform-prompt"
    TRANSFORM_QUERY = "transform-query"
    UNBIND = "unbind"


@unique
class ActionArgSeparator(Enum):
    PARENTHESES = enum_auto()
    CURLY_BRACES = enum_auto()
    SQUARE_BRACKETS = enum_auto()
    ANGLED_BRACKETS = enum_auto()
    TILDE = enum_auto()
    EXCLAMATION = enum_auto()
    AT = enum_auto()
    POUND = enum_auto()
    DOLLAR = enum_auto()
    PERCENT = enum_auto()
    CARET = enum_auto()
    AMPERSAND = enum_auto()
    ASTERISK = enum_auto()
    SEMICOLON = enum_auto()
    SLASH = enum_auto()
    PIPE = enum_auto()

    def opener(self) -> str:
        match self:
        # yapf: disable
            case ActionArgSeparator.PARENTHESES: return "("
            case ActionArgSeparator.CURLY_BRACES: return "{"
            case ActionArgSeparator.SQUARE_BRACKETS: return "["
            case ActionArgSeparator.ANGLED_BRACKETS: return "<"
            case ActionArgSeparator.TILDE: return "~"
            case ActionArgSeparator.EXCLAMATION: return "!"
            case ActionArgSeparator.AT: return "@"
            case ActionArgSeparator.POUND: return "#"
            case ActionArgSeparator.DOLLAR: return "$"
            case ActionArgSeparator.PERCENT: return "%"
            case ActionArgSeparator.CARET: return "^"
            case ActionArgSeparator.AMPERSAND: return "&"
            case ActionArgSeparator.ASTERISK: return "*"
            case ActionArgSeparator.SEMICOLON: return ";"
            case ActionArgSeparator.SLASH: return "/"
            case ActionArgSeparator.PIPE: return "|"
            case _: raise NotImplementedError()
            # yapf: enable

    def closer(self) -> str:
        match self:
        # yapf: disable
            case ActionArgSeparator.PARENTHESES: return ")"
            case ActionArgSeparator.CURLY_BRACES: return "}"
            case ActionArgSeparator.SQUARE_BRACKETS: return "]"
            case ActionArgSeparator.ANGLED_BRACKETS: return ">"
            case ActionArgSeparator.TILDE: return "~"
            case ActionArgSeparator.EXCLAMATION: return "!"
            case ActionArgSeparator.AT: return "@"
            case ActionArgSeparator.POUND: return "#"
            case ActionArgSeparator.DOLLAR: return "$"
            case ActionArgSeparator.PERCENT: return "%"
            case ActionArgSeparator.CARET: return "^"
            case ActionArgSeparator.AMPERSAND: return "&"
            case ActionArgSeparator.ASTERISK: return "*"
            case ActionArgSeparator.SEMICOLON: return ";"
            case ActionArgSeparator.SLASH: return "/"
            case ActionArgSeparator.PIPE: return "|"
            case _: raise NotImplementedError()
            # yapf: enable


@dataclass(slots=True, kw_only=True, frozen=True)
class ActionWithArg:
    action_type: ActionWithArgType
    argument: str
    separator: ActionArgSeparator = ActionArgSeparator.PARENTHESES

    def __str__(self) -> str:
        return "".join([
            self.action_type,
            self.separator.opener(),
            self.argument,
            self.separator.closer(),
        ])


@dataclass(slots=True, kw_only=True, frozen=True)
class Binding:
    binding: Key | Event
    actions: list[ActionSimple | ActionWithArg]

    def __str__(self) -> str:
        return f"{self.binding}:{'+'.join(str(a) for a in self.actions)}"


@dataclass(slots=True, kw_only=True)
class InterfaceOptions:
    multi: bool = False   # --multi --no-multi
    no_mouse: bool = False   # --no-mouse
    bind: list[Binding] | None = None   # --bind
    cycle: bool = False   # --cycle
    wrap: bool = False   # --wrap
    wrap_sign: str | None = None   # --wrap-sign
    keep_right: bool = False   # --keep-right
    scroll_off: int = 3   # --scroll-off
    no_hscroll: bool = False   # --no-hscroll
    hscroll_off: int = 10   # --hscroll-off
    filepath_word: bool = False   # --filepath-word
    jump_labels: str | None = None   # --jump-labels=CHARS

    def as_args(self) -> list[str]:
        args = [
            '--multi' if self.multi else '--no-multi',
            '--cycle' if self.cycle else '--no-cycle',
            '--wrap' if self.wrap else '--no-wrap',
            '--keep-right' if self.keep_right else '--no-keep-right',
            f'--scroll-off={self.scroll_off}',
            '--no-hscroll' if self.no_hscroll else '--hscroll',
            f'--hscroll-off={self.hscroll_off}',
            '--filepath-word' if self.filepath_word else '--no-filepath-word',
        ]
        if self.no_mouse:
            args.append('--no-mouse')
        if self.bind is not None:
            args.append(f'--bind={",".join(str(b) for b in self.bind)!r}')
        if self.wrap_sign is not None:
            args.append(f'--wrap-sign={self.wrap_sign!r}')
        if self.jump_labels is not None:
            args.append(f'--jump-labels={",".join(self.jump_labels)!r}')
        return args


@unique
class TmuxPosition(StrEnum):
    CENTER = "center"
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"

    def default_width(self) -> Pixels | Percent:
        TP = TmuxPosition
        match self:
            case TP.CENTER | TP.LEFT | TP.RIGHT:
                return Percent(50)
            case TP.TOP | TP.BOTTOM:
                return Percent(100)
            case other:
                raise RuntimeError(f"No default width known for: {other}")

    def default_height(self) -> Pixels | Percent:
        TP = TmuxPosition
        match self:
            case TP.CENTER | TP.TOP | TP.BOTTOM:
                return Percent(50)
            case TP.LEFT | TP.RIGHT:
                return Percent(100)
            case other:
                raise RuntimeError(f"No default height known for: {other}")


@dataclass(slots=True, kw_only=True, frozen=True)
class TmuxSettings:
    position: TmuxPosition = TmuxPosition.CENTER
    width: Pixels | Percent | None = None
    height: Pixels | Percent | None = None

    def __str__(self) -> str:
        return ",".join([
            position,
            TmuxPosition.default_width() if width is None else width,
            TmuxPosition.default_height() if height is None else height,
        ])


@unique
class LayoutType(StrEnum):
    DEFAULT = "default"
    REVERSE = "reverse"
    REVERSE_LIST = "reverse-list"


@unique
class BorderType(StrEnum):
    ROUNDED = "rounded"
    SHARP = "sharp"
    BOLD = "bold"
    DOUBLE = "double"
    BLOCK = "block"
    THINBLOCK = "thinblock"
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"
    NONE = "none"


Pixels = NewType("Pixels", int)


class Percent(float):

    def __str__(self) -> str:
        return super().__str__() + "%"


@dataclass(slots=True, kw_only=True, frozen=True)
class Height:
    value: Pixels | Percent
    adaptive: bool = False

    def __str__(self) -> str:
        return ("~" if self.adaptive else "") + str(self.value)


@dataclass(slots=True, kw_only=True, frozen=True)
class Sides:
    top: Pixels | Percent = Pixels(0)
    bottom: Pixels | Percent = Pixels(0)
    left: Pixels | Percent = Pixels(0)
    right: Pixels | Percent = Pixels(0)

    def __str__(self) -> str:
        return ",".join(map(str, [
            self.top,
            self.right,
            self.bottom,
            self.left,
        ]))


@unique
class LayoutInfoStyle(StrEnum):
    DEFAULT = "default"
    RIGHT = "right"
    INLINE = "inline"
    INLINE_RIGHT = "inline-right"
    HIDDEN = "hidden"


@unique
class LabelSide(StrEnum):
    TOP = "top"
    BOTTOM = "bottom"


@dataclass(slots=True, kw_only=True, frozen=True)
class LabelPosition:
    offset: int = 0
    side: LabelSide = LabelSide.TOP

    def __str__(self) -> str:
        return f"{self.offset}:{self.side}"


@dataclass(slots=True, kw_only=True)
class LayoutOptions:
    height: Height | None = None
    min_height: Pixels = Pixels(10)
    tmux: TmuxSettings | None = None
    layout: LayoutType = LayoutType.DEFAULT
    border: BorderType = BorderType.ROUNDED
    border_label: str | None = None   # --border-label
    border_label_pos: LabelPosition = LabelPosition()
    no_unicode: bool = False   # --no-unicode
    ambidouble: bool = False
    margin: Sides = Sides()
    padding: Sides = Sides()
    info: LayoutInfoStyle = LayoutInfoStyle.DEFAULT
    info_command: str | None = None
    separator: str | None = None
    scrollbar: str | None = None
    prompt: str | None = None
    pointer: str | None = None
    marker: str | None = None
    marker_multi_line: str | None = None
    header: str | None = None
    header_lines: int = 0   # --header-lines
    header_first: bool = False
    ellipsis: str = ".."

    def as_args(self) -> list[str]:
        args = [
            f'--min-height={self.min_height}',
            f'--layout={self.layout}',
            f'--border={self.border}',
            f'--border-label-pos={self.border_label_pos}',
            '--no-unicode' if self.no_unicode else '--unicode',
            '--ambidouble' if self.ambidouble else '--no-ambidouble',
            f'--margin={self.margin}',
            f'--padding={self.padding}',
            f'--info={self.info}',
            f'--header-lines={self.header_lines}',
            '--header-first' if self.header_first else '--no-header-first',
            '--ellipsis={self.ellipsis}',
        ]
        if self.height is not None:
            args.append(f'--height={self.height}')
        if self.tmux is not None:
            args.append(f'--tmux={self.tmux}')
        if self.border_label is not None:
            args.append(f'--border-label={self.border_label}')
        if self.info_command is not None:
            args.append(f'--info-command={self.info_command!r}')
        if self.separator is not None:
            args.append(f'--separator={self.separator}')
        if self.scrollbar is not None:
            args.append(f'--scrollbar={self.scrollbar}')
        if self.prompt is not None:
            args.append(f'--prompt={self.prompt}')
        if self.pointer is not None:
            args.append(f'--pointer={self.pointer}')
        if self.marker is not None:
            args.append(f'--marker={self.marker}')
        if self.marker_multi_line is not None:
            args.append(f'--marker-multi-line={self.marker_multi_line}')
        if self.header is not None:
            args.append(f'--header={self.header}')
        return args


@unique
class ColorName(StrEnum):
    FG = "fg"
    SELECTED_FG = "selected-fg"
    PREVIEW_FG = "preview-fg"
    BG = "bg"
    SELECTED_BG = "selected-bg"
    PREVIEW_BG = "preview-bg"
    HL = "hl"
    SELECTED_HL = "selected-hl"
    FG_CURRENT_LINE = "fg+"
    BG_CURRENT_LINE = "bg+"
    GUTTER = "gutter"
    HL_CURRENT_LINE = "hl+"
    QUERY = "query"
    DISABLED = "disabled"
    INFO = "info"
    BORDER = "border"
    SCROLLBAR = "scrollbar"
    PREVIEW_BORDER = "preview-border"
    PREVIEW_SCROLLBAR = "preview-scrollbar"
    SEPARATOR = "separator"
    LABEL = "label"
    PREVIEW_LABEL = "preview-label"
    PROMPT = "prompt"
    POINTER = "pointer"
    MARKER = "marker"
    SPINNER = "spinner"
    HEADER = "header"


@unique
class BaseColorScheme(StrEnum):
    DARK_256 = "dark"
    LIGHT_256 = "light"
    DARK_16 = "16"
    NO_COLOR = "bw"


@unique
class AnsiColor16(IntEnum):
    BLACK = 0
    RED = 1
    GREEN = 2
    YELLOW = 3
    BLUE = 4
    MAGENTA = 5
    CYAN = 6
    WHITE = 7
    BRIGHT_BLACK = 8
    BRIGHT_RED = 9
    BRIGHT_GREEN = 10
    BRIGHT_YELLOW = 11
    BRIGHT_BLUE = 12
    BRIGHT_MAGENTA = 13
    BRIGHT_CYAN = 14
    BRIGHT_WHITE = 15


class AnsiColor256(int):

    def __init__(self, value) -> None:
        if value < 0 or value >= 256:
            raise ValueError("out of bounds")
        super.__init__(value)


@dataclass(slots=True, kw_only=True, frozen=True)
class AnsiColorRgb:
    r: AnsiColor256
    g: AnsiColor256
    b: AnsiColor256

    def __str__(self) -> str:
        return f'#{self.r:0=2x}{self.g:0=2x{self.b:0=2x}}'


int.__new__


class AnsiColorDefault(int):

    def __new__(cls: type) -> AnsiColorDefault:
        return int.__new__(cls, -1)


AnsiColor: TypeAlias = AnsiColorDefault | AnsiColor16 | AnsiColor256 | AnsiColorRgb


@unique
class AnsiAttribute(StrEnum):
    REGULAR = "regular"
    BOLD = "bold"
    UNDERLINE = "underline"
    REVERSE = "reverse"
    DIM = "dim"
    ITALIC = "italic"
    STRIKETHROUGH = "strikethrough"


@dataclass(slots=True, kw_only=True, frozen=True)
class ColorMapping:
    color_name: ColorName
    ansi_color: AnsiColor | None = None
    ansi_attribute: AnsiAttribute | None = None

    def __str__(self) -> str:
        parts: list[str] = [self.color_name]
        if self.ansi_color is not None:
            parts.append(str(self.ansi_color))
        if self.ansi_attribute is not None:
            parts.append(self.ansi_attribute)
        return ":".join(parts)


@dataclass(slots=True, kw_only=True, frozen=True)
class Color:
    base_scheme: BaseColorScheme
    mappings: list[ColorMapping] | None = None

    def __str__(self) -> str:
        if self.mappings is None:
            return self.base_scheme
        return ",".join([
            self.base_scheme,
            *map(str, self.mappings),
        ])


@dataclass(slots=True, kw_only=True)
class DisplayOptions:
    ansi: bool = False
    tabstop: int = 8
    color: Color | None = None
    highlight_line: bool = False
    no_bold: bool = False
    black: bool = False

    def as_args(self) -> list[str]:
        args = [
            '--ansi' if self.ansi else '--no-ansi',
            f'--tabstop={self.tabstop}',
            '--highlight-line' if self.highlight_line else '--no-highlight-line',
            '--no-bold' if self.no_bold else '--bold',
            '--black' if self.black else '--no-black',
        ]
        if self.color is not None:
            args.append(f'--color={self.color}')
        return args


@dataclass(slots=True, kw_only=True)
class HistoryOptions:
    history: Path | str | None = None
    history_size: int = 1000

    def as_args(self) -> list[str]:
        args = [f'--history-size={self.history_size}']
        if self.history is not None:
            args.append(f'--history={self.history}')
        return args


@unique
class PreviewLabel(StrEnum):
    BORDER_ROUNDED = "border-rounded"
    BORDER_SHARP = "border-sharp"
    BORDER_BOLD = "border-bold"
    BORDER_DOUBLE = "border-double"
    BORDER_BLOCK = "border-block"
    BORDER_THINBLOCK = "border-thinblock"
    BORDER_HORIZONTAL = "border-horizontal"
    BORDER_TOP = "border-top"
    BORDER_BOTTOM = "border-bottom"


@unique
class PreviewWindowPosition(StrEnum):
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


@unique
class PreviewWindowBorderType(StrEnum):
    ROUNDED = "border-rounded"
    SHARP = "border-sharp"
    BOLD = "border-bold"
    DOUBLE = "border-double"
    BLOCK = "border-block"
    THINBLOCK = "border-thinblock"
    HORIZONTAL = "border-horizontal"
    VERTICAL = "border-vertical"
    TOP = "border-top"
    BOTTOM = "border-bottom"
    LEFT = "border-left"
    RIGHT = "border-right"
    NONE = "border-none"


@dataclass(slots=True, kw_only=True)
class PreviewOptions:
    preview_command: str | None = None   # --preview
    preview_label: PreviewLabel = PreviewLabel.BORDER_ROUNDED
    preview_label_pos: LabelPosition = LabelPosition()
    preview_window: str | None = None

    def as_args(self) -> list[str]:
        args = [
            f'--preview-label={self.preview_label}',
            f'--preview-label-pos={self.preview_label_pos}',
        ]
        if self.preview_command is not None:
            args.append(f'--preview={self.preview_command}')
        if self.preview_window is not None:
            args.append(f'--preview-window={self.preview_window}')
        return args


class Port(int):

    def __new__(cls, value) -> Port:
        if value < 0 or value >= 2**16:
            raise ValueError("out of bounds")
        return int.__new__(cls, value)


@dataclass(slots=True, kw_only=True, frozen=True)
class RemoteHost:
    address: str | None
    port: Port

    def __str__(self) -> str:
        if self.address is None:
            return f"{self.address}:{self.port}"
        return str(self.port)


@dataclass(slots=True, kw_only=True)
class ScriptingOptions:
    query: str | None = None
    select_1: bool = False
    exit_0: bool = False
    filter: str | None = None
    print_query: bool = False
    expect: list[Key] | None = None
    read0: bool = False
    print0: bool = False
    no_clear: bool = False
    sync: bool = False
    with_shell: str | None = None
    listen: RemoteHost | None = None
    listen_unsafe: RemoteHost | None = None

    def as_args(self) -> list[str]:
        args = [
            '--select-1' if self.select_1 else '--no-select-1',
            '--exit-0' if self.exit_0 else '--no-exit-0',
            '--print-query' if self.print_query else '--no-print-query',
            '--read0' if self.read0 else '--no-read0',
            '--print0' if self.print0 else '--no-print0',
            '--no-clear' if self.no_clear else '--clear',
            '--sync' if self.sync else '--no-sync',
        ]
        if self.query is not None:
            args.append(f'--query={self.query}')
        if self.filter is not None:
            args.append(f'--filter={self.filter}')
        if self.listen is not None:
            args.append(f'--listen={self.listen}')
        if self.listen_unsafe is not None:
            args.append(f'--listen-unsafe={self.listen_unsafe}')
        if self.expect is not None:
            args.append(f'--expect={",".join(self.expect)}')
        if self.with_shell is not None:
            args.append(f'--with-shell={self.with_shell}')
        return args


@unique
class TraversalBehavior(StrEnum):
    FILE = "file"
    DIR = "dir"
    FOLLOW = "follow"
    HIDDEN = "hidden"


@dataclass(slots=True, kw_only=True)
class DirectoryTraversalOptions:
    walker: set[TraversalBehavior] | None = None
    walker_root: str | Path | None = None
    walker_skip: Iterable[str | Path] | None = None

    def as_args(self) -> list[str]:
        args = []
        if self.walker is not None:
            args.append(f'--walker={",".join(self.walker)}')
        if self.walker_root is not None:
            args.append(f'--walker-root={self.walker_root!s}')
        if self.walker_skip is not None:
            args.append(f'--walker-skip={",".join(map(str, self.walker_skip))}')
        return args


@unique
class Shell(StrEnum):
    BASH = "bash"
    ZSH = "zsh"
    FISH = "fish"


@dataclass(slots=True, kw_only=True)
class ShellIntegrationOptions:
    shell: Shell | None = None

    def as_args(self) -> list[str]:
        if self.shell is not None:
            return [str(self.shell)]


def _resolve_fzf_path() -> str:
    if (p := shutil.which('fzf')) is not None:
        return p
    raise FileNotFoundError("could't find 'fzf' binary in $PATH. is it even installed?")


@dataclass(slots=True, kw_only=True)
class FuzzyFinderBuilder:
    binary_path: Path | str = field(default_factory=_resolve_fzf_path)
    search: SearchOptions | None = None
    results: ResultsOptions | None = None
    interface: InterfaceOptions | None = None
    layout: LayoutOptions | None = None
    display: DisplayOptions | None = None
    history: HistoryOptions | None = None
    preview: PreviewOptions | None = None
    scripting: ScriptingOptions | None = None
    directory_traversal: DirectoryTraversalOptions | None = None
    shell_integration: ShellIntegrationOptions | None = None

    def build(self) -> FuzzyFinder:
        args = itertools.chain(
            () if self.search is None else self.search.as_args(),
            () if self.results is None else self.results.as_args(),
            () if self.interface is None else self.interface.as_args(),
            () if self.layout is None else self.layout.as_args(),
            () if self.display is None else self.display.as_args(),
            () if self.history is None else self.history.as_args(),
            () if self.preview is None else self.preview.as_args(),
            () if self.scripting is None else self.scripting.as_args(),
            () if self.directory_traversal is None else self.directory_traversal.as_args(),
            () if self.shell_integration is None else self.shell_integration.as_args(),
        )
        if self.scripting is not None and self.scripting.print0:
            _output_sep = '\0'
        else:
            _output_sep = '\n'

        return FuzzyFinder(
            binary_path=self.binary_path,
            args=args,
            _output_sep=_output_sep,
        )


@unique
class ExitStatusCode(IntEnum):
    NORMAL = 0
    NO_MATCH = 1
    ERROR = 2
    USER_INTERRUPTED = 130


@dataclass(slots=True, kw_only=True, frozen=True)
class FuzzyFinderOutput:
    exit_status_code: ExitStatusCode
    output: list[str]


@dataclass(slots=True, kw_only=True, frozen=True)
class FuzzyFinder:
    binary_path: Path | str
    args: Iterable[str] = field(default_factory=list)
    _output_sep: str = '\n'

    def run(self, input_lines: str, **other_popen_kwargs) -> FuzzyFinderOutput:
        process = sp.run(
            args=list(itertools.chain([self.binary_path], self.args)),
            text=True,
            stdout=sp.PIPE,
            stderr=None,
            input=input_lines,
            **other_popen_kwargs,
        )
        return FuzzyFinderOutput(
            exit_status_code=ExitStatusCode(value=process.returncode),
            output=process.stdout[:-1].split(sep=self._output_sep),
        )


def fzf(input_text: str, **options) -> list[str]:
    try:
        return FuzzyFinderBuilder(**options).build().run(input_text, check=True).output
    except sp.CalledProcessError as error:
        print(f"fzf returned status code: {ExitStatusCode(value=error.returncode).name}")
        raise


def fzf_iter(input: Iterable[SupportsStr], **options) -> list[str]:
    builder = FuzzyFinderBuilder(**options)
    try:
        sep = '\0' if builder.scripting.read0 else '\n'   # type: ignore
    except AttributeError:
        sep = '\n'

    try:
        return builder.build().run(sep.join(map(str, input)), check=True).output
    except sp.CalledProcessError as error:
        print(f"fzf returned status code: {ExitStatusCode(value=error.returncode).name}")
        raise


def _join_kv(key: SupportsStr, val: SupportsStr, delimiter: str = ':') -> str:
    return f"{key}{delimiter}{val}"


def fzf_pairs(input: Iterable[tuple[SupportsStr, SupportsStr]], **options) -> list[str]:
    KEY_INDEX = 1
    VAL_INDEX = 2
    KV_SEP = ':'

    if not hasattr(options, "search"):
        options["search"] = SearchOptions()
    options["search"].with_nth = [VAL_INDEX]
    options["search"].delimiter = KV_SEP

    builder = FuzzyFinderBuilder(**options)
    try:
        line_sep = '\0' if builder.scripting.read0 else '\n'   # type: ignore
    except AttributeError:
        line_sep = '\n'

    input_text = line_sep.join(starmap(partial(_join_kv, delimiter=KV_SEP), input))
    try:
        raw_output = builder.build().run(input_text, check=True).output
        return [line.split(KV_SEP, maxsplit=1)[KEY_INDEX - 1] for line in raw_output]
    except sp.CalledProcessError as error:
        print(f"fzf returned status code: {ExitStatusCode(value=error.returncode).name}")
        raise


def fzf_mapping(input: Mapping[SupportsStr, SupportsStr], **options) -> list[str]:
    return fzf_pairs(input.items())
