"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from PyDefold.ddf import ddf_extensions_pb2 as ddf_dot_ddf__extensions__pb2
from PyDefold.ddf import ddf_math_pb2 as ddf_dot_ddf__math__pb2
from PyDefold.graphics import graphics_ddf_pb2 as graphics_dot_graphics__ddf__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x12particle_ddf.proto\x12\rdmParticleDDF\x1a\x18ddf/ddf_extensions.proto\x1a\x12ddf/ddf_math.proto\x1a\x1bgraphics/graphics_ddf.proto"=\n\x0bSplinePoint\x12\t\n\x01x\x18\x01 \x02(\x02\x12\t\n\x01y\x18\x02 \x02(\x02\x12\x0b\n\x03t_x\x18\x03 \x02(\x02\x12\x0b\n\x03t_y\x18\x04 \x02(\x02"\xbb\x02\n\x08Modifier\x12)\n\x04type\x18\x01 \x02(\x0e2\x1b.dmParticleDDF.ModifierType\x12\x18\n\ruse_direction\x18\x02 \x01(\r:\x010\x12 \n\x08position\x18\x03 \x01(\x0b2\x0e.dmMath.Point3\x12\x1e\n\x08rotation\x18\x04 \x01(\x0b2\x0c.dmMath.Quat\x124\n\nproperties\x18\x05 \x03(\x0b2 .dmParticleDDF.Modifier.Property\x1ar\n\x08Property\x12\'\n\x03key\x18\x01 \x02(\x0e2\x1a.dmParticleDDF.ModifierKey\x12*\n\x06points\x18\x02 \x03(\x0b2\x1a.dmParticleDDF.SplinePoint\x12\x11\n\x06spread\x18\x03 \x01(\x02:\x010"\xb5\t\n\x07Emitter\x12\x13\n\x02id\x18\x01 \x01(\t:\x07emitter\x12%\n\x04mode\x18\x02 \x02(\x0e2\x17.dmParticleDDF.PlayMode\x12\x13\n\x08duration\x18\x03 \x01(\x02:\x010\x12+\n\x05space\x18\x04 \x02(\x0e2\x1c.dmParticleDDF.EmissionSpace\x12 \n\x08position\x18\x05 \x02(\x0b2\x0e.dmMath.Point3\x12\x1e\n\x08rotation\x18\x06 \x02(\x0b2\x0c.dmMath.Quat\x12\x19\n\x0btile_source\x18\x07 \x02(\tB\x04\xa0\xbb\x18\x01\x12\x11\n\tanimation\x18\x08 \x02(\t\x12\x16\n\x08material\x18\t \x02(\tB\x04\xa0\xbb\x18\x01\x12>\n\nblend_mode\x18\n \x01(\x0e2\x18.dmParticleDDF.BlendMode:\x10BLEND_MODE_ALPHA\x12^\n\x14particle_orientation\x18\x0b \x01(\x0e2".dmParticleDDF.ParticleOrientation:\x1cPARTICLE_ORIENTATION_DEFAULT\x12\x1b\n\x10inherit_velocity\x18\x0c \x01(\x02:\x010\x12\x1a\n\x12max_particle_count\x18\r \x02(\r\x12(\n\x04type\x18\x0e \x02(\x0e2\x1a.dmParticleDDF.EmitterType\x12\x16\n\x0bstart_delay\x18\x0f \x01(\x02:\x010\x123\n\nproperties\x18\x10 \x03(\x0b2\x1f.dmParticleDDF.Emitter.Property\x12D\n\x13particle_properties\x18\x11 \x03(\x0b2\'.dmParticleDDF.Emitter.ParticleProperty\x12*\n\tmodifiers\x18\x12 \x03(\x0b2\x17.dmParticleDDF.Modifier\x12<\n\tsize_mode\x18\x13 \x01(\x0e2\x17.dmParticleDDF.SizeMode:\x10SIZE_MODE_MANUAL\x12\x1d\n\x12start_delay_spread\x18\x14 \x01(\x02:\x010\x12\x1a\n\x0fduration_spread\x18\x15 \x01(\x02:\x010\x12$\n\x15stretch_with_velocity\x18\x16 \x01(\x08:\x05false\x12\x17\n\x0cstart_offset\x18\x17 \x01(\x02:\x010\x12\x1d\n\x05pivot\x18\x18 \x01(\x0b2\x0e.dmMath.Point3\x12/\n\nattributes\x18\x19 \x03(\x0b2\x1b.dmGraphics.VertexAttribute\x1aq\n\x08Property\x12&\n\x03key\x18\x01 \x02(\x0e2\x19.dmParticleDDF.EmitterKey\x12*\n\x06points\x18\x02 \x03(\x0b2\x1a.dmParticleDDF.SplinePoint\x12\x11\n\x06spread\x18\x03 \x01(\x02:\x010\x1ag\n\x10ParticleProperty\x12\'\n\x03key\x18\x01 \x02(\x0e2\x1a.dmParticleDDF.ParticleKey\x12*\n\x06points\x18\x02 \x03(\x0b2\x1a.dmParticleDDF.SplinePoint"b\n\nParticleFX\x12(\n\x08emitters\x18\x01 \x03(\x0b2\x16.dmParticleDDF.Emitter\x12*\n\tmodifiers\x18\x02 \x03(\x0b2\x17.dmParticleDDF.Modifier*\xbd\x01\n\x0bEmitterType\x12#\n\x13EMITTER_TYPE_CIRCLE\x10\x00\x1a\n\xc2\xc1\x18\x06Circle\x12$\n\x13EMITTER_TYPE_2DCONE\x10\x01\x1a\x0b\xc2\xc1\x18\x072D Cone\x12\x1d\n\x10EMITTER_TYPE_BOX\x10\x02\x1a\x07\xc2\xc1\x18\x03Box\x12#\n\x13EMITTER_TYPE_SPHERE\x10\x03\x1a\n\xc2\xc1\x18\x06Sphere\x12\x1f\n\x11EMITTER_TYPE_CONE\x10\x04\x1a\x08\xc2\xc1\x18\x04Cone*F\n\x08PlayMode\x12\x1c\n\x0ePLAY_MODE_ONCE\x10\x00\x1a\x08\xc2\xc1\x18\x04Once\x12\x1c\n\x0ePLAY_MODE_LOOP\x10\x01\x1a\x08\xc2\xc1\x18\x04Loop*]\n\rEmissionSpace\x12#\n\x14EMISSION_SPACE_WORLD\x10\x00\x1a\t\xc2\xc1\x18\x05World\x12\'\n\x16EMISSION_SPACE_EMITTER\x10\x01\x1a\x0b\xc2\xc1\x18\x07Emitter*\xbf\x06\n\nEmitterKey\x12*\n\x16EMITTER_KEY_SPAWN_RATE\x10\x00\x1a\x0e\xc2\xc1\x18\nSpawn Rate\x12*\n\x12EMITTER_KEY_SIZE_X\x10\x01\x1a\x12\xc2\xc1\x18\x0eEmitter Size X\x12*\n\x12EMITTER_KEY_SIZE_Y\x10\x02\x1a\x12\xc2\xc1\x18\x0eEmitter Size Y\x12*\n\x12EMITTER_KEY_SIZE_Z\x10\x03\x1a\x12\xc2\xc1\x18\x0eEmitter Size Z\x12:\n\x1eEMITTER_KEY_PARTICLE_LIFE_TIME\x10\x04\x1a\x16\xc2\xc1\x18\x12Particle Life Time\x121\n\x1aEMITTER_KEY_PARTICLE_SPEED\x10\x05\x1a\x11\xc2\xc1\x18\rInitial Speed\x12/\n\x19EMITTER_KEY_PARTICLE_SIZE\x10\x06\x1a\x10\xc2\xc1\x18\x0cInitial Size\x12-\n\x18EMITTER_KEY_PARTICLE_RED\x10\x07\x1a\x0f\xc2\xc1\x18\x0bInitial Red\x121\n\x1aEMITTER_KEY_PARTICLE_GREEN\x10\x08\x1a\x11\xc2\xc1\x18\rInitial Green\x12/\n\x19EMITTER_KEY_PARTICLE_BLUE\x10\t\x1a\x10\xc2\xc1\x18\x0cInitial Blue\x121\n\x1aEMITTER_KEY_PARTICLE_ALPHA\x10\n\x1a\x11\xc2\xc1\x18\rInitial Alpha\x127\n\x1dEMITTER_KEY_PARTICLE_ROTATION\x10\x0b\x1a\x14\xc2\xc1\x18\x10Initial Rotation\x12@\n%EMITTER_KEY_PARTICLE_STRETCH_FACTOR_X\x10\x0c\x1a\x15\xc2\xc1\x18\x11Initial Stretch X\x12@\n%EMITTER_KEY_PARTICLE_STRETCH_FACTOR_Y\x10\r\x1a\x15\xc2\xc1\x18\x11Initial Stretch Y\x12G\n%EMITTER_KEY_PARTICLE_ANGULAR_VELOCITY\x10\x0e\x1a\x1c\xc2\xc1\x18\x18Initial Angular Velocity\x12\x15\n\x11EMITTER_KEY_COUNT\x10\x0f*\xc1\x03\n\x0bParticleKey\x12&\n\x12PARTICLE_KEY_SCALE\x10\x00\x1a\x0e\xc2\xc1\x18\nLife Scale\x12"\n\x10PARTICLE_KEY_RED\x10\x01\x1a\x0c\xc2\xc1\x18\x08Life Red\x12&\n\x12PARTICLE_KEY_GREEN\x10\x02\x1a\x0e\xc2\xc1\x18\nLife Green\x12$\n\x11PARTICLE_KEY_BLUE\x10\x03\x1a\r\xc2\xc1\x18\tLife Blue\x12&\n\x12PARTICLE_KEY_ALPHA\x10\x04\x1a\x0e\xc2\xc1\x18\nLife Alpha\x12,\n\x15PARTICLE_KEY_ROTATION\x10\x05\x1a\x11\xc2\xc1\x18\rLife Rotation\x125\n\x1dPARTICLE_KEY_STRETCH_FACTOR_X\x10\x06\x1a\x12\xc2\xc1\x18\x0eLife Stretch X\x125\n\x1dPARTICLE_KEY_STRETCH_FACTOR_Y\x10\x07\x1a\x12\xc2\xc1\x18\x0eLife Stretch Y\x12<\n\x1dPARTICLE_KEY_ANGULAR_VELOCITY\x10\x08\x1a\x19\xc2\xc1\x18\x15Life Angular Velocity\x12\x16\n\x12PARTICLE_KEY_COUNT\x10\t*\xae\x01\n\x0cModifierType\x120\n\x1aMODIFIER_TYPE_ACCELERATION\x10\x00\x1a\x10\xc2\xc1\x18\x0cAcceleration\x12 \n\x12MODIFIER_TYPE_DRAG\x10\x01\x1a\x08\xc2\xc1\x18\x04Drag\x12$\n\x14MODIFIER_TYPE_RADIAL\x10\x02\x1a\n\xc2\xc1\x18\x06Radial\x12$\n\x14MODIFIER_TYPE_VORTEX\x10\x03\x1a\n\xc2\xc1\x18\x06Vortex*\x81\x01\n\x0bModifierKey\x12)\n\x16MODIFIER_KEY_MAGNITUDE\x10\x00\x1a\r\xc2\xc1\x18\tMagnitude\x12/\n\x19MODIFIER_KEY_MAX_DISTANCE\x10\x01\x1a\x10\xc2\xc1\x18\x0cMax Distance\x12\x16\n\x12MODIFIER_KEY_COUNT\x10\x02*\xc5\x01\n\tBlendMode\x12\x1f\n\x10BLEND_MODE_ALPHA\x10\x00\x1a\t\xc2\xc1\x18\x05Alpha\x12\x1b\n\x0eBLEND_MODE_ADD\x10\x01\x1a\x07\xc2\xc1\x18\x03Add\x124\n\x14BLEND_MODE_ADD_ALPHA\x10\x02\x1a\x1a\xc2\xc1\x18\x16Add Alpha (Deprecated)\x12!\n\x0fBLEND_MODE_MULT\x10\x03\x1a\x0c\xc2\xc1\x18\x08Multiply\x12!\n\x11BLEND_MODE_SCREEN\x10\x04\x1a\n\xc2\xc1\x18\x06Screen*J\n\x08SizeMode\x12 \n\x10SIZE_MODE_MANUAL\x10\x00\x1a\n\xc2\xc1\x18\x06Manual\x12\x1c\n\x0eSIZE_MODE_AUTO\x10\x01\x1a\x08\xc2\xc1\x18\x04Auto*\x8d\x02\n\x13ParticleOrientation\x12-\n\x1cPARTICLE_ORIENTATION_DEFAULT\x10\x00\x1a\x0b\xc2\xc1\x18\x07Default\x12A\n&PARTICLE_ORIENTATION_INITIAL_DIRECTION\x10\x01\x1a\x15\xc2\xc1\x18\x11Initial Direction\x12C\n\'PARTICLE_ORIENTATION_MOVEMENT_DIRECTION\x10\x02\x1a\x16\xc2\xc1\x18\x12Movement direction\x12?\n%PARTICLE_ORIENTATION_ANGULAR_VELOCITY\x10\x03\x1a\x14\xc2\xc1\x18\x10Angular VelocityB%\n\x19com.dynamo.particle.protoB\x08Particle'
    )
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'particle_ddf_pb2',
    globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    DESCRIPTOR._serialized_options = (
        b'\n\x19com.dynamo.particle.protoB\x08Particle')
    _EMITTERTYPE.values_by_name['EMITTER_TYPE_CIRCLE']._options = None
    _EMITTERTYPE.values_by_name['EMITTER_TYPE_CIRCLE'
        ]._serialized_options = b'\xc2\xc1\x18\x06Circle'
    _EMITTERTYPE.values_by_name['EMITTER_TYPE_2DCONE']._options = None
    _EMITTERTYPE.values_by_name['EMITTER_TYPE_2DCONE'
        ]._serialized_options = b'\xc2\xc1\x18\x072D Cone'
    _EMITTERTYPE.values_by_name['EMITTER_TYPE_BOX']._options = None
    _EMITTERTYPE.values_by_name['EMITTER_TYPE_BOX'
        ]._serialized_options = b'\xc2\xc1\x18\x03Box'
    _EMITTERTYPE.values_by_name['EMITTER_TYPE_SPHERE']._options = None
    _EMITTERTYPE.values_by_name['EMITTER_TYPE_SPHERE'
        ]._serialized_options = b'\xc2\xc1\x18\x06Sphere'
    _EMITTERTYPE.values_by_name['EMITTER_TYPE_CONE']._options = None
    _EMITTERTYPE.values_by_name['EMITTER_TYPE_CONE'
        ]._serialized_options = b'\xc2\xc1\x18\x04Cone'
    _PLAYMODE.values_by_name['PLAY_MODE_ONCE']._options = None
    _PLAYMODE.values_by_name['PLAY_MODE_ONCE'
        ]._serialized_options = b'\xc2\xc1\x18\x04Once'
    _PLAYMODE.values_by_name['PLAY_MODE_LOOP']._options = None
    _PLAYMODE.values_by_name['PLAY_MODE_LOOP'
        ]._serialized_options = b'\xc2\xc1\x18\x04Loop'
    _EMISSIONSPACE.values_by_name['EMISSION_SPACE_WORLD']._options = None
    _EMISSIONSPACE.values_by_name['EMISSION_SPACE_WORLD'
        ]._serialized_options = b'\xc2\xc1\x18\x05World'
    _EMISSIONSPACE.values_by_name['EMISSION_SPACE_EMITTER']._options = None
    _EMISSIONSPACE.values_by_name['EMISSION_SPACE_EMITTER'
        ]._serialized_options = b'\xc2\xc1\x18\x07Emitter'
    _EMITTERKEY.values_by_name['EMITTER_KEY_SPAWN_RATE']._options = None
    _EMITTERKEY.values_by_name['EMITTER_KEY_SPAWN_RATE'
        ]._serialized_options = b'\xc2\xc1\x18\nSpawn Rate'
    _EMITTERKEY.values_by_name['EMITTER_KEY_SIZE_X']._options = None
    _EMITTERKEY.values_by_name['EMITTER_KEY_SIZE_X'
        ]._serialized_options = b'\xc2\xc1\x18\x0eEmitter Size X'
    _EMITTERKEY.values_by_name['EMITTER_KEY_SIZE_Y']._options = None
    _EMITTERKEY.values_by_name['EMITTER_KEY_SIZE_Y'
        ]._serialized_options = b'\xc2\xc1\x18\x0eEmitter Size Y'
    _EMITTERKEY.values_by_name['EMITTER_KEY_SIZE_Z']._options = None
    _EMITTERKEY.values_by_name['EMITTER_KEY_SIZE_Z'
        ]._serialized_options = b'\xc2\xc1\x18\x0eEmitter Size Z'
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_LIFE_TIME'
        ]._options = None
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_LIFE_TIME'
        ]._serialized_options = b'\xc2\xc1\x18\x12Particle Life Time'
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_SPEED']._options = None
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_SPEED'
        ]._serialized_options = b'\xc2\xc1\x18\rInitial Speed'
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_SIZE']._options = None
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_SIZE'
        ]._serialized_options = b'\xc2\xc1\x18\x0cInitial Size'
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_RED']._options = None
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_RED'
        ]._serialized_options = b'\xc2\xc1\x18\x0bInitial Red'
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_GREEN']._options = None
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_GREEN'
        ]._serialized_options = b'\xc2\xc1\x18\rInitial Green'
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_BLUE']._options = None
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_BLUE'
        ]._serialized_options = b'\xc2\xc1\x18\x0cInitial Blue'
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_ALPHA']._options = None
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_ALPHA'
        ]._serialized_options = b'\xc2\xc1\x18\rInitial Alpha'
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_ROTATION']._options = None
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_ROTATION'
        ]._serialized_options = b'\xc2\xc1\x18\x10Initial Rotation'
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_STRETCH_FACTOR_X'
        ]._options = None
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_STRETCH_FACTOR_X'
        ]._serialized_options = b'\xc2\xc1\x18\x11Initial Stretch X'
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_STRETCH_FACTOR_Y'
        ]._options = None
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_STRETCH_FACTOR_Y'
        ]._serialized_options = b'\xc2\xc1\x18\x11Initial Stretch Y'
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_ANGULAR_VELOCITY'
        ]._options = None
    _EMITTERKEY.values_by_name['EMITTER_KEY_PARTICLE_ANGULAR_VELOCITY'
        ]._serialized_options = b'\xc2\xc1\x18\x18Initial Angular Velocity'
    _PARTICLEKEY.values_by_name['PARTICLE_KEY_SCALE']._options = None
    _PARTICLEKEY.values_by_name['PARTICLE_KEY_SCALE'
        ]._serialized_options = b'\xc2\xc1\x18\nLife Scale'
    _PARTICLEKEY.values_by_name['PARTICLE_KEY_RED']._options = None
    _PARTICLEKEY.values_by_name['PARTICLE_KEY_RED'
        ]._serialized_options = b'\xc2\xc1\x18\x08Life Red'
    _PARTICLEKEY.values_by_name['PARTICLE_KEY_GREEN']._options = None
    _PARTICLEKEY.values_by_name['PARTICLE_KEY_GREEN'
        ]._serialized_options = b'\xc2\xc1\x18\nLife Green'
    _PARTICLEKEY.values_by_name['PARTICLE_KEY_BLUE']._options = None
    _PARTICLEKEY.values_by_name['PARTICLE_KEY_BLUE'
        ]._serialized_options = b'\xc2\xc1\x18\tLife Blue'
    _PARTICLEKEY.values_by_name['PARTICLE_KEY_ALPHA']._options = None
    _PARTICLEKEY.values_by_name['PARTICLE_KEY_ALPHA'
        ]._serialized_options = b'\xc2\xc1\x18\nLife Alpha'
    _PARTICLEKEY.values_by_name['PARTICLE_KEY_ROTATION']._options = None
    _PARTICLEKEY.values_by_name['PARTICLE_KEY_ROTATION'
        ]._serialized_options = b'\xc2\xc1\x18\rLife Rotation'
    _PARTICLEKEY.values_by_name['PARTICLE_KEY_STRETCH_FACTOR_X'
        ]._options = None
    _PARTICLEKEY.values_by_name['PARTICLE_KEY_STRETCH_FACTOR_X'
        ]._serialized_options = b'\xc2\xc1\x18\x0eLife Stretch X'
    _PARTICLEKEY.values_by_name['PARTICLE_KEY_STRETCH_FACTOR_Y'
        ]._options = None
    _PARTICLEKEY.values_by_name['PARTICLE_KEY_STRETCH_FACTOR_Y'
        ]._serialized_options = b'\xc2\xc1\x18\x0eLife Stretch Y'
    _PARTICLEKEY.values_by_name['PARTICLE_KEY_ANGULAR_VELOCITY'
        ]._options = None
    _PARTICLEKEY.values_by_name['PARTICLE_KEY_ANGULAR_VELOCITY'
        ]._serialized_options = b'\xc2\xc1\x18\x15Life Angular Velocity'
    _MODIFIERTYPE.values_by_name['MODIFIER_TYPE_ACCELERATION']._options = None
    _MODIFIERTYPE.values_by_name['MODIFIER_TYPE_ACCELERATION'
        ]._serialized_options = b'\xc2\xc1\x18\x0cAcceleration'
    _MODIFIERTYPE.values_by_name['MODIFIER_TYPE_DRAG']._options = None
    _MODIFIERTYPE.values_by_name['MODIFIER_TYPE_DRAG'
        ]._serialized_options = b'\xc2\xc1\x18\x04Drag'
    _MODIFIERTYPE.values_by_name['MODIFIER_TYPE_RADIAL']._options = None
    _MODIFIERTYPE.values_by_name['MODIFIER_TYPE_RADIAL'
        ]._serialized_options = b'\xc2\xc1\x18\x06Radial'
    _MODIFIERTYPE.values_by_name['MODIFIER_TYPE_VORTEX']._options = None
    _MODIFIERTYPE.values_by_name['MODIFIER_TYPE_VORTEX'
        ]._serialized_options = b'\xc2\xc1\x18\x06Vortex'
    _MODIFIERKEY.values_by_name['MODIFIER_KEY_MAGNITUDE']._options = None
    _MODIFIERKEY.values_by_name['MODIFIER_KEY_MAGNITUDE'
        ]._serialized_options = b'\xc2\xc1\x18\tMagnitude'
    _MODIFIERKEY.values_by_name['MODIFIER_KEY_MAX_DISTANCE']._options = None
    _MODIFIERKEY.values_by_name['MODIFIER_KEY_MAX_DISTANCE'
        ]._serialized_options = b'\xc2\xc1\x18\x0cMax Distance'
    _BLENDMODE.values_by_name['BLEND_MODE_ALPHA']._options = None
    _BLENDMODE.values_by_name['BLEND_MODE_ALPHA'
        ]._serialized_options = b'\xc2\xc1\x18\x05Alpha'
    _BLENDMODE.values_by_name['BLEND_MODE_ADD']._options = None
    _BLENDMODE.values_by_name['BLEND_MODE_ADD'
        ]._serialized_options = b'\xc2\xc1\x18\x03Add'
    _BLENDMODE.values_by_name['BLEND_MODE_ADD_ALPHA']._options = None
    _BLENDMODE.values_by_name['BLEND_MODE_ADD_ALPHA'
        ]._serialized_options = b'\xc2\xc1\x18\x16Add Alpha (Deprecated)'
    _BLENDMODE.values_by_name['BLEND_MODE_MULT']._options = None
    _BLENDMODE.values_by_name['BLEND_MODE_MULT'
        ]._serialized_options = b'\xc2\xc1\x18\x08Multiply'
    _BLENDMODE.values_by_name['BLEND_MODE_SCREEN']._options = None
    _BLENDMODE.values_by_name['BLEND_MODE_SCREEN'
        ]._serialized_options = b'\xc2\xc1\x18\x06Screen'
    _SIZEMODE.values_by_name['SIZE_MODE_MANUAL']._options = None
    _SIZEMODE.values_by_name['SIZE_MODE_MANUAL'
        ]._serialized_options = b'\xc2\xc1\x18\x06Manual'
    _SIZEMODE.values_by_name['SIZE_MODE_AUTO']._options = None
    _SIZEMODE.values_by_name['SIZE_MODE_AUTO'
        ]._serialized_options = b'\xc2\xc1\x18\x04Auto'
    _PARTICLEORIENTATION.values_by_name['PARTICLE_ORIENTATION_DEFAULT'
        ]._options = None
    _PARTICLEORIENTATION.values_by_name['PARTICLE_ORIENTATION_DEFAULT'
        ]._serialized_options = b'\xc2\xc1\x18\x07Default'
    _PARTICLEORIENTATION.values_by_name[
        'PARTICLE_ORIENTATION_INITIAL_DIRECTION']._options = None
    _PARTICLEORIENTATION.values_by_name[
        'PARTICLE_ORIENTATION_INITIAL_DIRECTION'
        ]._serialized_options = b'\xc2\xc1\x18\x11Initial Direction'
    _PARTICLEORIENTATION.values_by_name[
        'PARTICLE_ORIENTATION_MOVEMENT_DIRECTION']._options = None
    _PARTICLEORIENTATION.values_by_name[
        'PARTICLE_ORIENTATION_MOVEMENT_DIRECTION'
        ]._serialized_options = b'\xc2\xc1\x18\x12Movement direction'
    _PARTICLEORIENTATION.values_by_name['PARTICLE_ORIENTATION_ANGULAR_VELOCITY'
        ]._options = None
    _PARTICLEORIENTATION.values_by_name['PARTICLE_ORIENTATION_ANGULAR_VELOCITY'
        ]._serialized_options = b'\xc2\xc1\x18\x10Angular Velocity'
    _EMITTER.fields_by_name['tile_source']._options = None
    _EMITTER.fields_by_name['tile_source'
        ]._serialized_options = b'\xa0\xbb\x18\x01'
    _EMITTER.fields_by_name['material']._options = None
    _EMITTER.fields_by_name['material'
        ]._serialized_options = b'\xa0\xbb\x18\x01'
    _EMITTERTYPE._serialized_start = 1802
    _EMITTERTYPE._serialized_end = 1991
    _PLAYMODE._serialized_start = 1993
    _PLAYMODE._serialized_end = 2063
    _EMISSIONSPACE._serialized_start = 2065
    _EMISSIONSPACE._serialized_end = 2158
    _EMITTERKEY._serialized_start = 2161
    _EMITTERKEY._serialized_end = 2992
    _PARTICLEKEY._serialized_start = 2995
    _PARTICLEKEY._serialized_end = 3444
    _MODIFIERTYPE._serialized_start = 3447
    _MODIFIERTYPE._serialized_end = 3621
    _MODIFIERKEY._serialized_start = 3624
    _MODIFIERKEY._serialized_end = 3753
    _BLENDMODE._serialized_start = 3756
    _BLENDMODE._serialized_end = 3953
    _SIZEMODE._serialized_start = 3955
    _SIZEMODE._serialized_end = 4029
    _PARTICLEORIENTATION._serialized_start = 4032
    _PARTICLEORIENTATION._serialized_end = 4301
    _SPLINEPOINT._serialized_start = 112
    _SPLINEPOINT._serialized_end = 173
    _MODIFIER._serialized_start = 176
    _MODIFIER._serialized_end = 491
    _MODIFIER_PROPERTY._serialized_start = 377
    _MODIFIER_PROPERTY._serialized_end = 491
    _EMITTER._serialized_start = 494
    _EMITTER._serialized_end = 1699
    _EMITTER_PROPERTY._serialized_start = 1481
    _EMITTER_PROPERTY._serialized_end = 1594
    _EMITTER_PARTICLEPROPERTY._serialized_start = 1596
    _EMITTER_PARTICLEPROPERTY._serialized_end = 1699
    _PARTICLEFX._serialized_start = 1701
    _PARTICLEFX._serialized_end = 1799

