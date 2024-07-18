from .particle_ddf_pb2 import Emitter,Modifier,ParticleFX,SplinePoint 
from .input_ddf_pb2 import GamepadMap,GamepadMapEntry,GamepadMaps,GamepadModifier_t,GamepadTrigger,InputBinding,KeyTrigger,MouseTrigger,TextTrigger,TouchTrigger 
from .rig_ddf_pb2 import AnimationInstanceDesc,AnimationSet,AnimationSetDesc,AnimationTrack,Bone,EventKey,EventTrack,IK,Mesh,MeshSet,Model,RigAnimation,RigScene,Skeleton 

import pkgutil , importlib ,  os , collections
current_module_path = os.path.dirname(__file__)
result = dict()
for finder, name, ispkg in pkgutil.iter_modules([current_module_path]):
    full_module_name = f"{__name__}.{name}"
    pkg_lib = importlib.import_module(full_module_name)
    for elem in dir(pkg_lib) : 
        may_msg = pkg_lib.__getattribute__(elem)
        if type(may_msg).__name__ == 'MessageMeta' : 
            result[may_msg.__name__] = may_msg
Defold = collections.namedtuple('Defold' , result.keys() )(**result)
__all__ = ['Defold']
