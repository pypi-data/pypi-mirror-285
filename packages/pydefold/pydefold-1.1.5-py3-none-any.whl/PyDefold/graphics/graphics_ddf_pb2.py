"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from PyDefold.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from PyDefold.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x1bgraphics/graphics_ddf.proto\x12\ndmGraphics\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto"\x84\x01\n\x07Cubemap\x12\x13\n\x05right\x18\x01 \x02(\tB\x04\xa0\xbb\x18\x01\x12\x12\n\x04left\x18\x02 \x02(\tB\x04\xa0\xbb\x18\x01\x12\x11\n\x03top\x18\x03 \x02(\tB\x04\xa0\xbb\x18\x01\x12\x14\n\x06bottom\x18\x04 \x02(\tB\x04\xa0\xbb\x18\x01\x12\x13\n\x05front\x18\x05 \x02(\tB\x04\xa0\xbb\x18\x01\x12\x12\n\x04back\x18\x06 \x02(\tB\x04\xa0\xbb\x18\x01"\x9b\x07\n\x0fVertexAttribute\x12\x0c\n\x04name\x18\x01 \x02(\t\x12\x17\n\tname_hash\x18\x02 \x01(\x04B\x04\xa8\xbb\x18\x01\x12S\n\rsemantic_type\x18\x03 \x01(\x0e2(.dmGraphics.VertexAttribute.SemanticType:\x12SEMANTIC_TYPE_NONE\x12\x18\n\relement_count\x18\x04 \x01(\x05:\x010\x12\x18\n\tnormalize\x18\x05 \x01(\x08:\x05false\x12C\n\tdata_type\x18\x06 \x01(\x0e2$.dmGraphics.VertexAttribute.DataType:\nTYPE_FLOAT\x12M\n\x10coordinate_space\x18\x07 \x01(\x0e2\x1b.dmGraphics.CoordinateSpace:\x16COORDINATE_SPACE_LOCAL\x12=\n\x0blong_values\x18\x08 \x01(\x0b2&.dmGraphics.VertexAttribute.LongValuesH\x00\x12A\n\rdouble_values\x18\t \x01(\x0b2(.dmGraphics.VertexAttribute.DoubleValuesH\x00\x12\x1d\n\rbinary_values\x18\n \x01(\x0cB\x04\xa8\xbb\x18\x01H\x00\x1a\x1b\n\nLongValues\x12\r\n\x01v\x18\x01 \x03(\x03B\x02\x10\x01\x1a\x1d\n\x0cDoubleValues\x12\r\n\x01v\x18\x01 \x03(\x01B\x02\x10\x01"\x8f\x01\n\x08DataType\x12\r\n\tTYPE_BYTE\x10\x01\x12\x16\n\x12TYPE_UNSIGNED_BYTE\x10\x02\x12\x0e\n\nTYPE_SHORT\x10\x03\x12\x17\n\x13TYPE_UNSIGNED_SHORT\x10\x04\x12\x0c\n\x08TYPE_INT\x10\x05\x12\x15\n\x11TYPE_UNSIGNED_INT\x10\x06\x12\x0e\n\nTYPE_FLOAT\x10\x07"\xca\x01\n\x0cSemanticType\x12\x16\n\x12SEMANTIC_TYPE_NONE\x10\x01\x12\x1a\n\x16SEMANTIC_TYPE_POSITION\x10\x02\x12\x1a\n\x16SEMANTIC_TYPE_TEXCOORD\x10\x03\x12\x1c\n\x18SEMANTIC_TYPE_PAGE_INDEX\x10\x04\x12\x17\n\x13SEMANTIC_TYPE_COLOR\x10\x05\x12\x18\n\x14SEMANTIC_TYPE_NORMAL\x10\x06\x12\x19\n\x15SEMANTIC_TYPE_TANGENT\x10\x07B\x08\n\x06values"\xc9\x0c\n\x0cTextureImage\x124\n\x0calternatives\x18\x01 \x03(\x0b2\x1e.dmGraphics.TextureImage.Image\x12+\n\x04type\x18\x02 \x02(\x0e2\x1d.dmGraphics.TextureImage.Type\x12\r\n\x05count\x18\x03 \x02(\r\x12\x16\n\x0busage_flags\x18\x04 \x01(\r:\x011\x1a\xe5\x02\n\x05Image\x12\r\n\x05width\x18\x01 \x02(\r\x12\x0e\n\x06height\x18\x02 \x02(\r\x12\x16\n\x0eoriginal_width\x18\x03 \x02(\r\x12\x17\n\x0foriginal_height\x18\x04 \x02(\r\x126\n\x06format\x18\x05 \x02(\x0e2&.dmGraphics.TextureImage.TextureFormat\x12\x16\n\x0emip_map_offset\x18\x06 \x03(\r\x12\x14\n\x0cmip_map_size\x18\x07 \x03(\r\x12\x0c\n\x04data\x18\x08 \x02(\x0c\x12\\\n\x10compression_type\x18\t \x01(\x0e2(.dmGraphics.TextureImage.CompressionType:\x18COMPRESSION_TYPE_DEFAULT\x12\x19\n\x11compression_flags\x18\n \x01(\x04\x12\x1f\n\x17mip_map_size_compressed\x18\x0b \x03(\r"K\n\x04Type\x12\x0b\n\x07TYPE_2D\x10\x01\x12\x10\n\x0cTYPE_CUBEMAP\x10\x02\x12\x11\n\rTYPE_2D_ARRAY\x10\x03\x12\x11\n\rTYPE_2D_IMAGE\x10\x04"\xaf\x01\n\x0fCompressionType\x12\x1c\n\x18COMPRESSION_TYPE_DEFAULT\x10\x00\x12\x19\n\x15COMPRESSION_TYPE_WEBP\x10\x01\x12\x1f\n\x1bCOMPRESSION_TYPE_WEBP_LOSSY\x10\x02\x12 \n\x1cCOMPRESSION_TYPE_BASIS_UASTC\x10\x03\x12 \n\x1cCOMPRESSION_TYPE_BASIS_ETC1S\x10\x04"4\n\x10CompressionFlags\x12 \n\x1cCOMPRESSION_FLAG_ALPHA_CLEAN\x10\x01"\x91\x06\n\rTextureFormat\x12\x1c\n\x18TEXTURE_FORMAT_LUMINANCE\x10\x00\x12\x16\n\x12TEXTURE_FORMAT_RGB\x10\x01\x12\x17\n\x13TEXTURE_FORMAT_RGBA\x10\x02\x12#\n\x1fTEXTURE_FORMAT_RGB_PVRTC_2BPPV1\x10\x03\x12#\n\x1fTEXTURE_FORMAT_RGB_PVRTC_4BPPV1\x10\x04\x12$\n TEXTURE_FORMAT_RGBA_PVRTC_2BPPV1\x10\x05\x12$\n TEXTURE_FORMAT_RGBA_PVRTC_4BPPV1\x10\x06\x12\x1b\n\x17TEXTURE_FORMAT_RGB_ETC1\x10\x07\x12\x1c\n\x18TEXTURE_FORMAT_RGB_16BPP\x10\x08\x12\x1d\n\x19TEXTURE_FORMAT_RGBA_16BPP\x10\t\x12"\n\x1eTEXTURE_FORMAT_LUMINANCE_ALPHA\x10\n\x12\x1c\n\x18TEXTURE_FORMAT_RGBA_ETC2\x10\x0b\x12 \n\x1cTEXTURE_FORMAT_RGBA_ASTC_4x4\x10\x0c\x12\x1a\n\x16TEXTURE_FORMAT_RGB_BC1\x10\r\x12\x1b\n\x17TEXTURE_FORMAT_RGBA_BC3\x10\x0e\x12\x18\n\x14TEXTURE_FORMAT_R_BC4\x10\x0f\x12\x19\n\x15TEXTURE_FORMAT_RG_BC5\x10\x10\x12\x1b\n\x17TEXTURE_FORMAT_RGBA_BC7\x10\x11\x12\x19\n\x15TEXTURE_FORMAT_RGB16F\x10\x12\x12\x19\n\x15TEXTURE_FORMAT_RGB32F\x10\x13\x12\x1a\n\x16TEXTURE_FORMAT_RGBA16F\x10\x14\x12\x1a\n\x16TEXTURE_FORMAT_RGBA32F\x10\x15\x12\x17\n\x13TEXTURE_FORMAT_R16F\x10\x16\x12\x18\n\x14TEXTURE_FORMAT_RG16F\x10\x17\x12\x17\n\x13TEXTURE_FORMAT_R32F\x10\x18\x12\x18\n\x14TEXTURE_FORMAT_RG32F\x10\x19"\xc0\x02\n\x18TextureFormatAlternative\x126\n\x06format\x18\x01 \x02(\x0e2&.dmGraphics.TextureImage.TextureFormat\x12P\n\x11compression_level\x18\x02 \x02(\x0e25.dmGraphics.TextureFormatAlternative.CompressionLevel\x12\\\n\x10compression_type\x18\x03 \x01(\x0e2(.dmGraphics.TextureImage.CompressionType:\x18COMPRESSION_TYPE_DEFAULT"<\n\x10CompressionLevel\x12\x08\n\x04FAST\x10\x00\x12\n\n\x06NORMAL\x10\x01\x12\x08\n\x04HIGH\x10\x02\x12\x08\n\x04BEST\x10\x03"-\n\x0cPathSettings\x12\x0c\n\x04path\x18\x01 \x02(\t\x12\x0f\n\x07profile\x18\x02 \x02(\t"\xee\x02\n\x0fPlatformProfile\x12*\n\x02os\x18\x01 \x02(\x0e2\x1e.dmGraphics.PlatformProfile.OS\x125\n\x07formats\x18\x02 \x03(\x0b2$.dmGraphics.TextureFormatAlternative\x12\x0f\n\x07mipmaps\x18\x03 \x02(\x08\x12\x18\n\x10max_texture_size\x18\x04 \x01(\r\x12\x1f\n\x11premultiply_alpha\x18\x05 \x01(\x08:\x04true"\xab\x01\n\x02OS\x12\x11\n\rOS_ID_GENERIC\x10\x00\x12\x11\n\rOS_ID_WINDOWS\x10\x01\x12\r\n\tOS_ID_OSX\x10\x02\x12\x0f\n\x0bOS_ID_LINUX\x10\x03\x12\r\n\tOS_ID_IOS\x10\x04\x12\x11\n\rOS_ID_ANDROID\x10\x05\x12\r\n\tOS_ID_WEB\x10\x06\x12\x10\n\x0cOS_ID_SWITCH\x10\x07\x12\r\n\tOS_ID_PS4\x10\x08\x12\r\n\tOS_ID_PS5\x10\t"N\n\x0eTextureProfile\x12\x0c\n\x04name\x18\x01 \x02(\t\x12.\n\tplatforms\x18\x02 \x03(\x0b2\x1b.dmGraphics.PlatformProfile"p\n\x0fTextureProfiles\x12/\n\rpath_settings\x18\x01 \x03(\x0b2\x18.dmGraphics.PathSettings\x12,\n\x08profiles\x18\x02 \x03(\x0b2\x1a.dmGraphics.TextureProfile"\xfe\x0f\n\nShaderDesc\x12.\n\x07shaders\x18\x01 \x03(\x0b2\x1d.dmGraphics.ShaderDesc.Shader\x128\n\x0cshader_class\x18\x02 \x01(\x0e2".dmGraphics.ShaderDesc.ShaderClass\x1a\x82\x01\n\x0cResourceType\x12<\n\x0bshader_type\x18\x01 \x01(\x0e2%.dmGraphics.ShaderDesc.ShaderDataTypeH\x00\x12\x14\n\ntype_index\x18\x02 \x01(\x05H\x00\x12\x16\n\x0euse_type_index\x18\x03 \x01(\x08B\x06\n\x04Type\x1a\x8b\x01\n\x0eResourceMember\x12\x0c\n\x04name\x18\x01 \x02(\t\x12\x11\n\tname_hash\x18\x02 \x02(\x04\x121\n\x04type\x18\x03 \x02(\x0b2#.dmGraphics.ShaderDesc.ResourceType\x12\x15\n\relement_count\x18\x04 \x01(\r\x12\x0e\n\x06offset\x18\x05 \x01(\r\x1ak\n\x10ResourceTypeInfo\x12\x0c\n\x04name\x18\x01 \x02(\t\x12\x11\n\tname_hash\x18\x02 \x02(\x04\x126\n\x07members\x18\x03 \x03(\x0b2%.dmGraphics.ShaderDesc.ResourceMember\x1a\x97\x01\n\x0fResourceBinding\x12\x0c\n\x04name\x18\x01 \x02(\t\x12\x11\n\tname_hash\x18\x02 \x02(\x04\x121\n\x04type\x18\x03 \x02(\x0b2#.dmGraphics.ShaderDesc.ResourceType\x12\x0b\n\x03set\x18\x04 \x01(\r\x12\x0f\n\x07binding\x18\x05 \x01(\r\x12\x12\n\nblock_size\x18\x06 \x01(\r\x1a\xe4\x03\n\x06Shader\x121\n\x08language\x18\x01 \x02(\x0e2\x1f.dmGraphics.ShaderDesc.Language\x12\x0e\n\x06source\x18\x02 \x01(\x0c\x12\x0c\n\x04name\x18\x03 \x01(\t\x12?\n\x0funiform_buffers\x18\x04 \x03(\x0b2&.dmGraphics.ShaderDesc.ResourceBinding\x12?\n\x0fstorage_buffers\x18\x05 \x03(\x0b2&.dmGraphics.ShaderDesc.ResourceBinding\x128\n\x08textures\x18\x06 \x03(\x0b2&.dmGraphics.ShaderDesc.ResourceBinding\x126\n\x06inputs\x18\x07 \x03(\x0b2&.dmGraphics.ShaderDesc.ResourceBinding\x127\n\x07outputs\x18\x08 \x03(\x0b2&.dmGraphics.ShaderDesc.ResourceBinding\x126\n\x05types\x18\t \x03(\x0b2\'.dmGraphics.ShaderDesc.ResourceTypeInfo\x12$\n\x15variant_texture_array\x18\n \x01(\x08:\x05false"\xae\x01\n\x08Language\x12\x17\n\x13LANGUAGE_GLSL_SM120\x10\x01\x12\x17\n\x13LANGUAGE_GLSL_SM140\x10\x02\x12\x17\n\x13LANGUAGE_GLES_SM100\x10\x03\x12\x17\n\x13LANGUAGE_GLES_SM300\x10\x04\x12\x12\n\x0eLANGUAGE_SPIRV\x10\x05\x12\x11\n\rLANGUAGE_PSSL\x10\x06\x12\x17\n\x13LANGUAGE_GLSL_SM430\x10\x07"B\n\x0bShaderClass\x12\x19\n\x15SHADER_CLASS_GRAPHICS\x10\x00\x12\x18\n\x14SHADER_CLASS_COMPUTE\x10\x01"\x8f\x05\n\x0eShaderDataType\x12\x17\n\x13SHADER_TYPE_UNKNOWN\x10\x00\x12\x13\n\x0fSHADER_TYPE_INT\x10\x01\x12\x14\n\x10SHADER_TYPE_UINT\x10\x02\x12\x15\n\x11SHADER_TYPE_FLOAT\x10\x03\x12\x14\n\x10SHADER_TYPE_VEC2\x10\x04\x12\x14\n\x10SHADER_TYPE_VEC3\x10\x05\x12\x14\n\x10SHADER_TYPE_VEC4\x10\x06\x12\x14\n\x10SHADER_TYPE_MAT2\x10\x07\x12\x14\n\x10SHADER_TYPE_MAT3\x10\x08\x12\x14\n\x10SHADER_TYPE_MAT4\x10\t\x12\x19\n\x15SHADER_TYPE_SAMPLER2D\x10\n\x12\x19\n\x15SHADER_TYPE_SAMPLER3D\x10\x0b\x12\x1c\n\x18SHADER_TYPE_SAMPLER_CUBE\x10\x0c\x12\x1f\n\x1bSHADER_TYPE_SAMPLER2D_ARRAY\x10\r\x12\x1e\n\x1aSHADER_TYPE_UNIFORM_BUFFER\x10\x0e\x12\x15\n\x11SHADER_TYPE_UVEC2\x10\x0f\x12\x15\n\x11SHADER_TYPE_UVEC3\x10\x10\x12\x15\n\x11SHADER_TYPE_UVEC4\x10\x11\x12\x19\n\x15SHADER_TYPE_TEXTURE2D\x10\x12\x12\x1a\n\x16SHADER_TYPE_UTEXTURE2D\x10\x13\x12!\n\x1dSHADER_TYPE_RENDER_PASS_INPUT\x10\x14\x12\x18\n\x14SHADER_TYPE_UIMAGE2D\x10\x15\x12\x17\n\x13SHADER_TYPE_IMAGE2D\x10\x16\x12\x17\n\x13SHADER_TYPE_SAMPLER\x10\x17\x12\x1e\n\x1aSHADER_TYPE_STORAGE_BUFFER\x10\x18*I\n\x0fCoordinateSpace\x12\x1a\n\x16COORDINATE_SPACE_WORLD\x10\x01\x12\x1a\n\x16COORDINATE_SPACE_LOCAL\x10\x02*\xba\x01\n\x12DepthStencilFormat\x12\x1d\n\x19DEPTH_STENCIL_FORMAT_D32F\x10\x01\x12!\n\x1dDEPTH_STENCIL_FORMAT_D32F_S8U\x10\x02\x12!\n\x1dDEPTH_STENCIL_FORMAT_D16U_S8U\x10\x03\x12!\n\x1dDEPTH_STENCIL_FORMAT_D24U_S8U\x10\x04\x12\x1c\n\x18DEPTH_STENCIL_FORMAT_S8U\x10\x05*t\n\x10TextureUsageFlag\x12\x1d\n\x19TEXTURE_USAGE_FLAG_SAMPLE\x10\x01\x12!\n\x1dTEXTURE_USAGE_FLAG_MEMORYLESS\x10\x02\x12\x1e\n\x1aTEXTURE_USAGE_FLAG_STORAGE\x10\x04B%\n\x19com.dynamo.graphics.protoB\x08Graphics'
    )
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR,
    'graphics.graphics_ddf_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = (
        b'\n\x19com.dynamo.graphics.protoB\x08Graphics')
    _CUBEMAP.fields_by_name['right']._options = None
    _CUBEMAP.fields_by_name['right']._serialized_options = b'\xa0\xbb\x18\x01'
    _CUBEMAP.fields_by_name['left']._options = None
    _CUBEMAP.fields_by_name['left']._serialized_options = b'\xa0\xbb\x18\x01'
    _CUBEMAP.fields_by_name['top']._options = None
    _CUBEMAP.fields_by_name['top']._serialized_options = b'\xa0\xbb\x18\x01'
    _CUBEMAP.fields_by_name['bottom']._options = None
    _CUBEMAP.fields_by_name['bottom']._serialized_options = b'\xa0\xbb\x18\x01'
    _CUBEMAP.fields_by_name['front']._options = None
    _CUBEMAP.fields_by_name['front']._serialized_options = b'\xa0\xbb\x18\x01'
    _CUBEMAP.fields_by_name['back']._options = None
    _CUBEMAP.fields_by_name['back']._serialized_options = b'\xa0\xbb\x18\x01'
    _VERTEXATTRIBUTE_LONGVALUES.fields_by_name['v']._options = None
    _VERTEXATTRIBUTE_LONGVALUES.fields_by_name['v'
        ]._serialized_options = b'\x10\x01'
    _VERTEXATTRIBUTE_DOUBLEVALUES.fields_by_name['v']._options = None
    _VERTEXATTRIBUTE_DOUBLEVALUES.fields_by_name['v'
        ]._serialized_options = b'\x10\x01'
    _VERTEXATTRIBUTE.fields_by_name['name_hash']._options = None
    _VERTEXATTRIBUTE.fields_by_name['name_hash'
        ]._serialized_options = b'\xa8\xbb\x18\x01'
    _VERTEXATTRIBUTE.fields_by_name['binary_values']._options = None
    _VERTEXATTRIBUTE.fields_by_name['binary_values'
        ]._serialized_options = b'\xa8\xbb\x18\x01'
    _COORDINATESPACE._serialized_start = 5744
    _COORDINATESPACE._serialized_end = 5817
    _DEPTHSTENCILFORMAT._serialized_start = 5820
    _DEPTHSTENCILFORMAT._serialized_end = 6006
    _TEXTUREUSAGEFLAG._serialized_start = 6008
    _TEXTUREUSAGEFLAG._serialized_end = 6124
    _CUBEMAP._serialized_start = 90
    _CUBEMAP._serialized_end = 222
    _VERTEXATTRIBUTE._serialized_start = 225
    _VERTEXATTRIBUTE._serialized_end = 1148
    _VERTEXATTRIBUTE_LONGVALUES._serialized_start = 729
    _VERTEXATTRIBUTE_LONGVALUES._serialized_end = 756
    _VERTEXATTRIBUTE_DOUBLEVALUES._serialized_start = 758
    _VERTEXATTRIBUTE_DOUBLEVALUES._serialized_end = 787
    _VERTEXATTRIBUTE_DATATYPE._serialized_start = 790
    _VERTEXATTRIBUTE_DATATYPE._serialized_end = 933
    _VERTEXATTRIBUTE_SEMANTICTYPE._serialized_start = 936
    _VERTEXATTRIBUTE_SEMANTICTYPE._serialized_end = 1138
    _TEXTUREIMAGE._serialized_start = 1151
    _TEXTUREIMAGE._serialized_end = 2760
    _TEXTUREIMAGE_IMAGE._serialized_start = 1306
    _TEXTUREIMAGE_IMAGE._serialized_end = 1663
    _TEXTUREIMAGE_TYPE._serialized_start = 1665
    _TEXTUREIMAGE_TYPE._serialized_end = 1740
    _TEXTUREIMAGE_COMPRESSIONTYPE._serialized_start = 1743
    _TEXTUREIMAGE_COMPRESSIONTYPE._serialized_end = 1918
    _TEXTUREIMAGE_COMPRESSIONFLAGS._serialized_start = 1920
    _TEXTUREIMAGE_COMPRESSIONFLAGS._serialized_end = 1972
    _TEXTUREIMAGE_TEXTUREFORMAT._serialized_start = 1975
    _TEXTUREIMAGE_TEXTUREFORMAT._serialized_end = 2760
    _TEXTUREFORMATALTERNATIVE._serialized_start = 2763
    _TEXTUREFORMATALTERNATIVE._serialized_end = 3083
    _TEXTUREFORMATALTERNATIVE_COMPRESSIONLEVEL._serialized_start = 3023
    _TEXTUREFORMATALTERNATIVE_COMPRESSIONLEVEL._serialized_end = 3083
    _PATHSETTINGS._serialized_start = 3085
    _PATHSETTINGS._serialized_end = 3130
    _PLATFORMPROFILE._serialized_start = 3133
    _PLATFORMPROFILE._serialized_end = 3499
    _PLATFORMPROFILE_OS._serialized_start = 3328
    _PLATFORMPROFILE_OS._serialized_end = 3499
    _TEXTUREPROFILE._serialized_start = 3501
    _TEXTUREPROFILE._serialized_end = 3579
    _TEXTUREPROFILES._serialized_start = 3581
    _TEXTUREPROFILES._serialized_end = 3693
    _SHADERDESC._serialized_start = 3696
    _SHADERDESC._serialized_end = 5742
    _SHADERDESC_RESOURCETYPE._serialized_start = 3817
    _SHADERDESC_RESOURCETYPE._serialized_end = 3947
    _SHADERDESC_RESOURCEMEMBER._serialized_start = 3950
    _SHADERDESC_RESOURCEMEMBER._serialized_end = 4089
    _SHADERDESC_RESOURCETYPEINFO._serialized_start = 4091
    _SHADERDESC_RESOURCETYPEINFO._serialized_end = 4198
    _SHADERDESC_RESOURCEBINDING._serialized_start = 4201
    _SHADERDESC_RESOURCEBINDING._serialized_end = 4352
    _SHADERDESC_SHADER._serialized_start = 4355
    _SHADERDESC_SHADER._serialized_end = 4839
    _SHADERDESC_LANGUAGE._serialized_start = 4842
    _SHADERDESC_LANGUAGE._serialized_end = 5016
    _SHADERDESC_SHADERCLASS._serialized_start = 5018
    _SHADERDESC_SHADERCLASS._serialized_end = 5084
    _SHADERDESC_SHADERDATATYPE._serialized_start = 5087
    _SHADERDESC_SHADERDATATYPE._serialized_end = 5742

