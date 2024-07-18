"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from PyDefold.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from PyDefold.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\rrig_ddf.proto\x12\x08dmRigDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto"\xcd\x01\n\x04Bone\x12\x0e\n\x06parent\x18\x01 \x02(\r\x12\n\n\x02id\x18\x02 \x02(\x04\x12\x0c\n\x04name\x18\x03 \x02(\t\x12&\n\x05local\x18\x04 \x02(\x0b2\x11.dmMath.TransformB\x04\xa0\xb5\x18\x01\x12&\n\x05world\x18\x05 \x02(\x0b2\x11.dmMath.TransformB\x04\xa0\xb5\x18\x01\x122\n\x11inverse_bind_pose\x18\x06 \x02(\x0b2\x11.dmMath.TransformB\x04\xa0\xb5\x18\x01\x12\x11\n\x06length\x18\x07 \x01(\x02:\x010:\x04\x98\xb5\x18\x01"g\n\x02IK\x12\n\n\x02id\x18\x01 \x02(\x04\x12\x0e\n\x06parent\x18\x02 \x02(\r\x12\r\n\x05child\x18\x03 \x02(\r\x12\x0e\n\x06target\x18\x04 \x02(\r\x12\x16\n\x08positive\x18\x05 \x01(\x08:\x04true\x12\x0e\n\x03mix\x18\x06 \x01(\x02:\x011"D\n\x08Skeleton\x12\x1d\n\x05bones\x18\x01 \x03(\x0b2\x0e.dmRigDDF.Bone\x12\x19\n\x03iks\x18\x02 \x03(\x0b2\x0c.dmRigDDF.IK"V\n\x0eAnimationTrack\x12\x0f\n\x07bone_id\x18\x01 \x02(\x04\x12\x11\n\tpositions\x18\x02 \x03(\x02\x12\x11\n\trotations\x18\x03 \x03(\x02\x12\r\n\x05scale\x18\x04 \x03(\x02"N\n\x08EventKey\x12\t\n\x01t\x18\x01 \x02(\x02\x12\x12\n\x07integer\x18\x02 \x01(\x05:\x010\x12\x10\n\x05float\x18\x03 \x01(\x02:\x010\x12\x11\n\x06string\x18\x04 \x01(\x04:\x010"@\n\nEventTrack\x12\x10\n\x08event_id\x18\x01 \x02(\x04\x12 \n\x04keys\x18\x02 \x03(\x0b2\x12.dmRigDDF.EventKey"\x97\x01\n\x0cRigAnimation\x12\n\n\x02id\x18\x01 \x02(\x04\x12\x10\n\x08duration\x18\x02 \x02(\x02\x12\x13\n\x0bsample_rate\x18\x03 \x02(\x02\x12(\n\x06tracks\x18\x04 \x03(\x0b2\x18.dmRigDDF.AnimationTrack\x12*\n\x0cevent_tracks\x18\x05 \x03(\x0b2\x14.dmRigDDF.EventTrack":\n\x0cAnimationSet\x12*\n\nanimations\x18\x01 \x03(\x0b2\x16.dmRigDDF.RigAnimation"0\n\x15AnimationInstanceDesc\x12\x17\n\tanimation\x18\x01 \x02(\tB\x04\xa0\xbb\x18\x01"Y\n\x10AnimationSetDesc\x123\n\nanimations\x18\x01 \x03(\x0b2\x1f.dmRigDDF.AnimationInstanceDesc\x12\x10\n\x08skeleton\x18\x02 \x01(\t"\x81\x03\n\x04Mesh\x12!\n\x08aabb_min\x18\x01 \x02(\x0b2\x0f.dmMath.Vector3\x12!\n\x08aabb_max\x18\x02 \x02(\x0b2\x0f.dmMath.Vector3\x12\x11\n\tpositions\x18\x03 \x03(\x02\x12\x0f\n\x07normals\x18\x04 \x03(\x02\x12\x10\n\x08tangents\x18\x05 \x03(\x02\x12\x0e\n\x06colors\x18\x06 \x03(\x02\x12\x11\n\ttexcoord0\x18\x07 \x03(\x02\x12 \n\x18num_texcoord0_components\x18\x08 \x01(\r\x12\x11\n\ttexcoord1\x18\t \x03(\x02\x12 \n\x18num_texcoord1_components\x18\n \x01(\r\x12\x0f\n\x07indices\x18\x0b \x01(\x0c\x123\n\x0eindices_format\x18\x0c \x01(\x0e2\x1b.dmRigDDF.IndexBufferFormat\x12\x0f\n\x07weights\x18\r \x03(\x02\x12\x14\n\x0cbone_indices\x18\x0e \x03(\r\x12\x16\n\x0ematerial_index\x18\x0f \x01(\r"u\n\x05Model\x12&\n\x05local\x18\x01 \x02(\x0b2\x11.dmMath.TransformB\x04\xa0\xb5\x18\x01\x12\n\n\x02id\x18\x02 \x02(\x04\x12\x1e\n\x06meshes\x18\x03 \x03(\x0b2\x0e.dmRigDDF.Mesh\x12\x12\n\x07bone_id\x18\x04 \x01(\x04:\x010:\x04\x98\xb5\x18\x01"h\n\x07MeshSet\x12\x1f\n\x06models\x18\x01 \x03(\x0b2\x0f.dmRigDDF.Model\x12\x11\n\tmaterials\x18\x02 \x03(\t\x12\x11\n\tbone_list\x18\x03 \x03(\x04\x12\x16\n\x0emax_bone_count\x18\x04 \x01(\r"r\n\x08RigScene\x12\x16\n\x08skeleton\x18\x01 \x01(\tB\x04\xa0\xbb\x18\x01\x12\x1b\n\ranimation_set\x18\x02 \x01(\tB\x04\xa0\xbb\x18\x01\x12\x16\n\x08mesh_set\x18\x03 \x02(\tB\x04\xa0\xbb\x18\x01\x12\x19\n\x0btexture_set\x18\x04 \x01(\tB\x04\xa0\xbb\x18\x01*I\n\x11IndexBufferFormat\x12\x19\n\x15INDEXBUFFER_FORMAT_16\x10\x00\x12\x19\n\x15INDEXBUFFER_FORMAT_32\x10\x01B\x1b\n\x14com.dynamo.rig.protoB\x03Rig'
    )
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'rig_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = b'\n\x14com.dynamo.rig.protoB\x03Rig'
    _BONE.fields_by_name['local']._options = None
    _BONE.fields_by_name['local']._serialized_options = b'\xa0\xb5\x18\x01'
    _BONE.fields_by_name['world']._options = None
    _BONE.fields_by_name['world']._serialized_options = b'\xa0\xb5\x18\x01'
    _BONE.fields_by_name['inverse_bind_pose']._options = None
    _BONE.fields_by_name['inverse_bind_pose'
        ]._serialized_options = b'\xa0\xb5\x18\x01'
    _BONE._options = None
    _BONE._serialized_options = b'\x98\xb5\x18\x01'
    _ANIMATIONINSTANCEDESC.fields_by_name['animation']._options = None
    _ANIMATIONINSTANCEDESC.fields_by_name['animation'
        ]._serialized_options = b'\xa0\xbb\x18\x01'
    _MODEL.fields_by_name['local']._options = None
    _MODEL.fields_by_name['local']._serialized_options = b'\xa0\xb5\x18\x01'
    _MODEL._options = None
    _MODEL._serialized_options = b'\x98\xb5\x18\x01'
    _RIGSCENE.fields_by_name['skeleton']._options = None
    _RIGSCENE.fields_by_name['skeleton'
        ]._serialized_options = b'\xa0\xbb\x18\x01'
    _RIGSCENE.fields_by_name['animation_set']._options = None
    _RIGSCENE.fields_by_name['animation_set'
        ]._serialized_options = b'\xa0\xbb\x18\x01'
    _RIGSCENE.fields_by_name['mesh_set']._options = None
    _RIGSCENE.fields_by_name['mesh_set'
        ]._serialized_options = b'\xa0\xbb\x18\x01'
    _RIGSCENE.fields_by_name['texture_set']._options = None
    _RIGSCENE.fields_by_name['texture_set'
        ]._serialized_options = b'\xa0\xbb\x18\x01'
    _INDEXBUFFERFORMAT._serialized_start = 1774
    _INDEXBUFFERFORMAT._serialized_end = 1847
    _BONE._serialized_start = 74
    _BONE._serialized_end = 279
    _IK._serialized_start = 281
    _IK._serialized_end = 384
    _SKELETON._serialized_start = 386
    _SKELETON._serialized_end = 454
    _ANIMATIONTRACK._serialized_start = 456
    _ANIMATIONTRACK._serialized_end = 542
    _EVENTKEY._serialized_start = 544
    _EVENTKEY._serialized_end = 622
    _EVENTTRACK._serialized_start = 624
    _EVENTTRACK._serialized_end = 688
    _RIGANIMATION._serialized_start = 691
    _RIGANIMATION._serialized_end = 842
    _ANIMATIONSET._serialized_start = 844
    _ANIMATIONSET._serialized_end = 902
    _ANIMATIONINSTANCEDESC._serialized_start = 904
    _ANIMATIONINSTANCEDESC._serialized_end = 952
    _ANIMATIONSETDESC._serialized_start = 954
    _ANIMATIONSETDESC._serialized_end = 1043
    _MESH._serialized_start = 1046
    _MESH._serialized_end = 1431
    _MODEL._serialized_start = 1433
    _MODEL._serialized_end = 1550
    _MESHSET._serialized_start = 1552
    _MESHSET._serialized_end = 1656
    _RIGSCENE._serialized_start = 1658
    _RIGSCENE._serialized_end = 1772

