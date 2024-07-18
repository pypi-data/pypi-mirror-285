"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from PyDefold.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from PyDefold.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x0finput_ddf.proto\x12\ndmInputDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto"=\n\x11GamepadModifier_t\x12(\n\x03mod\x18\x01 \x02(\x0e2\x1b.dmInputDDF.GamepadModifier"\xa9\x01\n\x0fGamepadMapEntry\x12"\n\x05input\x18\x01 \x02(\x0e2\x13.dmInputDDF.Gamepad\x12%\n\x04type\x18\x02 \x02(\x0e2\x17.dmInputDDF.GamepadType\x12\r\n\x05index\x18\x03 \x02(\r\x12*\n\x03mod\x18\x04 \x03(\x0b2\x1d.dmInputDDF.GamepadModifier_t\x12\x10\n\x08hat_mask\x18\x05 \x01(\r"k\n\nGamepadMap\x12\x0e\n\x06device\x18\x01 \x02(\t\x12\x10\n\x08platform\x18\x02 \x02(\t\x12\x11\n\tdead_zone\x18\x03 \x02(\x02\x12(\n\x03map\x18\x04 \x03(\x0b2\x1b.dmInputDDF.GamepadMapEntry"5\n\x0bGamepadMaps\x12&\n\x06driver\x18\x01 \x03(\x0b2\x16.dmInputDDF.GamepadMap"<\n\nKeyTrigger\x12\x1e\n\x05input\x18\x01 \x02(\x0e2\x0f.dmInputDDF.Key\x12\x0e\n\x06action\x18\x02 \x02(\t"@\n\x0cMouseTrigger\x12 \n\x05input\x18\x01 \x02(\x0e2\x11.dmInputDDF.Mouse\x12\x0e\n\x06action\x18\x02 \x02(\t"D\n\x0eGamepadTrigger\x12"\n\x05input\x18\x01 \x02(\x0e2\x13.dmInputDDF.Gamepad\x12\x0e\n\x06action\x18\x02 \x02(\t"@\n\x0cTouchTrigger\x12 \n\x05input\x18\x01 \x02(\x0e2\x11.dmInputDDF.Touch\x12\x0e\n\x06action\x18\x02 \x02(\t">\n\x0bTextTrigger\x12\x1f\n\x05input\x18\x01 \x02(\x0e2\x10.dmInputDDF.Text\x12\x0e\n\x06action\x18\x02 \x02(\t"\x81\x02\n\x0cInputBinding\x12+\n\x0bkey_trigger\x18\x01 \x03(\x0b2\x16.dmInputDDF.KeyTrigger\x12/\n\rmouse_trigger\x18\x02 \x03(\x0b2\x18.dmInputDDF.MouseTrigger\x123\n\x0fgamepad_trigger\x18\x03 \x03(\x0b2\x1a.dmInputDDF.GamepadTrigger\x12/\n\rtouch_trigger\x18\x04 \x03(\x0b2\x18.dmInputDDF.TouchTrigger\x12-\n\x0ctext_trigger\x18\x05 \x03(\x0b2\x17.dmInputDDF.TextTrigger*\xff\r\n\x03Key\x12\r\n\tKEY_SPACE\x10\x00\x12\x0f\n\x0bKEY_EXCLAIM\x10\x01\x12\x10\n\x0cKEY_QUOTEDBL\x10\x02\x12\x0c\n\x08KEY_HASH\x10\x03\x12\x0e\n\nKEY_DOLLAR\x10\x04\x12\x11\n\rKEY_AMPERSAND\x10\x05\x12\r\n\tKEY_QUOTE\x10\x06\x12\x0e\n\nKEY_LPAREN\x10\x07\x12\x0e\n\nKEY_RPAREN\x10\x08\x12\x10\n\x0cKEY_ASTERISK\x10\t\x12\x0c\n\x08KEY_PLUS\x10\n\x12\r\n\tKEY_COMMA\x10\x0b\x12\r\n\tKEY_MINUS\x10\x0c\x12\x0e\n\nKEY_PERIOD\x10\r\x12\r\n\tKEY_SLASH\x10\x0e\x12\t\n\x05KEY_0\x10\x0f\x12\t\n\x05KEY_1\x10\x10\x12\t\n\x05KEY_2\x10\x11\x12\t\n\x05KEY_3\x10\x12\x12\t\n\x05KEY_4\x10\x13\x12\t\n\x05KEY_5\x10\x14\x12\t\n\x05KEY_6\x10\x15\x12\t\n\x05KEY_7\x10\x16\x12\t\n\x05KEY_8\x10\x17\x12\t\n\x05KEY_9\x10\x18\x12\r\n\tKEY_COLON\x10\x19\x12\x11\n\rKEY_SEMICOLON\x10\x1a\x12\x0c\n\x08KEY_LESS\x10\x1b\x12\x0e\n\nKEY_EQUALS\x10\x1c\x12\x0f\n\x0bKEY_GREATER\x10\x1d\x12\x10\n\x0cKEY_QUESTION\x10\x1e\x12\n\n\x06KEY_AT\x10\x1f\x12\t\n\x05KEY_A\x10 \x12\t\n\x05KEY_B\x10!\x12\t\n\x05KEY_C\x10"\x12\t\n\x05KEY_D\x10#\x12\t\n\x05KEY_E\x10$\x12\t\n\x05KEY_F\x10%\x12\t\n\x05KEY_G\x10&\x12\t\n\x05KEY_H\x10\'\x12\t\n\x05KEY_I\x10(\x12\t\n\x05KEY_J\x10)\x12\t\n\x05KEY_K\x10*\x12\t\n\x05KEY_L\x10+\x12\t\n\x05KEY_M\x10,\x12\t\n\x05KEY_N\x10-\x12\t\n\x05KEY_O\x10.\x12\t\n\x05KEY_P\x10/\x12\t\n\x05KEY_Q\x100\x12\t\n\x05KEY_R\x101\x12\t\n\x05KEY_S\x102\x12\t\n\x05KEY_T\x103\x12\t\n\x05KEY_U\x104\x12\t\n\x05KEY_V\x105\x12\t\n\x05KEY_W\x106\x12\t\n\x05KEY_X\x107\x12\t\n\x05KEY_Y\x108\x12\t\n\x05KEY_Z\x109\x12\x10\n\x0cKEY_LBRACKET\x10:\x12\x11\n\rKEY_BACKSLASH\x10;\x12\x10\n\x0cKEY_RBRACKET\x10<\x12\r\n\tKEY_CARET\x10=\x12\x12\n\x0eKEY_UNDERSCORE\x10>\x12\x11\n\rKEY_BACKQUOTE\x10?\x12\x0e\n\nKEY_LBRACE\x10@\x12\x0c\n\x08KEY_PIPE\x10A\x12\x0e\n\nKEY_RBRACE\x10B\x12\r\n\tKEY_TILDE\x10C\x12\x0b\n\x07KEY_ESC\x10D\x12\n\n\x06KEY_F1\x10E\x12\n\n\x06KEY_F2\x10F\x12\n\n\x06KEY_F3\x10G\x12\n\n\x06KEY_F4\x10H\x12\n\n\x06KEY_F5\x10I\x12\n\n\x06KEY_F6\x10J\x12\n\n\x06KEY_F7\x10K\x12\n\n\x06KEY_F8\x10L\x12\n\n\x06KEY_F9\x10M\x12\x0b\n\x07KEY_F10\x10N\x12\x0b\n\x07KEY_F11\x10O\x12\x0b\n\x07KEY_F12\x10P\x12\n\n\x06KEY_UP\x10Q\x12\x0c\n\x08KEY_DOWN\x10R\x12\x0c\n\x08KEY_LEFT\x10S\x12\r\n\tKEY_RIGHT\x10T\x12\x0e\n\nKEY_LSHIFT\x10U\x12\x0e\n\nKEY_RSHIFT\x10V\x12\r\n\tKEY_LCTRL\x10W\x12\r\n\tKEY_RCTRL\x10X\x12\x0c\n\x08KEY_LALT\x10Y\x12\x0c\n\x08KEY_RALT\x10Z\x12\x0b\n\x07KEY_TAB\x10[\x12\r\n\tKEY_ENTER\x10\\\x12\x11\n\rKEY_BACKSPACE\x10]\x12\x0e\n\nKEY_INSERT\x10^\x12\x0b\n\x07KEY_DEL\x10_\x12\x0e\n\nKEY_PAGEUP\x10`\x12\x10\n\x0cKEY_PAGEDOWN\x10a\x12\x0c\n\x08KEY_HOME\x10b\x12\x0b\n\x07KEY_END\x10c\x12\x0c\n\x08KEY_KP_0\x10d\x12\x0c\n\x08KEY_KP_1\x10e\x12\x0c\n\x08KEY_KP_2\x10f\x12\x0c\n\x08KEY_KP_3\x10g\x12\x0c\n\x08KEY_KP_4\x10h\x12\x0c\n\x08KEY_KP_5\x10i\x12\x0c\n\x08KEY_KP_6\x10j\x12\x0c\n\x08KEY_KP_7\x10k\x12\x0c\n\x08KEY_KP_8\x10l\x12\x0c\n\x08KEY_KP_9\x10m\x12\x11\n\rKEY_KP_DIVIDE\x10n\x12\x13\n\x0fKEY_KP_MULTIPLY\x10o\x12\x13\n\x0fKEY_KP_SUBTRACT\x10p\x12\x0e\n\nKEY_KP_ADD\x10q\x12\x12\n\x0eKEY_KP_DECIMAL\x10r\x12\x10\n\x0cKEY_KP_EQUAL\x10s\x12\x10\n\x0cKEY_KP_ENTER\x10t\x12\x13\n\x0fKEY_KP_NUM_LOCK\x10u\x12\x11\n\rKEY_CAPS_LOCK\x10v\x12\x13\n\x0fKEY_SCROLL_LOCK\x10w\x12\r\n\tKEY_PAUSE\x10x\x12\x0e\n\nKEY_LSUPER\x10y\x12\x0e\n\nKEY_RSUPER\x10z\x12\x0c\n\x08KEY_MENU\x10{\x12\x0c\n\x08KEY_BACK\x10|\x12\x11\n\rMAX_KEY_COUNT\x10}*\xae\x02\n\x05Mouse\x12\x12\n\x0eMOUSE_WHEEL_UP\x10\x00\x12\x14\n\x10MOUSE_WHEEL_DOWN\x10\x01\x12\x15\n\x11MOUSE_BUTTON_LEFT\x10\x02\x12\x17\n\x13MOUSE_BUTTON_MIDDLE\x10\x03\x12\x16\n\x12MOUSE_BUTTON_RIGHT\x10\x04\x12\x12\n\x0eMOUSE_BUTTON_1\x10\x05\x12\x12\n\x0eMOUSE_BUTTON_2\x10\x06\x12\x12\n\x0eMOUSE_BUTTON_3\x10\x07\x12\x12\n\x0eMOUSE_BUTTON_4\x10\x08\x12\x12\n\x0eMOUSE_BUTTON_5\x10\t\x12\x12\n\x0eMOUSE_BUTTON_6\x10\n\x12\x12\n\x0eMOUSE_BUTTON_7\x10\x0b\x12\x12\n\x0eMOUSE_BUTTON_8\x10\x0c\x12\x13\n\x0fMAX_MOUSE_COUNT\x10\r*\xa4\x05\n\x07Gamepad\x12\x17\n\x13GAMEPAD_LSTICK_LEFT\x10\x00\x12\x18\n\x14GAMEPAD_LSTICK_RIGHT\x10\x01\x12\x17\n\x13GAMEPAD_LSTICK_DOWN\x10\x02\x12\x15\n\x11GAMEPAD_LSTICK_UP\x10\x03\x12\x18\n\x14GAMEPAD_LSTICK_CLICK\x10\x04\x12\x14\n\x10GAMEPAD_LTRIGGER\x10\x05\x12\x15\n\x11GAMEPAD_LSHOULDER\x10\x06\x12\x15\n\x11GAMEPAD_LPAD_LEFT\x10\x07\x12\x16\n\x12GAMEPAD_LPAD_RIGHT\x10\x08\x12\x15\n\x11GAMEPAD_LPAD_DOWN\x10\t\x12\x13\n\x0fGAMEPAD_LPAD_UP\x10\n\x12\x17\n\x13GAMEPAD_RSTICK_LEFT\x10\x0b\x12\x18\n\x14GAMEPAD_RSTICK_RIGHT\x10\x0c\x12\x17\n\x13GAMEPAD_RSTICK_DOWN\x10\r\x12\x15\n\x11GAMEPAD_RSTICK_UP\x10\x0e\x12\x18\n\x14GAMEPAD_RSTICK_CLICK\x10\x0f\x12\x14\n\x10GAMEPAD_RTRIGGER\x10\x10\x12\x15\n\x11GAMEPAD_RSHOULDER\x10\x11\x12\x15\n\x11GAMEPAD_RPAD_LEFT\x10\x12\x12\x16\n\x12GAMEPAD_RPAD_RIGHT\x10\x13\x12\x15\n\x11GAMEPAD_RPAD_DOWN\x10\x14\x12\x13\n\x0fGAMEPAD_RPAD_UP\x10\x15\x12\x11\n\rGAMEPAD_START\x10\x16\x12\x10\n\x0cGAMEPAD_BACK\x10\x17\x12\x11\n\rGAMEPAD_GUIDE\x10\x18\x12\x15\n\x11GAMEPAD_CONNECTED\x10\x19\x12\x18\n\x14GAMEPAD_DISCONNECTED\x10\x1a\x12\x0f\n\x0bGAMEPAD_RAW\x10\x1b\x12\x15\n\x11MAX_GAMEPAD_COUNT\x10\x1c*S\n\x0bGamepadType\x12\x15\n\x11GAMEPAD_TYPE_AXIS\x10\x00\x12\x17\n\x13GAMEPAD_TYPE_BUTTON\x10\x01\x12\x14\n\x10GAMEPAD_TYPE_HAT\x10\x02*\x86\x01\n\x0fGamepadModifier\x12\x1b\n\x17GAMEPAD_MODIFIER_NEGATE\x10\x00\x12\x1a\n\x16GAMEPAD_MODIFIER_SCALE\x10\x01\x12\x1a\n\x16GAMEPAD_MODIFIER_CLAMP\x10\x02\x12\x1e\n\x1aMAX_GAMEPAD_MODIFIER_COUNT\x10\x03*-\n\x05Touch\x12\x0f\n\x0bTOUCH_MULTI\x10\x00\x12\x13\n\x0fMAX_TOUCH_COUNT\x10\x01*5\n\x04Text\x12\x08\n\x04TEXT\x10\x00\x12\x0f\n\x0bMARKED_TEXT\x10\x01\x12\x12\n\x0eMAX_TEXT_COUNT\x10\x02B\x1f\n\x16com.dynamo.input.protoB\x05Input'
    )
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'input_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x16com.dynamo.input.protoB\x05Input'
    _KEY._serialized_start = 1065
    _KEY._serialized_end = 2856
    _MOUSE._serialized_start = 2859
    _MOUSE._serialized_end = 3161
    _GAMEPAD._serialized_start = 3164
    _GAMEPAD._serialized_end = 3840
    _GAMEPADTYPE._serialized_start = 3842
    _GAMEPADTYPE._serialized_end = 3925
    _GAMEPADMODIFIER._serialized_start = 3928
    _GAMEPADMODIFIER._serialized_end = 4062
    _TOUCH._serialized_start = 4064
    _TOUCH._serialized_end = 4109
    _TEXT._serialized_start = 4111
    _TEXT._serialized_end = 4164
    _GAMEPADMODIFIER_T._serialized_start = 77
    _GAMEPADMODIFIER_T._serialized_end = 138
    _GAMEPADMAPENTRY._serialized_start = 141
    _GAMEPADMAPENTRY._serialized_end = 310
    _GAMEPADMAP._serialized_start = 312
    _GAMEPADMAP._serialized_end = 419
    _GAMEPADMAPS._serialized_start = 421
    _GAMEPADMAPS._serialized_end = 474
    _KEYTRIGGER._serialized_start = 476
    _KEYTRIGGER._serialized_end = 536
    _MOUSETRIGGER._serialized_start = 538
    _MOUSETRIGGER._serialized_end = 602
    _GAMEPADTRIGGER._serialized_start = 604
    _GAMEPADTRIGGER._serialized_end = 672
    _TOUCHTRIGGER._serialized_start = 674
    _TOUCHTRIGGER._serialized_end = 738
    _TEXTTRIGGER._serialized_start = 740
    _TEXTTRIGGER._serialized_end = 802
    _INPUTBINDING._serialized_start = 805
    _INPUTBINDING._serialized_end = 1062

