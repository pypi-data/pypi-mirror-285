"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from PyDefold.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x12ddf/ddf_math.proto\x12\x06dmMath\x1a\x18ddf/ddf_extensions.proto"U\n\x06Point3\x12\x0c\n\x01x\x18\x01 \x01(\x02:\x010\x12\x0c\n\x01y\x18\x02 \x01(\x02:\x010\x12\x0c\n\x01z\x18\x03 \x01(\x02:\x010\x12\x0c\n\x01d\x18\x04 \x01(\x02:\x010:\x13\x82\xb5\x18\x0fdmVMath::Point3"W\n\x07Vector3\x12\x0c\n\x01x\x18\x01 \x01(\x02:\x010\x12\x0c\n\x01y\x18\x02 \x01(\x02:\x010\x12\x0c\n\x01z\x18\x03 \x01(\x02:\x010\x12\x0c\n\x01d\x18\x04 \x01(\x02:\x010:\x14\x82\xb5\x18\x10dmVMath::Vector3"W\n\x07Vector4\x12\x0c\n\x01x\x18\x01 \x01(\x02:\x010\x12\x0c\n\x01y\x18\x02 \x01(\x02:\x010\x12\x0c\n\x01z\x18\x03 \x01(\x02:\x010\x12\x0c\n\x01w\x18\x04 \x01(\x02:\x010:\x14\x82\xb5\x18\x10dmVMath::Vector4"Q\n\x04Quat\x12\x0c\n\x01x\x18\x01 \x01(\x02:\x010\x12\x0c\n\x01y\x18\x02 \x01(\x02:\x010\x12\x0c\n\x01z\x18\x03 \x01(\x02:\x010\x12\x0c\n\x01w\x18\x04 \x01(\x02:\x011:\x11\x82\xb5\x18\rdmVMath::Quat"\x8d\x01\n\tTransform\x12\x1e\n\x08rotation\x18\x01 \x01(\x0b2\x0c.dmMath.Quat\x12$\n\x0btranslation\x18\x02 \x01(\x0b2\x0f.dmMath.Vector3\x12\x1e\n\x05scale\x18\x03 \x01(\x0b2\x0f.dmMath.Vector3:\x1a\x82\xb5\x18\x16dmTransform::Transform"\x9f\x02\n\x07Matrix4\x12\x0e\n\x03m00\x18\x01 \x01(\x02:\x011\x12\x0e\n\x03m01\x18\x02 \x01(\x02:\x010\x12\x0e\n\x03m02\x18\x03 \x01(\x02:\x010\x12\x0e\n\x03m03\x18\x04 \x01(\x02:\x010\x12\x0e\n\x03m10\x18\x05 \x01(\x02:\x010\x12\x0e\n\x03m11\x18\x06 \x01(\x02:\x011\x12\x0e\n\x03m12\x18\x07 \x01(\x02:\x010\x12\x0e\n\x03m13\x18\x08 \x01(\x02:\x010\x12\x0e\n\x03m20\x18\t \x01(\x02:\x010\x12\x0e\n\x03m21\x18\n \x01(\x02:\x010\x12\x0e\n\x03m22\x18\x0b \x01(\x02:\x011\x12\x0e\n\x03m23\x18\x0c \x01(\x02:\x010\x12\x0e\n\x03m30\x18\r \x01(\x02:\x010\x12\x0e\n\x03m31\x18\x0e \x01(\x02:\x010\x12\x0e\n\x03m32\x18\x0f \x01(\x02:\x010\x12\x0e\n\x03m33\x18\x10 \x01(\x02:\x011:\x14\x82\xb5\x18\x10dmVMath::Matrix4BH\n\x10com.dynamo.protoB\x07DdfMath\x92\xb5\x18)dmsdk/dlib/vmath.h dmsdk/dlib/transform.h'
    )
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'ddf.ddf_math_pb2',
    globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = (
        b'\n\x10com.dynamo.protoB\x07DdfMath\x92\xb5\x18)dmsdk/dlib/vmath.h dmsdk/dlib/transform.h'
        )
    _POINT3._options = None
    _POINT3._serialized_options = b'\x82\xb5\x18\x0fdmVMath::Point3'
    _VECTOR3._options = None
    _VECTOR3._serialized_options = b'\x82\xb5\x18\x10dmVMath::Vector3'
    _VECTOR4._options = None
    _VECTOR4._serialized_options = b'\x82\xb5\x18\x10dmVMath::Vector4'
    _QUAT._options = None
    _QUAT._serialized_options = b'\x82\xb5\x18\rdmVMath::Quat'
    _TRANSFORM._options = None
    _TRANSFORM._serialized_options = b'\x82\xb5\x18\x16dmTransform::Transform'
    _MATRIX4._options = None
    _MATRIX4._serialized_options = b'\x82\xb5\x18\x10dmVMath::Matrix4'
    _POINT3._serialized_start = 56
    _POINT3._serialized_end = 141
    _VECTOR3._serialized_start = 143
    _VECTOR3._serialized_end = 230
    _VECTOR4._serialized_start = 232
    _VECTOR4._serialized_end = 319
    _QUAT._serialized_start = 321
    _QUAT._serialized_end = 402
    _TRANSFORM._serialized_start = 405
    _TRANSFORM._serialized_end = 546
    _MATRIX4._serialized_start = 549
    _MATRIX4._serialized_end = 836

