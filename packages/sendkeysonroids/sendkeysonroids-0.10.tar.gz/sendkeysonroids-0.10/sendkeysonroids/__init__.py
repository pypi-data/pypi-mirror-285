import re
import struct
import random
import sys
import os
from adbshellexecuter import (
    get_short_path_name,
    UniversalADBExecutor,
)
from functools import cache
from normaltext import lookup
import base64
from typing import Literal

modulecfg = sys.modules[__name__]
modulecfg.cache_commands_concat_str_and_bytes = {}
modulecfg.cache_string_bytes_newlines_linux = {}
modulecfg.cache_split_echo_printf = {}
modulecfg.cache_tuples = {}
modulecfg.cache_dict_for_special_chars = {}
this_folder = os.path.dirname(os.path.abspath(__file__))
regex_compiled_for_bin_prefix = re.compile(r"^b[\'\"]", re.I)
FORMAT = "iiHHI"  # should be "llHHI", but long is sometimes 32 bit and sometimes 64 bit, that way it works on both
chunk_size = struct.calcsize(FORMAT)
pack_fu = struct.Struct(FORMAT).pack
unpack_fu = struct.Struct(FORMAT).unpack

all_linux_key_events = {
    "KEY_RESERVED": 0,
    "KEY_ESC": 1,
    "KEY_1": 2,
    "KEY_2": 3,
    "KEY_3": 4,
    "KEY_4": 5,
    "KEY_5": 6,
    "KEY_6": 7,
    "KEY_7": 8,
    "KEY_8": 9,
    "KEY_9": 10,
    "KEY_0": 11,
    "KEY_MINUS": 12,
    "KEY_EQUAL": 13,
    "KEY_BACKSPACE": 14,
    "KEY_TAB": 15,
    "KEY_Q": 16,
    "KEY_W": 17,
    "KEY_E": 18,
    "KEY_R": 19,
    "KEY_T": 20,
    "KEY_Y": 21,
    "KEY_U": 22,
    "KEY_I": 23,
    "KEY_O": 24,
    "KEY_P": 25,
    "KEY_LEFTBRACE": 26,
    "KEY_RIGHTBRACE": 27,
    "KEY_ENTER": 28,
    "KEY_LEFTCTRL": 29,
    "KEY_A": 30,
    "KEY_S": 31,
    "KEY_D": 32,
    "KEY_F": 33,
    "KEY_G": 34,
    "KEY_H": 35,
    "KEY_J": 36,
    "KEY_K": 37,
    "KEY_L": 38,
    "KEY_SEMICOLON": 39,
    "KEY_APOSTROPHE": 40,
    "KEY_GRAVE": 41,
    "KEY_LEFTSHIFT": 42,
    "KEY_BACKSLASH": 43,
    "KEY_Z": 44,
    "KEY_X": 45,
    "KEY_C": 46,
    "KEY_V": 47,
    "KEY_B": 48,
    "KEY_N": 49,
    "KEY_M": 50,
    "KEY_COMMA": 51,
    "KEY_DOT": 52,
    "KEY_SLASH": 53,
    "KEY_RIGHTSHIFT": 54,
    "KEY_KPASTERISK": 55,
    "KEY_LEFTALT": 56,
    "KEY_SPACE": 57,
    "KEY_CAPSLOCK": 58,
    "KEY_F1": 59,
    "KEY_F2": 60,
    "KEY_F3": 61,
    "KEY_F4": 62,
    "KEY_F5": 63,
    "KEY_F6": 64,
    "KEY_F7": 65,
    "KEY_F8": 66,
    "KEY_F9": 67,
    "KEY_F10": 68,
    "KEY_NUMLOCK": 69,
    "KEY_SCROLLLOCK": 70,
    "KEY_KP7": 71,
    "KEY_KP8": 72,
    "KEY_KP9": 73,
    "KEY_KPMINUS": 74,
    "KEY_KP4": 75,
    "KEY_KP5": 76,
    "KEY_KP6": 77,
    "KEY_KPPLUS": 78,
    "KEY_KP1": 79,
    "KEY_KP2": 80,
    "KEY_KP3": 81,
    "KEY_KP0": 82,
    "KEY_KPDOT": 83,
    "KEY_ZENKAKUHANKAKU": 85,
    "KEY_102ND": 86,
    "KEY_F11": 87,
    "KEY_F12": 88,
    "KEY_RO": 89,
    "KEY_KATAKANA": 90,
    "KEY_HIRAGANA": 91,
    "KEY_HENKAN": 92,
    "KEY_KATAKANAHIRAGANA": 93,
    "KEY_MUHENKAN": 94,
    "KEY_KPJPCOMMA": 95,
    "KEY_KPENTER": 96,
    "KEY_RIGHTCTRL": 97,
    "KEY_KPSLASH": 98,
    "KEY_SYSRQ": 99,
    "KEY_RIGHTALT": 100,
    "KEY_LINEFEED": 101,
    "KEY_HOME": 102,
    "KEY_UP": 103,
    "KEY_PAGEUP": 104,
    "KEY_LEFT": 105,
    "KEY_RIGHT": 106,
    "KEY_END": 107,
    "KEY_DOWN": 108,
    "KEY_PAGEDOWN": 109,
    "KEY_INSERT": 110,
    "KEY_DELETE": 111,
    "KEY_MACRO": 112,
    "KEY_MUTE": 113,
    "KEY_VOLUMEDOWN": 114,
    "KEY_VOLUMEUP": 115,
    "KEY_POWER": 116,
    "KEY_KPEQUAL": 117,
    "KEY_KPPLUSMINUS": 118,
    "KEY_PAUSE": 119,
    "KEY_SCALE": 120,
    "KEY_KPCOMMA": 121,
    "KEY_HANGEUL": 122,
    "KEY_HANGUEL": 122,
    "KEY_HANJA": 123,
    "KEY_YEN": 124,
    "KEY_LEFTMETA": 125,
    "KEY_RIGHTMETA": 126,
    "KEY_COMPOSE": 127,
    "KEY_STOP": 128,
    "KEY_AGAIN": 129,
    "KEY_PROPS": 130,
    "KEY_UNDO": 131,
    "KEY_FRONT": 132,
    "KEY_COPY": 133,
    "KEY_OPEN": 134,
    "KEY_PASTE": 135,
    "KEY_FIND": 136,
    "KEY_CUT": 137,
    "KEY_HELP": 138,
    "KEY_MENU": 139,
    "KEY_CALC": 140,
    "KEY_SETUP": 141,
    "KEY_SLEEP": 142,
    "KEY_WAKEUP": 143,
    "KEY_FILE": 144,
    "KEY_SENDFILE": 145,
    "KEY_DELETEFILE": 146,
    "KEY_XFER": 147,
    "KEY_PROG1": 148,
    "KEY_PROG2": 149,
    "KEY_WWW": 150,
    "KEY_MSDOS": 151,
    "KEY_COFFEE": 152,
    "KEY_SCREENLOCK": 152,
    "KEY_ROTATE_DISPLAY": 153,
    "KEY_DIRECTION": 153,
    "KEY_CYCLEWINDOWS": 154,
    "KEY_MAIL": 155,
    "KEY_BOOKMARKS": 156,
    "KEY_COMPUTER": 157,
    "KEY_BACK": 158,
    "KEY_FORWARD": 159,
    "KEY_CLOSECD": 160,
    "KEY_EJECTCD": 161,
    "KEY_EJECTCLOSECD": 162,
    "KEY_NEXTSONG": 163,
    "KEY_PLAYPAUSE": 164,
    "KEY_PREVIOUSSONG": 165,
    "KEY_STOPCD": 166,
    "KEY_RECORD": 167,
    "KEY_REWIND": 168,
    "KEY_PHONE": 169,
    "KEY_ISO": 170,
    "KEY_CONFIG": 171,
    "KEY_HOMEPAGE": 172,
    "KEY_REFRESH": 173,
    "KEY_EXIT": 174,
    "KEY_MOVE": 175,
    "KEY_EDIT": 176,
    "KEY_SCROLLUP": 177,
    "KEY_SCROLLDOWN": 178,
    "KEY_KPLEFTPAREN": 179,
    "KEY_KPRIGHTPAREN": 180,
    "KEY_NEW": 181,
    "KEY_REDO": 182,
    "KEY_F13": 183,
    "KEY_F14": 184,
    "KEY_F15": 185,
    "KEY_F16": 186,
    "KEY_F17": 187,
    "KEY_F18": 188,
    "KEY_F19": 189,
    "KEY_F20": 190,
    "KEY_F21": 191,
    "KEY_F22": 192,
    "KEY_F23": 193,
    "KEY_F24": 194,
    "KEY_PLAYCD": 200,
    "KEY_PAUSECD": 201,
    "KEY_PROG3": 202,
    "KEY_PROG4": 203,
    "KEY_ALL_APPLICATIONS": 204,
    "KEY_DASHBOARD": 204,
    "KEY_SUSPEND": 205,
    "KEY_CLOSE": 206,
    "KEY_PLAY": 207,
    "KEY_FASTFORWARD": 208,
    "KEY_BASSBOOST": 209,
    "KEY_PRINT": 210,
    "KEY_HP": 211,
    "KEY_CAMERA": 212,
    "KEY_SOUND": 213,
    "KEY_QUESTION": 214,
    "KEY_EMAIL": 215,
    "KEY_CHAT": 216,
    "KEY_SEARCH": 217,
    "KEY_CONNECT": 218,
    "KEY_FINANCE": 219,
    "KEY_SPORT": 220,
    "KEY_SHOP": 221,
    "KEY_ALTERASE": 222,
    "KEY_CANCEL": 223,
    "KEY_BRIGHTNESSDOWN": 224,
    "KEY_BRIGHTNESSUP": 225,
    "KEY_MEDIA": 226,
    "KEY_SWITCHVIDEOMODE": 227,
    "KEY_KBDILLUMTOGGLE": 228,
    "KEY_KBDILLUMDOWN": 229,
    "KEY_KBDILLUMUP": 230,
    "KEY_SEND": 231,
    "KEY_REPLY": 232,
    "KEY_FORWARDMAIL": 233,
    "KEY_SAVE": 234,
    "KEY_DOCUMENTS": 235,
    "KEY_BATTERY": 236,
    "KEY_BLUETOOTH": 237,
    "KEY_WLAN": 238,
    "KEY_UWB": 239,
    "KEY_UNKNOWN": 240,
    "KEY_VIDEO_NEXT": 241,
    "KEY_VIDEO_PREV": 242,
    "KEY_BRIGHTNESS_CYCLE": 243,
    "KEY_BRIGHTNESS_AUTO": 244,
    "KEY_BRIGHTNESS_ZERO": 244,
    "KEY_DISPLAY_OFF": 245,
    "KEY_WWAN": 246,
    "KEY_WIMAX": 246,
    "KEY_RFKILL": 247,
    "KEY_MICMUTE": 248,
    "BTN_MISC": 0x100,
    "BTN_0": 0x100,
    "BTN_1": 0x101,
    "BTN_2": 0x102,
    "BTN_3": 0x103,
    "BTN_4": 0x104,
    "BTN_5": 0x105,
    "BTN_6": 0x106,
    "BTN_7": 0x107,
    "BTN_8": 0x108,
    "BTN_9": 0x109,
    "BTN_MOUSE": 0x110,
    "BTN_LEFT": 0x110,
    "BTN_RIGHT": 0x111,
    "BTN_MIDDLE": 0x112,
    "BTN_SIDE": 0x113,
    "BTN_EXTRA": 0x114,
    "BTN_FORWARD": 0x115,
    "BTN_BACK": 0x116,
    "BTN_TASK": 0x117,
    "BTN_JOYSTICK": 0x120,
    "BTN_TRIGGER": 0x120,
    "BTN_THUMB": 0x121,
    "BTN_THUMB2": 0x122,
    "BTN_TOP": 0x123,
    "BTN_TOP2": 0x124,
    "BTN_PINKIE": 0x125,
    "BTN_BASE": 0x126,
    "BTN_BASE2": 0x127,
    "BTN_BASE3": 0x128,
    "BTN_BASE4": 0x129,
    "BTN_BASE5": 0x12A,
    "BTN_BASE6": 0x12B,
    "BTN_DEAD": 0x12F,
    "BTN_GAMEPAD": 0x130,
    "BTN_SOUTH": 0x130,
    "BTN_A": 0x130,
    "BTN_EAST": 0x131,
    "BTN_B": 0x131,
    "BTN_C": 0x132,
    "BTN_NORTH": 0x133,
    "BTN_X": 0x133,
    "BTN_WEST": 0x134,
    "BTN_Y": 0x134,
    "BTN_Z": 0x135,
    "BTN_TL": 0x136,
    "BTN_TR": 0x137,
    "BTN_TL2": 0x138,
    "BTN_TR2": 0x139,
    "BTN_SELECT": 0x13A,
    "BTN_START": 0x13B,
    "BTN_MODE": 0x13C,
    "BTN_THUMBL": 0x13D,
    "BTN_THUMBR": 0x13E,
    "BTN_DIGI": 0x140,
    "BTN_TOOL_PEN": 0x140,
    "BTN_TOOL_RUBBER": 0x141,
    "BTN_TOOL_BRUSH": 0x142,
    "BTN_TOOL_PENCIL": 0x143,
    "BTN_TOOL_AIRBRUSH": 0x144,
    "BTN_TOOL_FINGER": 0x145,
    "BTN_TOOL_MOUSE": 0x146,
    "BTN_TOOL_LENS": 0x147,
    "BTN_TOOL_QUINTTAP": 0x148,
    "BTN_STYLUS3": 0x149,
    "BTN_TOUCH": 0x14A,
    "BTN_STYLUS": 0x14B,
    "BTN_STYLUS2": 0x14C,
    "BTN_TOOL_DOUBLETAP": 0x14D,
    "BTN_TOOL_TRIPLETAP": 0x14E,
    "BTN_TOOL_QUADTAP": 0x14F,
    "BTN_WHEEL": 0x150,
    "BTN_GEAR_DOWN": 0x150,
    "BTN_GEAR_UP": 0x151,
    "KEY_OK": 0x160,
    "KEY_SELECT": 0x161,
    "KEY_GOTO": 0x162,
    "KEY_CLEAR": 0x163,
    "KEY_POWER2": 0x164,
    "KEY_OPTION": 0x165,
    "KEY_INFO": 0x166,
    "KEY_TIME": 0x167,
    "KEY_VENDOR": 0x168,
    "KEY_ARCHIVE": 0x169,
    "KEY_PROGRAM": 0x16A,
    "KEY_CHANNEL": 0x16B,
    "KEY_FAVORITES": 0x16C,
    "KEY_EPG": 0x16D,
    "KEY_PVR": 0x16E,
    "KEY_MHP": 0x16F,
    "KEY_LANGUAGE": 0x170,
    "KEY_TITLE": 0x171,
    "KEY_SUBTITLE": 0x172,
    "KEY_ANGLE": 0x173,
    "KEY_ZOOM": 0x174,
    "KEY_MODE": 0x175,
    "KEY_KEYBOARD": 0x176,
    "KEY_SCREEN": 0x177,
    "KEY_PC": 0x178,
    "KEY_TV": 0x179,
    "KEY_TV2": 0x17A,
    "KEY_VCR": 0x17B,
    "KEY_VCR2": 0x17C,
    "KEY_SAT": 0x17D,
    "KEY_SAT2": 0x17E,
    "KEY_CD": 0x17F,
    "KEY_TAPE": 0x180,
    "KEY_RADIO": 0x181,
    "KEY_TUNER": 0x182,
    "KEY_PLAYER": 0x183,
    "KEY_TEXT": 0x184,
    "KEY_DVD": 0x185,
    "KEY_AUX": 0x186,
    "KEY_MP3": 0x187,
    "KEY_AUDIO": 0x188,
    "KEY_VIDEO": 0x189,
    "KEY_DIRECTORY": 0x18A,
    "KEY_LIST": 0x18B,
    "KEY_MEMO": 0x18C,
    "KEY_CALENDAR": 0x18D,
    "KEY_RED": 0x18E,
    "KEY_GREEN": 0x18F,
    "KEY_YELLOW": 0x190,
    "KEY_BLUE": 0x191,
    "KEY_CHANNELUP": 0x192,
    "KEY_CHANNELDOWN": 0x193,
    "KEY_FIRST": 0x194,
    "KEY_LAST": 0x195,
    "KEY_AB": 0x196,
    "KEY_NEXT": 0x197,
    "KEY_RESTART": 0x198,
    "KEY_SLOW": 0x199,
    "KEY_SHUFFLE": 0x19A,
    "KEY_BREAK": 0x19B,
    "KEY_PREVIOUS": 0x19C,
    "KEY_DIGITS": 0x19D,
    "KEY_TEEN": 0x19E,
    "KEY_TWEN": 0x19F,
    "KEY_VIDEOPHONE": 0x1A0,
    "KEY_GAMES": 0x1A1,
    "KEY_ZOOMIN": 0x1A2,
    "KEY_ZOOMOUT": 0x1A3,
    "KEY_ZOOMRESET": 0x1A4,
    "KEY_WORDPROCESSOR": 0x1A5,
    "KEY_EDITOR": 0x1A6,
    "KEY_SPREADSHEET": 0x1A7,
    "KEY_GRAPHICSEDITOR": 0x1A8,
    "KEY_PRESENTATION": 0x1A9,
    "KEY_DATABASE": 0x1AA,
    "KEY_NEWS": 0x1AB,
    "KEY_VOICEMAIL": 0x1AC,
    "KEY_ADDRESSBOOK": 0x1AD,
    "KEY_MESSENGER": 0x1AE,
    "KEY_DISPLAYTOGGLE": 0x1AF,
    "KEY_BRIGHTNESS_TOGGLE": 0x1AF,
    "KEY_SPELLCHECK": 0x1B0,
    "KEY_LOGOFF": 0x1B1,
    "KEY_DOLLAR": 0x1B2,
    "KEY_EURO": 0x1B3,
    "KEY_FRAMEBACK": 0x1B4,
    "KEY_FRAMEFORWARD": 0x1B5,
    "KEY_CONTEXT_MENU": 0x1B6,
    "KEY_MEDIA_REPEAT": 0x1B7,
    "KEY_10CHANNELSUP": 0x1B8,
    "KEY_10CHANNELSDOWN": 0x1B9,
    "KEY_IMAGES": 0x1BA,
    "KEY_DEL_EOL": 0x1C0,
    "KEY_DEL_EOS": 0x1C1,
    "KEY_INS_LINE": 0x1C2,
    "KEY_DEL_LINE": 0x1C3,
    "KEY_FN": 0x1D0,
    "KEY_FN_ESC": 0x1D1,
    "KEY_FN_F1": 0x1D2,
    "KEY_FN_F2": 0x1D3,
    "KEY_FN_F3": 0x1D4,
    "KEY_FN_F4": 0x1D5,
    "KEY_FN_F5": 0x1D6,
    "KEY_FN_F6": 0x1D7,
    "KEY_FN_F7": 0x1D8,
    "KEY_FN_F8": 0x1D9,
    "KEY_FN_F9": 0x1DA,
    "KEY_FN_F10": 0x1DB,
    "KEY_FN_F11": 0x1DC,
    "KEY_FN_F12": 0x1DD,
    "KEY_FN_1": 0x1DE,
    "KEY_FN_2": 0x1DF,
    "KEY_FN_D": 0x1E0,
    "KEY_FN_E": 0x1E1,
    "KEY_FN_F": 0x1E2,
    "KEY_FN_S": 0x1E3,
    "KEY_FN_B": 0x1E4,
    "KEY_BRL_DOT1": 0x1F1,
    "KEY_BRL_DOT2": 0x1F2,
    "KEY_BRL_DOT3": 0x1F3,
    "KEY_BRL_DOT4": 0x1F4,
    "KEY_BRL_DOT5": 0x1F5,
    "KEY_BRL_DOT6": 0x1F6,
    "KEY_BRL_DOT7": 0x1F7,
    "KEY_BRL_DOT8": 0x1F8,
    "KEY_BRL_DOT9": 0x1F9,
    "KEY_BRL_DOT10": 0x1FA,
    "KEY_NUMERIC_0": 0x200,
    "KEY_NUMERIC_1": 0x201,
    "KEY_NUMERIC_2": 0x202,
    "KEY_NUMERIC_3": 0x203,
    "KEY_NUMERIC_4": 0x204,
    "KEY_NUMERIC_5": 0x205,
    "KEY_NUMERIC_6": 0x206,
    "KEY_NUMERIC_7": 0x207,
    "KEY_NUMERIC_8": 0x208,
    "KEY_NUMERIC_9": 0x209,
    "KEY_NUMERIC_STAR": 0x20A,
    "KEY_NUMERIC_POUND": 0x20B,
    "KEY_NUMERIC_A": 0x20C,
    "KEY_NUMERIC_B": 0x20D,
    "KEY_NUMERIC_C": 0x20E,
    "KEY_NUMERIC_D": 0x20F,
    "KEY_CAMERA_FOCUS": 0x210,
    "KEY_WPS_BUTTON": 0x211,
    "KEY_TOUCHPAD_TOGGLE": 0x212,
    "KEY_TOUCHPAD_ON": 0x213,
    "KEY_TOUCHPAD_OFF": 0x214,
    "KEY_CAMERA_ZOOMIN": 0x215,
    "KEY_CAMERA_ZOOMOUT": 0x216,
    "KEY_CAMERA_UP": 0x217,
    "KEY_CAMERA_DOWN": 0x218,
    "KEY_CAMERA_LEFT": 0x219,
    "KEY_CAMERA_RIGHT": 0x21A,
    "KEY_ATTENDANT_ON": 0x21B,
    "KEY_ATTENDANT_OFF": 0x21C,
    "KEY_ATTENDANT_TOGGLE": 0x21D,
    "KEY_LIGHTS_TOGGLE": 0x21E,
    "BTN_DPAD_UP": 0x220,
    "BTN_DPAD_DOWN": 0x221,
    "BTN_DPAD_LEFT": 0x222,
    "BTN_DPAD_RIGHT": 0x223,
    "KEY_ALS_TOGGLE": 0x230,
    "KEY_ROTATE_LOCK_TOGGLE": 0x231,
    "KEY_BUTTONCONFIG": 0x240,
    "KEY_TASKMANAGER": 0x241,
    "KEY_JOURNAL": 0x242,
    "KEY_CONTROLPANEL": 0x243,
    "KEY_APPSELECT": 0x244,
    "KEY_SCREENSAVER": 0x245,
    "KEY_VOICECOMMAND": 0x246,
    "KEY_ASSISTANT": 0x247,
    "KEY_BRIGHTNESS_MIN": 0x250,
    "KEY_BRIGHTNESS_MAX": 0x251,
    "KEY_KBDINPUTASSIST_PREV": 0x260,
    "KEY_KBDINPUTASSIST_NEXT": 0x261,
    "KEY_KBDINPUTASSIST_PREVGROUP": 0x262,
    "KEY_KBDINPUTASSIST_NEXTGROUP": 0x263,
    "KEY_KBDINPUTASSIST_ACCEPT": 0x264,
    "KEY_KBDINPUTASSIST_CANCEL": 0x265,
    "KEY_RIGHT_UP": 0x266,
    "KEY_RIGHT_DOWN": 0x267,
    "KEY_LEFT_UP": 0x268,
    "KEY_LEFT_DOWN": 0x269,
    "KEY_ROOT_MENU": 0x26A,
    "KEY_MEDIA_TOP_MENU": 0x26B,
    "KEY_NUMERIC_11": 0x26C,
    "KEY_NUMERIC_12": 0x26D,
    "KEY_AUDIO_DESC": 0x26E,
    "KEY_3D_MODE": 0x26F,
    "KEY_NEXT_FAVORITE": 0x270,
    "KEY_STOP_RECORD": 0x271,
    "KEY_PAUSE_RECORD": 0x272,
    "KEY_VOD": 0x273,
    "KEY_UNMUTE": 0x274,
    "KEY_FASTREVERSE": 0x275,
    "KEY_SLOWREVERSE": 0x276,
    "KEY_DATA": 0x277,
    "KEY_ONSCREEN_KEYBOARD": 0x278,
    "BTN_TRIGGER_HAPPY": 0x2C0,
    "BTN_TRIGGER_HAPPY1": 0x2C0,
    "BTN_TRIGGER_HAPPY2": 0x2C1,
    "BTN_TRIGGER_HAPPY3": 0x2C2,
    "BTN_TRIGGER_HAPPY4": 0x2C3,
    "BTN_TRIGGER_HAPPY5": 0x2C4,
    "BTN_TRIGGER_HAPPY6": 0x2C5,
    "BTN_TRIGGER_HAPPY7": 0x2C6,
    "BTN_TRIGGER_HAPPY8": 0x2C7,
    "BTN_TRIGGER_HAPPY9": 0x2C8,
    "BTN_TRIGGER_HAPPY10": 0x2C9,
    "BTN_TRIGGER_HAPPY11": 0x2CA,
    "BTN_TRIGGER_HAPPY12": 0x2CB,
    "BTN_TRIGGER_HAPPY13": 0x2CC,
    "BTN_TRIGGER_HAPPY14": 0x2CD,
    "BTN_TRIGGER_HAPPY15": 0x2CE,
    "BTN_TRIGGER_HAPPY16": 0x2CF,
    "BTN_TRIGGER_HAPPY17": 0x2D0,
    "BTN_TRIGGER_HAPPY18": 0x2D1,
    "BTN_TRIGGER_HAPPY19": 0x2D2,
    "BTN_TRIGGER_HAPPY20": 0x2D3,
    "BTN_TRIGGER_HAPPY21": 0x2D4,
    "BTN_TRIGGER_HAPPY22": 0x2D5,
    "BTN_TRIGGER_HAPPY23": 0x2D6,
    "BTN_TRIGGER_HAPPY24": 0x2D7,
    "BTN_TRIGGER_HAPPY25": 0x2D8,
    "BTN_TRIGGER_HAPPY26": 0x2D9,
    "BTN_TRIGGER_HAPPY27": 0x2DA,
    "BTN_TRIGGER_HAPPY28": 0x2DB,
    "BTN_TRIGGER_HAPPY29": 0x2DC,
    "BTN_TRIGGER_HAPPY30": 0x2DD,
    "BTN_TRIGGER_HAPPY31": 0x2DE,
    "BTN_TRIGGER_HAPPY32": 0x2DF,
    "BTN_TRIGGER_HAPPY33": 0x2E0,
    "BTN_TRIGGER_HAPPY34": 0x2E1,
    "BTN_TRIGGER_HAPPY35": 0x2E2,
    "BTN_TRIGGER_HAPPY36": 0x2E3,
    "BTN_TRIGGER_HAPPY37": 0x2E4,
    "BTN_TRIGGER_HAPPY38": 0x2E5,
    "BTN_TRIGGER_HAPPY39": 0x2E6,
    "BTN_TRIGGER_HAPPY40": 0x2E7,
}


std_key_mapping_dict = {
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
}


def keystroke_to_bytedata(key_event_number, randomize_other_args=False):
    key_event_number = int(key_event_number)
    timestamp = 1720908827
    always_zero = 0
    always_one = 1
    always_26254 = 26254
    ascending_number = 42378
    small_random_number1 = 2
    small_random_number2 = 2
    some_16_bit_number = 21775
    some_16_bit_number_unique = 19629
    always_4 = 4
    some_random_unique_int1 = 152847
    some_random_unique_int2 = 216237
    always_262148 = 262148
    if randomize_other_args:
        some_random_unique_int1 = random.randint(1, 65535)
        some_random_unique_int2 = random.randint(1, 65535)

    key_event_number_bitshifted = (key_event_number << 16) + 1
    purebytedata = b"".join(
        pack_fu(*q)
        for q in (
            (
                timestamp,
                always_zero,
                some_16_bit_number,
                small_random_number1,
                always_zero,
            ),
            (
                always_262148,
                key_event_number,
                ascending_number,
                always_26254,
                always_zero,
            ),
            (
                some_random_unique_int1,
                always_zero,
                always_one,
                key_event_number,
                always_one,
            ),
            (
                timestamp,
                always_zero,
                some_16_bit_number,
                small_random_number1,
                always_zero,
            ),
            (always_zero, always_zero, ascending_number, always_26254, always_zero),
            (
                some_random_unique_int2,
                always_zero,
                always_4,
                always_4,
                key_event_number,
            ),
            (
                timestamp,
                always_zero,
                some_16_bit_number_unique,
                small_random_number2,
                always_zero,
            ),
            (
                key_event_number_bitshifted,
                always_zero,
                ascending_number,
                always_26254,
                always_zero,
            ),
            (
                some_random_unique_int2,
                always_zero,
                always_zero,
                always_zero,
                always_zero,
            ),
        )
    )

    return (
        (
            regex_compiled_for_bin_prefix.sub("", ascii(purebytedata)[:-1])
            .replace("'", "'\\''")
            .encode()
        ),
        purebytedata,
        (
            regex_compiled_for_bin_prefix.sub("", ascii(purebytedata[:72])[:-1])
            .replace("'", "'\\''")
            .encode()
        ),
        (
            regex_compiled_for_bin_prefix.sub("", ascii(purebytedata[72:])[:-1])
            .replace("'", "'\\''")
            .encode()
        ),
        purebytedata[:72],
        purebytedata[72:],
    )


class DictGetMissing(dict):
    def __init__(self, *args, **kwargs):
        self.key_mapping_dict = kwargs.pop("key_mapping_dict", {})
        super().__init__(self, *args, **kwargs)

    def __missing__(self, k):
        if k in self.key_mapping_dict:
            if " + " in self.key_mapping_dict[k]:
                return modulecfg.cache_tuples.setdefault(
                    k,
                    tuple(
                        self[subkey] for subkey in self.key_mapping_dict[k].split(" + ")
                    )
                    + tuple(
                        reversed(
                            [
                                self[subkey]
                                for subkey in self.key_mapping_dict[k].split(" + ")
                            ]
                        )
                    ),
                )
            return self[self.key_mapping_dict[k]]

        if len(k) == 1:
            knew = modulecfg.cache_dict_for_special_chars.setdefault(
                k,
                "".join(
                    [
                        lookup(kx, case_sens=True, replace="", add_to_printable="")[
                            "suggested"
                        ]
                        for kx in k
                    ]
                ),
            )
            if knew in self.key_mapping_dict:
                print(f"{k} not found, substituting with {knew}")
                if " + " in self.key_mapping_dict[knew]:
                    return modulecfg.cache_tuples.setdefault(
                        knew,
                        tuple(
                            self[subkey]
                            for subkey in self.key_mapping_dict[knew].split(" + ")
                        )
                        + tuple(
                            reversed(
                                [
                                    self[subkey]
                                    for subkey in self.key_mapping_dict[knew].split(
                                        " + "
                                    )
                                ]
                            )
                        ),
                    )
                return self[self.key_mapping_dict[knew]]

        print('ignoring key "%s"' % k)
        return {}


def prepare_binary_data(key_mapping_dict, all_linux_key_events):
    sendevents_value_folder = os.path.join(this_folder, "sendeventvalues")
    sendevents_value_folder_as_ascii = os.path.join(sendevents_value_folder, "ascii")
    sendevents_value_folder_as_bin = os.path.join(sendevents_value_folder, "bin")
    sendevents_value_folder_as_ascii_1half = os.path.join(
        sendevents_value_folder, "ascii_1half"
    )
    sendevents_value_folder_as_ascii_2half = os.path.join(
        sendevents_value_folder, "ascii_2half"
    )
    sendevents_value_folder_as_bin_1half = os.path.join(
        sendevents_value_folder, "bin_1half"
    )
    sendevents_value_folder_as_bin_2half = os.path.join(
        sendevents_value_folder, "bin_2half"
    )

    for folder in [
        sendevents_value_folder,
        sendevents_value_folder_as_ascii,
        sendevents_value_folder_as_bin,
        sendevents_value_folder_as_ascii_1half,
        sendevents_value_folder_as_ascii_2half,
        sendevents_value_folder_as_bin_1half,
        sendevents_value_folder_as_bin_2half,
    ]:
        os.makedirs(folder, exist_ok=True)
    all_linux_key_events_data = DictGetMissing(key_mapping_dict=key_mapping_dict)

    for key, value in all_linux_key_events.items():
        file_sendevents_value_folder_as_ascii = os.path.join(
            sendevents_value_folder_as_ascii, str(value)
        )
        file_sendevents_value_folder_as_bin = os.path.join(
            sendevents_value_folder_as_bin, str(value)
        )
        file_sendevents_value_folder_as_ascii_1half = os.path.join(
            sendevents_value_folder_as_ascii_1half, str(value)
        )
        file_sendevents_value_folder_as_ascii_2half = os.path.join(
            sendevents_value_folder_as_ascii_2half, str(value)
        )
        file_sendevents_value_folder_as_bin_1half = os.path.join(
            sendevents_value_folder_as_bin_1half, str(value)
        )
        file_sendevents_value_folder_as_bin_2half = os.path.join(
            sendevents_value_folder_as_bin_2half, str(value)
        )
        if (
            not os.path.exists(file_sendevents_value_folder_as_ascii)
            or not os.path.exists(file_sendevents_value_folder_as_bin)
            or not os.path.exists(file_sendevents_value_folder_as_ascii_1half)
            or not os.path.exists(file_sendevents_value_folder_as_ascii_2half)
            or not os.path.exists(file_sendevents_value_folder_as_bin_1half)
            or not os.path.exists(file_sendevents_value_folder_as_bin_2half)
        ):
            all_bin_files = keystroke_to_bytedata(value, randomize_other_args=False)
            for binfile, filedata in zip(
                [
                    file_sendevents_value_folder_as_ascii,
                    file_sendevents_value_folder_as_bin,
                    file_sendevents_value_folder_as_ascii_1half,
                    file_sendevents_value_folder_as_ascii_2half,
                    file_sendevents_value_folder_as_bin_1half,
                    file_sendevents_value_folder_as_bin_2half,
                ],
                all_bin_files,
            ):
                with open(binfile, "wb") as f:
                    f.write(filedata)
        all_linux_key_events_data[key] = {
            value: {
                "ascii": get_short_path_name(
                    long_name=file_sendevents_value_folder_as_ascii
                ),
                "bin": get_short_path_name(
                    long_name=file_sendevents_value_folder_as_bin
                ),
                "ascii_1half": get_short_path_name(
                    long_name=file_sendevents_value_folder_as_ascii_1half
                ),
                "ascii_2half": get_short_path_name(
                    long_name=file_sendevents_value_folder_as_ascii_2half
                ),
                "bin_1half": get_short_path_name(
                    long_name=file_sendevents_value_folder_as_bin_1half
                ),
                "bin_2half": get_short_path_name(
                    long_name=file_sendevents_value_folder_as_bin_2half
                ),
            }
        }

    return all_linux_key_events_data


@cache
def read_binary_filedata(path):
    try:
        with open(path, "rb") as f:
            data = f.read()
        return data
    except Exception:
        return b""


def _write_data_using_dd(
    path_on_device,
    lendata,
    numberofloops,
    inputdev="/dev/input/event3",
    blocksize=72,
    sleepbetweencommand=0,
    exec_or_eval="eval",
):
    if sleepbetweencommand > 0:
        sleepbetweencommand = f"sleep {sleepbetweencommand}"
    else:
        sleepbetweencommand = ""
    if exec_or_eval == "eval":
        quotes = '"'
        commandline = f"eval {quotes}dd status=none conv=sync count=1 skip=$skiphowmany bs=$blocksize if=$inputfile of=$outdevice{quotes}"
    else:
        commandline = 'dd status=none conv=sync count=1 skip="$skiphowmany" bs="$blocksize" if="$inputfile" of="$outdevice"'
    return rf"""#!/bin/sh
# su -c 'sh {path_on_device}.sh'
inputfile={path_on_device}
outdevice={inputdev}
totalchars={lendata}
blocksize={blocksize}
howmanyloops={numberofloops}
skiphowmany=0
for line in $(seq 1 $howmanyloops); do
        skiphowmany=$((line-1))
        {commandline}
        {sleepbetweencommand}
        skiphowmany=$((skiphowmany+1))
done
        """


def _generate_dd_command(
    binary_data,
    output_path,
    inputdev="/dev/input/event4",
    blocksize=72,
    sleepbetweencommand=0,
    exec_or_eval="exec",
    su_exe="su",
):
    lendata = len(binary_data)
    numberofloops = (lendata // blocksize) + 1
    scriptdata = _write_data_using_dd(
        path_on_device=output_path,
        lendata=lendata,
        numberofloops=numberofloops,
        inputdev=inputdev,
        blocksize=blocksize,
        sleepbetweencommand=sleepbetweencommand,
        exec_or_eval=exec_or_eval,
    )

    return (
        (scriptdata),
        (binary_data),
        f"""su -c 'sh {output_path}.sh'""",
        (output_path + ".sh"),
    )


def convert_to_concat_str_and_bytes(data, sep=b""):
    if not isinstance(data, (tuple)):
        data = tuple(data)
    return modulecfg.cache_commands_concat_str_and_bytes.setdefault(
        (data, sep),
        (sep if isinstance(sep, bytes) else dos2unix(sep.encode("utf-8"))).join(
            d if isinstance(d, bytes) else dos2unix(d.encode("utf-8")) for d in data
        ),
    )


def dos2unix(data):
    if isinstance(data, str):
        return modulecfg.cache_string_bytes_newlines_linux.setdefault(
            data, data.replace("\r\n", b"\n")
        )
    return modulecfg.cache_string_bytes_newlines_linux.setdefault(
        data, data.replace(b"\r\n", b"\n")
    )


def convert_to_base64_blocks(
    data,
    outputpath="/dev/input/event3",
    chunksize=128,
    echo_or_printf=b'printf "%b"',
    split_into_chunks=True,
):
    outputdata = modulecfg.cache_split_echo_printf.get(
        (data, outputpath, echo_or_printf, chunksize, split_into_chunks, "base64"), b""
    )
    if not outputdata:
        if isinstance(echo_or_printf, str):
            echo_or_printf = echo_or_printf.encode()
        if isinstance(data, str):
            data = data.encode()
        data = base64.b64encode(data)
        if isinstance(outputpath, str):
            outputpath = outputpath.encode()
        outputpathtmp = outputpath + b".tmp"
        if split_into_chunks:
            outputdata = b"\n".join(
                [
                    (
                        echo_or_printf
                        + b" '"
                        + (data[i : i + chunksize]).replace(b"'", b"'\\''")
                    )
                    + b"'"
                    + (b" > " if i == 0 else b" >> ")
                    + outputpathtmp
                    for i in range(0, len(data), chunksize)
                ]
            ).replace(b"\r\n", b"\n")
        else:
            outputdata = (
                (echo_or_printf + b" '" + (data).replace(b"'", b"'\\''") + b"'")
                + b" > "
                + outputpathtmp
            ).replace(b"\r\n", b"\n")
        outputdata = outputdata + b"\nbase64 -d " + outputpathtmp + b" > " + outputpath
        modulecfg.cache_split_echo_printf[
            (data, outputpath, echo_or_printf, chunksize, split_into_chunks, "base64")
        ] = outputdata
    return outputdata


def _convert_command_to_echo_or_printf_and_dd(
    binary_data,
    inputdev,
    output_path="/sdcard/echoen_dd.bin",
    su_exe="su",
    blocksize=72,
    sleepbetweencommand=0,
    exec_or_eval="exec",
    echo_or_printf="echo -e -n",
):
    scriptdata, binarydata, executecommand, output_path_sh = _generate_dd_command(
        binary_data=binary_data,
        output_path=output_path,
        inputdev=inputdev,
        blocksize=blocksize,
        sleepbetweencommand=sleepbetweencommand,
        exec_or_eval=exec_or_eval,
        su_exe=su_exe,
    )
    return (
        convert_to_concat_str_and_bytes(
            data=(
                f"{su_exe}\n" if su_exe else "",
                convert_to_base64_blocks(
                    data=binarydata,
                    outputpath=output_path,
                    chunksize=1024,
                    echo_or_printf=echo_or_printf,
                    split_into_chunks=True,
                ),
                b"\n",
                convert_to_base64_blocks(
                    data=scriptdata,
                    outputpath=output_path_sh,
                    chunksize=1024,
                    echo_or_printf=echo_or_printf,
                    split_into_chunks=True,
                ),
            ),
            sep=b"",
        ),
        executecommand,
    )


def parse_ascii_or_bin(my_text, ascii_or_bin, all_linux_key_events_data):
    wholecommand = []
    for letter in my_text:
        keystopress = all_linux_key_events_data[letter]
        if not keystopress:
            continue
        if isinstance(keystopress, dict):
            for key, value in keystopress.items():
                wholecommand.append(
                    read_binary_filedata(value[f"{ascii_or_bin}_1half"])
                )
                wholecommand.append(
                    read_binary_filedata(value[f"{ascii_or_bin}_2half"])
                )
        if isinstance(keystopress, tuple):
            for first_part_index in range(len(keystopress) // 2):
                for key, value in keystopress[first_part_index].items():
                    wholecommand.append(
                        read_binary_filedata(value[f"{ascii_or_bin}_1half"])
                    )
            for second_part_index in range(len(keystopress) // 2, len(keystopress)):
                for key, value in keystopress[second_part_index].items():
                    wholecommand.append(
                        read_binary_filedata(value[f"{ascii_or_bin}_2half"])
                    )

    return wholecommand


def bin_write_text_echo_or_printf_to_dd(
    my_text,
    input_device,
    all_linux_key_events_data,
    output_path="/sdcard/echoen_dd.bin",
    su_exe="su",
    blocksize=72,
    sleepbetweencommand=0,
    exec_or_eval="exec",
    echo_or_printf="echo -e -n",
):
    wholecommand = b"".join(
        parse_ascii_or_bin(my_text, "bin", all_linux_key_events_data)
    )
    return _convert_command_to_echo_or_printf_and_dd(
        binary_data=wholecommand,
        inputdev=input_device,
        output_path=output_path,
        su_exe=su_exe,
        blocksize=blocksize,
        sleepbetweencommand=sleepbetweencommand,
        exec_or_eval=exec_or_eval,
        echo_or_printf=echo_or_printf,
    )


def ascii_write_text_echo_or_printf(
    my_text,
    all_linux_key_events_data,
    su_exe="su",
    echo_or_printf="echo -e -n",
    input_device="/dev/input/event3",
):
    if not isinstance(input_device, bytes):
        input_device = input_device.encode()
    if not isinstance(echo_or_printf, bytes):
        echo_or_printf = echo_or_printf.encode()
    if not isinstance(su_exe, bytes):
        su_exe = su_exe.encode()
    wholecommand = parse_ascii_or_bin(my_text, "ascii", all_linux_key_events_data)

    return (
        su_exe
        + b"\n"
        + b"\n".join(
            echo_or_printf + b" '" + x + b"' > " + input_device for x in wholecommand
        )
    )


def press_a_key_for_duration(
    key,
    input_device,
    all_linux_key_events_data,
    echo_or_printf=b"echo -e -n",
    su_exe="su",
    duration=1,
):
    raw_key_ascii_data = parse_ascii_or_bin(key, "ascii", all_linux_key_events_data)
    half_len = len(raw_key_ascii_data) // 2
    if not isinstance(input_device, bytes):
        input_device = input_device.encode()
    if not isinstance(echo_or_printf, bytes):
        echo_or_printf = echo_or_printf.encode()
    if not isinstance(su_exe, bytes):
        su_exe = su_exe.encode()
    wholecmd = [
        echo_or_printf + b" '" + x + b"' > " + input_device for x in raw_key_ascii_data
    ]
    wholecmd.insert(half_len, f"sleep {duration}".encode())
    return su_exe + b"\n" + b"\n".join(wholecmd)


class CodeExec:
    def __init__(
        self,
        executer,
        init_cmd,
        main_cmd,
    ) -> None:
        self.init_cmd = init_cmd
        self.main_cmd = main_cmd
        self.init_cmd_str = (
            init_cmd.decode("utf-8", "backslashreplace")
            if init_cmd and isinstance(init_cmd, bytes)
            else init_cmd
            if isinstance(init_cmd, str)
            else "intital command not needed"
        )[:300] + "..."
        self.main_cmd_str = (
            main_cmd.decode("utf-8", "backslashreplace")
            if main_cmd and isinstance(main_cmd, bytes)
            else main_cmd
            if isinstance(main_cmd, str)
            else "intital command not needed"
        )[:300]
        self.executer = executer
        if not init_cmd:
            self.inital_command_success = True
        else:
            self.inital_command_success = False

    def __repr__(self) -> str:
        return f"INITAL COMMAND:\n{self.init_cmd_str}\n\n\nMAIN COMMAND:\n{self.main_cmd_str}"

    def __str__(self) -> str:
        return self.__repr__()

    def __call__(self, **kwargs):
        if not self.inital_command_success:
            self.run_init_command()
        self.run_main_command()
        return self

    def run_init_command(self, **kwargs):
        self.executer.shell_without_capturing_stdout_and_stderr(self.init_cmd, **kwargs)
        self.inital_command_success = True
        return self

    def run_main_command(self, **kwargs):
        self.executer.shell_without_capturing_stdout_and_stderr(self.main_cmd, **kwargs)
        return self


class SendEventKeysOnRoids:
    r"""
    A class to manage and send key events to an Android device. It uses ADB, but also runs directly on the device (rooted and Python installed) -> https://github.com/hansalemaos/termuxfree

    This class prepares binary data for key events, converts them into different formats, and executes
    corresponding commands on Android devices.
    """

    def __init__(
        self,
        adb_path=None,
        device_serial=None,
        input_device="/dev/input/event3",
        su_exe="su",
        blocksize=72,
        prefered_execution: Literal["exec", "eval"] = "exec",
        chunk_size=1024,
        key_mapping_dict=None,
    ) -> None:
        r"""
        Initializes the SendEventKeysOnRoids class with specified parameters.

        Args:
            adb_path (str, optional): Path to the ADB executable. Defaults to None.
            device_serial (str, optional): Serial number of the target Android device. Defaults to None.
            input_device (str, optional): Path to the input device on the Android device. Defaults to "/dev/input/event3".
            su_exe (str, optional): Command to gain superuser privileges on the Android device. Defaults to "su". ALWAYS NEEDED!
            blocksize (int, optional): Block size for the `dd` command. Defaults to 72. This controls the speed, use steps of 72
            prefered_execution (str, optional): Preferred method of command execution ('exec' or 'eval'). Defaults to "exec".
            chunk_size (int, optional): Chunk size for splitting data into base64 blocks. Defaults to 1024.
            key_mapping_dict (dict, optional): Dictionary mapping keys to Linux key event codes. Defaults to None.

        Attributes:
            adb_path (str): Path to the ADB executable.
            device_serial (str): Serial number of the target Android device.
            input_device (str): Path to the input device on the Android device.
            su_exe (str): Command to gain superuser privileges on the Android device.
            blocksize (int): Block size for the `dd` command.
            prefered_execution (str): Preferred method of command execution.
            chunk_size (int): Chunk size for splitting data into base64 blocks.
            key_mapping_dict (dict): Dictionary mapping keys to Linux key event codes.
            all_linux_key_events_data (dict): Prepared binary data for all Linux key events.
            adb_shell (UniversalADBExecutor): ADB shell executor instance.
        """
        if not key_mapping_dict:
            self.key_mapping_dict = std_key_mapping_dict
        else:
            self.key_mapping_dict = key_mapping_dict
        self.all_linux_key_events_data = prepare_binary_data(
            self.key_mapping_dict, all_linux_key_events
        )

        self.adb_path = adb_path
        self.device_serial = device_serial
        self.input_device = input_device
        self.randomize_data = False
        self.su_exe = su_exe
        self.blocksize = blocksize
        self.prefered_execution = prefered_execution
        self.chunk_size = chunk_size
        self.adb_shell = UniversalADBExecutor(self.adb_path, self.device_serial)

    def echo_input_text(self, text, input_device=None):
        r"""
        Generates a command to send text input to the specified input device using echo.

        Args:
            text (str): The text to send as input.
            input_device (str, optional): Path to the input device on the Android device. Defaults to the class's input_device.

        Returns:
            CodeExec: An instance of CodeExec class to execute the generated command.
        """
        cmdecho = ascii_write_text_echo_or_printf(
            text,
            all_linux_key_events_data=self.all_linux_key_events_data,
            echo_or_printf="echo -e -n",
            input_device=input_device or self.input_device,
        )
        return CodeExec(
            executer=self.adb_shell,
            init_cmd=b"",
            main_cmd=cmdecho,
        )

    def printf_input_text(self, text, input_device=None):
        r"""
        Generates a command to send text input to the specified input device using printf.

        Args:
            text (str): The text to send as input.
            input_device (str, optional): Path to the input device on the Android device. Defaults to the class's input_device.

        Returns:
            CodeExec: An instance of CodeExec class to execute the generated command.
        """
        cmdecho = ascii_write_text_echo_or_printf(
            text,
            all_linux_key_events_data=self.all_linux_key_events_data,
            echo_or_printf="printf",
            input_device=input_device or self.input_device,
        )
        return CodeExec(
            executer=self.adb_shell,
            init_cmd=b"",
            main_cmd=cmdecho,
        )

    def echo_input_text_dd(
        self,
        text,
        output_path="/sdcard/echo_input_text_dd.bin",
        blocksize=None,
        sleep_after_each_execution=0,
        exec_or_eval=None,
        input_device=None,
    ):
        r"""
        Generates a command to send text input as binary data using echo and dd commands.

        Args:
            text (str): The text to send as input.
            output_path (str, optional): Path to store the generated binary data on the device. Defaults to "/sdcard/echo_input_text_dd.bin".
            blocksize (int, optional): Block size for the `dd` command. Defaults to the class's blocksize, this controls the speed, use steps of 72
            sleep_after_each_execution (int, optional): Sleep duration between each command execution. Defaults to 0.
            exec_or_eval (str, optional): Preferred method of command execution ('exec' or 'eval'). Defaults to the class's prefered_execution.
            input_device (str, optional): Path to the input device on the Android device. Defaults to the class's input_device.

        Returns:
            CodeExec: An instance of CodeExec class to execute the generated command.
        """
        cmd1_dd_inicial, cmd1_dd_main = bin_write_text_echo_or_printf_to_dd(
            text,
            input_device=input_device or self.input_device,
            all_linux_key_events_data=self.all_linux_key_events_data,
            output_path=output_path,
            su_exe=self.su_exe,
            blocksize=blocksize or self.blocksize,
            sleepbetweencommand=sleep_after_each_execution,
            exec_or_eval=exec_or_eval or self.prefered_execution,
            echo_or_printf="echo -e -n",
        )
        return CodeExec(
            executer=self.adb_shell,
            init_cmd=cmd1_dd_inicial,
            main_cmd=cmd1_dd_main,
        )

    def printf_input_text_dd(
        self,
        text,
        output_path="/sdcard/printf_input_text_dd.bin",
        blocksize=None,
        sleep_after_each_execution=0,
        exec_or_eval=None,
        input_device=None,
    ):
        r"""
        Generates a command to send text input as binary data using printf and dd commands.

        Args:
            text (str): The text to send as input.
            output_path (str, optional): Path to store the generated binary data on the device. Defaults to "/sdcard/printf_input_text_dd.bin".
            blocksize (int, optional): Block size for the `dd` command. Defaults to the class's blocksize.
            sleep_after_each_execution (int, optional): Sleep duration between each command execution. Defaults to 0.
            exec_or_eval (str, optional): Preferred method of command execution ('exec' or 'eval'). Defaults to the class's prefered_execution.
            input_device (str, optional): Path to the input device on the Android device. Defaults to the class's input_device.

        Returns:
            CodeExec: An instance of CodeExec class to execute the generated command.
        """
        cmd1_dd_inicial, cmd1_dd_main = bin_write_text_echo_or_printf_to_dd(
            text,
            input_device=input_device or self.input_device,
            all_linux_key_events_data=self.all_linux_key_events_data,
            output_path=output_path,
            su_exe=self.su_exe,
            blocksize=blocksize or self.blocksize,
            sleepbetweencommand=sleep_after_each_execution,
            exec_or_eval=exec_or_eval or self.prefered_execution,
            echo_or_printf="printf",
        )
        return CodeExec(
            executer=self.adb_shell,
            init_cmd=cmd1_dd_inicial,
            main_cmd=cmd1_dd_main,
        )

    def echo_input_keypress(self, key, duration=1, input_device=None):
        r"""
        Generates a command to send a key press event to the specified input device using echo.

        Args:
            key (str): The key to press.
            duration (int, optional): Duration to hold the key press. Defaults to 1 second.
            input_device (str, optional): Path to the input device on the Android device. Defaults to the class's input_device.

        Returns:
            CodeExec: An instance of CodeExec class to execute the generated command.
        """
        wholecmd_bytes = press_a_key_for_duration(
            key,
            input_device=input_device or self.input_device,
            all_linux_key_events_data=self.all_linux_key_events_data,
            echo_or_printf=b"echo -e -n",
            su_exe=self.su_exe,
            duration=duration,
        )
        return CodeExec(
            executer=self.adb_shell,
            init_cmd=b"",
            main_cmd=wholecmd_bytes,
        )

    def printf_input_keypress(self, key, duration=1, input_device=None):
        r"""
        Generates a command to send a key press event to the specified input device using printf.

        Args:
            key (str): The key to press.
            duration (int, optional): Duration to hold the key press. Defaults to 1 second.
            input_device (str, optional): Path to the input device on the Android device. Defaults to the class's input_device.

        Returns:
            CodeExec: An instance of CodeExec class to execute the generated command.
        """
        wholecmd_bytes = press_a_key_for_duration(
            key,
            input_device=input_device or self.input_device,
            all_linux_key_events_data=self.all_linux_key_events_data,
            echo_or_printf=b"printf",
            su_exe=self.su_exe,
            duration=duration,
        )
        return CodeExec(
            executer=self.adb_shell,
            init_cmd=b"",
            main_cmd=wholecmd_bytes,
        )
