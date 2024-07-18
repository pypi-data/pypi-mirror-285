# ndx-patterned-ogen Extension for NWB

<div style="display:inline">
This is a <a href="https://www.nwb.org/">NeuroData Without Borders (NWB)</a> extension for storing data and metadata from patterned optogenetic (<a href="https://www.nature.com/articles/nmeth.3217">holographic</a>) photostimulation methods. It includes containers for storing photostimulation-specific device parameters, photostimulation target, stimulation patterns and time interval data related to photostimulation.
</div>

![extension schema](ndx-patterned-ogen.png)

<br>We release ten <a href="https://pynwb.readthedocs.io/en/stable/">PyNWB</a> containers as part of this extension (we currently only have a Python implementation, rather than both Python and a MATLAB ones -- this is why the `matnwb` directory is empty):

* The `SpatialLightModulator2D`/`SpatialLightModulator3D` and `LightSource` containers store metadata about the spatial light modulator (either bidimensional or threedimensional) and light source used in the photostimulation, respectively. These containers are then linked to the `PatternedOptogeneticStimulusSite` parent container, which stores the remaining photostimulation method-specifici metadata.
* `OptogeneticStimulusPattern` stores parameters for a generic photostimulation pattern.
    * `TemporalFocusing` stores parameters associated with the temporal focusing pattern.
    * `SpiralScanning` stores parameters associated with the spiral scanning pattern.
* `OptogeneticStimulusTarget` container stored a subset of targeted ROIs `targeted_rois`, that is a `DynamicTableRegion` referencing the rows of a `PlaneSegmentation`. Optionally, we can store the corresponding segmented ROIs that have been successfully photostimulated. `segmented_rois` is also a `DynamicTableRegion` referencing the rows of a `PlaneSegmentation`. Since not all targeted ROIs may result in an actual photostimulation a `global_roi_ids` column should be added to both `PlaneSegmentation` object to express the correspondence between the targeted and segmented ROIs.
* `PhotostimulationTable` is an `TimeIntervals` table. Each row stores a stimulus onset - defined by `start`, `stop`, `power` (optionally `frequency` and `pulse_width`). Each stimulus onset reference a specific `OptogeneticStimulusTarget` and `PhotostimulationPattern`
NB: When `power`(`frequency` and `pulse_width`) is defined, its value apply to all the ROIs in `targets`. When `power_per_roi`(`frequency_per_roi` and `pulse_width_per_roi`) id defined, the length must equal to the number of ROIs in targets, and each element refers to a specific targeted ROI.

## Background

<img src="https://github.com/histedlab/ndx-photostim/blob/main/docs/images/Cap1.PNG?raw=True" width="225em" align="left" style=" margin:0.5em 0.5em 0.5em 0.5em;">
State-of-the-art <a href="https://www.nature.com/articles/s41467-017-01031-3">patterned photostimulation methods</a>, used in concert with <a href="https://www.nature.com/articles/nmeth818">two-photon imaging</a>, 
allow unprecedented 
control and measurement of cell activity in the living brain. Methods for managing data for two-photon imaging 
experiments are improving, but there is little to no standardization of data for these stimulation methods. 
Stimulation in vivo depends on fine-tuning many experimental variables, which poses a challenge for reproducibility 
and data sharing between researchers. To improve <a href="https://www.sciencedirect.com/science/article/pii/S0896627321009557">standardization</a> of photostimulation data storage and processing, 
we release this extension as a generic data format for simultaneous patterned optogenetic stimulation experiments, 
using the NWB format to store experimental details and data relating to both acquisition 
and photostimulation.

## Installation

To install the extension, first clone the `ndx-patterned-ogen` repository to the desired folder using the command
```angular2svg
git clone https://github.com/https://github.com/catalystneuro/ndx-patterned-ogen.git
```
Then, to install the requisite python packages and extension, run:
```angular2svg
python -m pip install -r requirements.txt -r requirements-dev.txt
python setup.py install
```
The extension can then be imported into python scripts via `import ndx_patterned_ogen`.

## Usage

**For full example usage, see [tutorial.ipynb](https://github.com/catalystneuro/ndx-patterned-ogen/blob/main/tutorial_patterned_ogen.ipynb)**

#### Example Usage for the ndx-patterne-ogen-stimulation for 2D stimulus 
In the following tutorial, we demonstrate use of the `ndx-patterned-ogen` extension to the NWB data standard. Specifically we:
1. Create `SpatialLightModulator2D` and `LightSource` containers, representing the devices used in the paradigm.
2. Use the `PatternedOptogeneticStimulusSite` container to store information about location, the opsin and excitation wavelength used in the paradigm
3. Use the `OptogeneticStimulus2DPattern` (or `SpiralScanning` or `TemporalFocusing`) container to store the pattern-specific parameters of the stimulus onset.
4. Record the stimulus presentation within the `PatternedOptogeneticStimulusTable` container
6. Write all devices, stimuli, and presentation tables to an `.nwb` file and confirm it can be read back




```python
# First, we import then necessary files and create an empty `NWBFile`.
import datetime
import numpy as np
from pynwb import NWBFile, NWBHDF5IO
from ndx_patterned_ogen import (
    SpatialLightModulator2D,
    LightSource,
    PatternedOptogeneticStimulusSite,
    PatternedOptogeneticStimulusTable,
    OptogeneticStimulus2DPattern,
    OptogeneticStimulusTarget,
    SpiralScanning,
    TemporalFocusing,
)
from hdmf.common.table import DynamicTableRegion

from pynwb.ophys import PlaneSegmentation, ImageSegmentation, OpticalChannel

nwbfile = NWBFile(
    session_description="patterned optogenetic synthetic experiment (all optical system)",
    identifier="identifier",
    session_start_time=datetime.datetime.now(datetime.timezone.utc),
)

# metadata for spiatial light modulator
spatial_light_modulator = SpatialLightModulator2D(
    name="SpatialLightModulator2D",
    description="Generic description for the slm",
    model="slm model",
    manufacturer="slm manufacturer",
    spatial_resolution=[512, 512],
)
nwbfile.add_device(spatial_light_modulator)

# metadata for the light source
light_source = LightSource(
    name="Laser",
    model="laser model",
    manufacturer="laser manufacturer",
    stimulation_wavelength=1035.0,  # nm
    filter_description="Short pass at 1040 nm",
    description="Generic description for the laser",
    peak_power=70e-3,  # the peak power of stimulation in Watts
    intensity=0.005,  # the intensity of excitation in W/mm^2
    exposure_time=2.51e-13,  # the exposure time of the sample in seconds
    pulse_rate=1 / 2.51e-13,  # the pulse rate of the laser is in Hz
)
nwbfile.add_device(light_source)

# metadata for the microscope
microscope = nwbfile.create_device(
    name="2P_microscope",
    description="My two-photon microscope",
    manufacturer="The best microscope manufacturer",
)

# metadata for the stimulus methods
site = PatternedOptogeneticStimulusSite(
    name="PatternedOptogeneticStimulusSite",
    description="Scanning",  # Scanning or scanless method for shaping optogenetic light (e.g., diffraction limited points, 3D shot, disks, etc.).
    excitation_lambda=600.0,  # nm
    effector="ChR2",
    location="VISrl",
    device=microscope,
    spatial_light_modulator=spatial_light_modulator,
    light_source=light_source,
)
nwbfile.add_ogen_site(site)

# For demonstrative purpose, we define here fout different stimulation pattern:
# 1. two generic where the `sweep_size` and the `sweep_mask` can be defined to describe the spatial pattern. If `sweep_size` is a scalar, the sweep pattern is assumed to be a circle with diameter `sweep_size`. If `sweep_size` is a two or three dimensional array, the the sweep pattern is assumed to be a rectangle, with dimensions [width, height]. If the shape is neither a circle or a rectangular, the shape can be save in `sweep_mask`.
# 2. one spiral pattern
# 3. one temporal focusing beam pattern

# metadata for a generic stimulus pattern
import numpy as np
import matplotlib.pyplot as plt


# auxiliary function to generate the sweep shape, either circular or rectangular
def generate_image_mask_np(width, height, sweep_size_in_pizels):
    # Create a black image mask
    image_mask = np.zeros((height, width), dtype=np.uint8)

    # Calculate the position for the center of the white spot
    center_x = width // 2
    center_y = height // 2

    if isinstance(sweep_size_in_pizels, int):
        # Circular spot
        Y, X = np.ogrid[:height, :width]
        dist_from_center = np.sqrt((X - center_x) ** 2 + (Y - center_y) ** 2)
        image_mask[dist_from_center <= sweep_size_in_pizels / 2] = 255

    elif len(sweep_size_in_pizels) == 2:
        # Rectangular spot
        half_width = sweep_size_in_pizels[0] // 2
        half_height = sweep_size_in_pizels[1] // 2
        top_left = (center_x - half_width, center_y - half_height)
        bottom_right = (center_x + half_width, center_y + half_height)
        image_mask[top_left[1] : bottom_right[1], top_left[0] : bottom_right[0]] = 255
    else:
        raise ValueError("Invalid sweep_size_in_pizels. Should be a scalar or a 2-element array.")
    return image_mask


sweep_size = 8
circular_image_mask_np = generate_image_mask_np(
    width=sweep_size * 2, height=sweep_size * 2, sweep_size_in_pizels=sweep_size
)  # assuming 1 pixel=1 um
generic_circular_pattern = OptogeneticStimulus2DPattern(
    name="CircularOptogeneticStimulusPattern",
    description="circular pattern",
    sweep_size=sweep_size,  # um
    # sweep_mask=circular_image_mask_np,
)
nwbfile.add_lab_meta_data(generic_circular_pattern)

# Display the image mask using matplotlib
plt.imshow(circular_image_mask_np, cmap="gray")
plt.show()

sweep_size = [5, 10]
rectangular_image_mask_np = generate_image_mask_np(width=20, height=20, sweep_size_in_pizels=sweep_size)
generic_rectangular_pattern = OptogeneticStimulus2DPattern(
    name="RectangularOptogeneticStimulusPattern",
    description="rectangular pattern",
    sweep_size=sweep_size,  # um
    sweep_mask=rectangular_image_mask_np,
)
nwbfile.add_lab_meta_data(generic_rectangular_pattern)

# Display the image mask using matplotlib
plt.imshow(rectangular_image_mask_np, cmap="gray")
plt.show()

# metadata for spiral scanning pattern
spiral_scanning = SpiralScanning(
    name="SpiralScanning",
    diameter=15,  # um
    height=10,  # um
    number_of_revolutions=5,
    description="scanning beam pattern",
)
nwbfile.add_lab_meta_data(spiral_scanning)

# metadata for temporal focusing pattern
temporal_focusing = TemporalFocusing(
    name="TemporalFocusing",
    description="scanless beam pattern",
    lateral_point_spread_function="9 um ± 0.7 um",
    axial_point_spread_function="32 um ± 1.6 um",
)
nwbfile.add_lab_meta_data(temporal_focusing)

# Define two `PlaneSegmentation` tables; one for post-hoc ROI (possibly cell) identification; the other for targeted ROIs. Additional columns on both tables can indicate if the ROI is a cell, and the two tables can be harmonized with the use of a global_roi_id field that matches ROI IDs from one table to the other.
# To do so, we need to define an `ImagingPlane` and an `OpticalChannel` first.
optical_channel = OpticalChannel(
    name="OpticalChannel",
    description="an optical channel",
    emission_lambda=500.0,
)
imaging_plane = nwbfile.create_imaging_plane(
    name="ImagingPlane",
    optical_channel=optical_channel,
    imaging_rate=30.0,
    description="a very interesting part of the brain",
    device=microscope,
    excitation_lambda=600.0,
    indicator="GFP",
    location="V1",
    grid_spacing=[0.01, 0.01],
    grid_spacing_unit="meters",
    origin_coords=[1.0, 2.0, 3.0],
    origin_coords_unit="meters",
)


# All the ROIs simultaneously illuminated are stored in `targeted_rois` in an `OptogeneticStimulusTarget` container, as a table region referencing the `TargetPlaneSegmentation`.
# In this example, the targeted ROIs are 45 in total, divided in 3 groups of 15 ROIs that will be simultaneously illuminated with the same stimulus pattern. Only 30 of them, 10 for each group, results in a successful photostimulation.
# Therefore, we define a `PlaneSegmentation` containing 30 ROIs in total and 3 `roi_table_region` containing 10 ROIs each that would be segmented after being stimulated, and stored in three separate `OptogeneticStimulusTarget` containers.
n_targeted_rois = 45
n_targeted_rois_per_group = n_targeted_rois // 3

targeted_rois_centroids = np.array([[i, i, 0] for i in np.arange(n_targeted_rois, dtype=int)])

targeted_plane_segmentation = PlaneSegmentation(
    name="TargetPlaneSegmentation",
    description="Table for storing the targeted roi centroids, defined by a one-pixel mask",
    imaging_plane=imaging_plane,
)

for roi_centroid in targeted_rois_centroids:
    targeted_plane_segmentation.add_roi(pixel_mask=[roi_centroid])

if nwbfile is not None:
    if "ophys" not in nwbfile.processing:
        nwbfile.create_processing_module("ophys", "ophys")
    nwbfile.processing["ophys"].add(targeted_plane_segmentation)

targeted_rois_1 = targeted_plane_segmentation.create_roi_table_region(
    name="targeted_rois",  # it must be called "segmented_rois"
    description="targeted rois",
    region=list(np.arange(n_targeted_rois_per_group, dtype=int)),
)

targeted_rois_2 = targeted_plane_segmentation.create_roi_table_region(
    name="targeted_rois",  # it must be called "segmented_rois"
    description="targeted rois",
    region=list(np.arange(n_targeted_rois_per_group, 2 * n_targeted_rois_per_group, dtype=int)),
)

targeted_rois_3 = targeted_plane_segmentation.create_roi_table_region(
    name="targeted_rois",  # it must be called "segmented_rois"
    description="targeted rois",
    region=list(np.arange(2 * n_targeted_rois_per_group, n_targeted_rois, dtype=int)),
)

n_segmented_rois = 30
n_segmented_rois_per_group = n_segmented_rois // 3

plane_segmentation = PlaneSegmentation(
    name="PlaneSegmentation",
    description="output from segmenting my favorite imaging plane",
    imaging_plane=imaging_plane,
)

# TODO add global_roi_id

for _ in range(n_segmented_rois):
    plane_segmentation.add_roi(image_mask=np.zeros((512, 512)))

if nwbfile is not None:
    if "ophys" not in nwbfile.processing:
        nwbfile.create_processing_module("ophys", "ophys")
    nwbfile.processing["ophys"].add(plane_segmentation)


segmented_rois_1 = plane_segmentation.create_roi_table_region(
    name="segmented_rois",  # it must be called "segmented_rois"
    description="segmented rois",
    region=list(np.arange(n_segmented_rois_per_group, dtype=int)),
)

segmented_rois_2 = plane_segmentation.create_roi_table_region(
    name="segmented_rois",
    description="segmented rois",
    region=list(np.arange(n_segmented_rois_per_group, 2 * n_segmented_rois_per_group, dtype=int)),
)

segmented_rois_3 = plane_segmentation.create_roi_table_region(
    name="segmented_rois",
    description="segmented rois",
    region=list(np.arange(2 * n_segmented_rois_per_group, n_segmented_rois, dtype=int)),
)


hologram_1 = OptogeneticStimulusTarget(name="Hologram1", segmented_rois=segmented_rois_1, targeted_rois=targeted_rois_1)
nwbfile.add_lab_meta_data(hologram_1)

hologram_2 = OptogeneticStimulusTarget(name="Hologram2", segmented_rois=segmented_rois_2, targeted_rois=targeted_rois_2)

nwbfile.add_lab_meta_data(hologram_2)

hologram_3 = OptogeneticStimulusTarget(name="Hologram3", targeted_rois=targeted_rois_3)

nwbfile.add_lab_meta_data(hologram_3)

# Define the stimulus sequences on the targeted ROIs previously defined in the imaging frame coordinates
# If `power`,`frequency` and `pulse_width` are defined as a scalar it is assumed that all the ROIs defined in `targets` receive the same stimulus `power`,`frequency` and `pulse_width`. However, we can also define `power`,`frequency` and `pulse_width` as 1D arrays of dimension equal to the number of ROIs in targets, so we can define different `power`,`frequency` and `pulse_width` for each target.
stimulus_table = PatternedOptogeneticStimulusTable(
    name="PatternedOptogeneticStimulusTable", description="Patterned stimulus"
)
stimulus_table.add_interval(
    start_time=0.0,
    stop_time=1.0,
    power=70e-3,
    frequency=20.0,
    pulse_width=0.1,
    stimulus_pattern=temporal_focusing,
    targets=nwbfile.lab_meta_data["Hologram1"],
    stimulus_site=site,
)
stimulus_table.add_interval(
    start_time=0.5,
    stop_time=1.0,
    power=50e-3,
    stimulus_pattern=spiral_scanning,
    targets=hologram_2,
    stimulus_site=site,
)
stimulus_table.add_interval(
    start_time=0.8,
    stop_time=1.7,
    power=40e-3,
    frequency=20.0,
    pulse_width=0.1,
    stimulus_pattern=generic_circular_pattern,
    targets=hologram_3,
    stimulus_site=site,
)
nwbfile.add_time_intervals(stimulus_table)

hologram_3.add_segmented_rois(segmented_rois_3)

# Write and read the NWB File
nwbfile_path = "basics_tutorial_patterned_ogen.nwb"
with NWBHDF5IO(nwbfile_path, mode="w") as io:
    io.write(nwbfile)

with NWBHDF5IO(nwbfile_path, mode="r") as io:
    nwbfile_in = io.read()

```

## Documentation

### Specification


Documentation for the extension's <a href="https://schema-language.readthedocs.io/en/latest/">specification</a>, which is based on the YAML files, is generated and stored in
the `./docs` folder. To create it, run the following from the home directory:
```angular2svg
cd docs
make fulldoc
```
This will save documentation to the `./docs/build` folder, and can be accessed via the 
`./docs/build/html/index.html` file.

### API

To generate documentation for the Python API (stores in `./api_docs`), we use <a href="https://www.sphinx-doc.org/en/master/">Sphinx</a> 
and a template from <a href="https://readthedocs.org/">ReadTheDocs</a>. API documentation can
be created by running 
```angular2svg
sphinx-build -b html api_docs/source/ api_docs/build/
```
from the home folder. Similar to the specification docs, API documentation is stored in `./api_docs/build`. Select 
`./api_docs/build/index.html` to access the API documentation in a website format.


## Credit

Code by Alessandra Trapani. Collaboration between the [CatalystNeuro Team](https://www.catalystneuro.com/) and [Histed Lab](https://www.nimh.nih.gov/research/research-conducted-at-nimh/research-areas/clinics-and-labs/ncb).


This extension was created using [ndx-template](https://github.com/nwb-extensions/ndx-template).

