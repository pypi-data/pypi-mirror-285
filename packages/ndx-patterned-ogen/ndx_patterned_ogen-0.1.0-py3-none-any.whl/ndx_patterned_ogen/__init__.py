import os
from pynwb import load_namespaces, get_class

try:
    from importlib.resources import files
except ImportError:
    # TODO: Remove when python 3.9 becomes the new minimum
    from importlib_resources import files

# Get path to the namespace.yaml file with the expected location when installed not in editable mode
__location_of_this_file = files(__name__)
__spec_path = __location_of_this_file / "spec" / "ndx-patterned-ogen.namespace.yaml"

# If that path does not exist, we are likely running in editable mode. Use the local path instead
if not os.path.exists(__spec_path):
    __spec_path = __location_of_this_file.parent.parent.parent / "spec" / "ndx-patterned-ogen.namespace.yaml"
    
load_namespaces(str(__spec_path))

SpatialLightModulator2D = get_class('SpatialLightModulator2D', 'ndx-patterned-ogen')
SpatialLightModulator3D = get_class('SpatialLightModulator3D', 'ndx-patterned-ogen')
LightSource = get_class('LightSource', 'ndx-patterned-ogen')
OptogeneticStimulus2DPattern = get_class('OptogeneticStimulus2DPattern', 'ndx-patterned-ogen')
OptogeneticStimulus3DPattern = get_class('OptogeneticStimulus3DPattern', 'ndx-patterned-ogen')
SpiralScanning = get_class('SpiralScanning', 'ndx-patterned-ogen')
TemporalFocusing = get_class('TemporalFocusing', 'ndx-patterned-ogen')

# Load the namespace

from .patterned_ogen import (
    PatternedOptogeneticStimulusSite,
    PatternedOptogeneticStimulusTable,
    OptogeneticStimulusSite,
    OptogeneticStimulusTarget,
)

__all__ = [
    "SpatialLightModulator3D",
    "SpatialLightModulator2D",
    "LightSource",
    "PatternedOptogeneticStimulusSite",
    "PatternedOptogeneticStimulusTable",
    "OptogeneticStimulus2DPattern",
    "OptogeneticStimulus3DPattern",
    "OptogeneticStimulusSite",
    "OptogeneticStimulusTarget",
    "SpiralScanning",
    "TemporalFocusing",
]
