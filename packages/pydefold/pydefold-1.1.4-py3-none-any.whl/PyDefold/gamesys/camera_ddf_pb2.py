"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from PyDefold.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from PyDefold.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x18gamesys/camera_ddf.proto\x12\x0cdmGamesysDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto"\xae\x01\n\nCameraDesc\x12\x14\n\x0caspect_ratio\x18\x01 \x02(\x02\x12\x0b\n\x03fov\x18\x02 \x02(\x02\x12\x0e\n\x06near_z\x18\x03 \x02(\x02\x12\r\n\x05far_z\x18\x04 \x02(\x02\x12\x1c\n\x11auto_aspect_ratio\x18\x05 \x01(\r:\x010\x12"\n\x17orthographic_projection\x18\x06 \x01(\r:\x010\x12\x1c\n\x11orthographic_zoom\x18\x07 \x01(\x02:\x011"\x8f\x01\n\tSetCamera\x12\x14\n\x0caspect_ratio\x18\x01 \x02(\x02\x12\x0b\n\x03fov\x18\x02 \x02(\x02\x12\x0e\n\x06near_z\x18\x03 \x02(\x02\x12\r\n\x05far_z\x18\x04 \x02(\x02\x12"\n\x17orthographic_projection\x18\x05 \x01(\r:\x010\x12\x1c\n\x11orthographic_zoom\x18\x06 \x01(\x02:\x011"\x14\n\x12AcquireCameraFocus"\x14\n\x12ReleaseCameraFocusB"\n\x18com.dynamo.gamesys.protoB\x06Camera'
    )
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR,
    'gamesys.camera_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = (
        b'\n\x18com.dynamo.gamesys.protoB\x06Camera')
    _CAMERADESC._serialized_start = 89
    _CAMERADESC._serialized_end = 263
    _SETCAMERA._serialized_start = 266
    _SETCAMERA._serialized_end = 409
    _ACQUIRECAMERAFOCUS._serialized_start = 411
    _ACQUIRECAMERAFOCUS._serialized_end = 431
    _RELEASECAMERAFOCUS._serialized_start = 433
    _RELEASECAMERAFOCUS._serialized_end = 453

