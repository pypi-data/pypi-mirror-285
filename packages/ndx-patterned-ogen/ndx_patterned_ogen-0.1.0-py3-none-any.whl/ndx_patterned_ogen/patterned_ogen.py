from collections.abc import Iterable
from hdmf.utils import docval, popargs_to_dict, get_docval, popargs
from pynwb import register_class
from pynwb.core import DynamicTableRegion
from pynwb.device import Device
from pynwb.file import LabMetaData, TimeIntervals
from pynwb.ogen import OptogeneticStimulusSite
import numpy as np

namespace = "ndx-patterned-ogen"


@register_class("PatternedOptogeneticStimulusSite", namespace)
class PatternedOptogeneticStimulusSite(OptogeneticStimulusSite):
    """
    Patterned optogenetic stimulus site.
    """

    __nwbfields__ = ("effector", "spatial_light_modulator", "light_source")

    @docval(
        *get_docval(OptogeneticStimulusSite.__init__, "name", "description", "device", "location", "excitation_lambda"),
        {
            "name": "effector",
            "type": str,
            "doc": "Light-activated effector protein expressed by the targeted cell (eg. ChR2).",
            "default": None,
        },
        {
            "name": "spatial_light_modulator",
            "type": Device,
            "doc": "Spatial light modulator used to generate photostimulation pattern.",
            "default": None,
        },
        {"name": "light_source", "type": Device, "doc": "Light source used to apply photostimulation."},
    )
    def __init__(self, **kwargs):
        keys_to_set = ("effector", "spatial_light_modulator", "light_source")
        args_to_set = popargs_to_dict(keys_to_set, kwargs)
        super().__init__(**kwargs)
        for key, val in args_to_set.items():
            setattr(self, key, val)

    @docval({
        "name": "spatial_light_modulator",
        "type": Device,
        "doc": "Spatial light modulator used to generate photostimulation pattern. ",
    })
    def add_spatial_light_modulator(self, spatial_light_modulator):
        """
        Add a spatial light modulator to the photostimulation method.
        """
        if self.spatial_light_modulator is not None:
            raise ValueError("SpatialLightModulator already exists in this PatternedOptogeneticStimulusSite container.")
        else:
            self.spatial_light_modulator = spatial_light_modulator

    @docval({"name": "light_source", "type": Device, "doc": "Light source used to apply photostimulation."})
    def add_light_source(self, light_source):
        """
        Add a light source to the photostimulation method.
        """

        if self.light_source is not None:
            raise ValueError("LightSource already exists in this PatternedOptogeneticStimulusSite container.")
        else:
            self.light_source = light_source


@register_class("OptogeneticStimulusTarget", namespace)
class OptogeneticStimulusTarget(LabMetaData):
    """
    Container to store the targated rois in a photostimulation experiment.
    """

    __nwbfields__ = (
        {"name": "targeted_rois", "child": True},
        {"name": "segmented_rois", "child": True},
    )

    @docval(
        *get_docval(LabMetaData.__init__, "name"),
        {
            "name": "segmented_rois",
            "type": DynamicTableRegion,
            "doc": (
                "A table region referencing a PlaneSegmentation object storing segmented ROIs that receive"
                " photostimulation."
            ),
            "default": None,
        },
        {
            "name": "targeted_rois",
            "type": DynamicTableRegion,
            "doc": "A table region referencing a PlaneSegmentation object storing targeted ROIs.",
        },
    )
    def __init__(self, **kwargs):
        keys_to_set = ("segmented_rois", "targeted_rois")
        args_to_set = popargs_to_dict(keys_to_set, kwargs)
        super().__init__(**kwargs)
        for key, val in args_to_set.items():
            setattr(self, key, val)


@register_class("PatternedOptogeneticStimulusTable", namespace)
class PatternedOptogeneticStimulusTable(TimeIntervals):
    """
    Parameters corresponding to events of patterned optogenetic stimulation with indicated targeted rois.
    """

    __fields__ = ()
    __columns__ = (
        {"name": "start_time", "description": "Start time of stimulation, in seconds"},
        {"name": "stop_time", "description": "Stop time of stimulation, in seconds"},
        {
            "name": "power",
            "description": (
                "Power (in Watts) defined as a scalar. All rois in target receive the same photostimulation power."
            ),
            "required": False,
        },
        {
            "name": "frequency",
            "description": (
                "Frequency (in Hz) defined as a scalar. All rois in target receive the photostimulation at the same"
                " frequency."
            ),
            "required": False,
        },
        {
            "name": "pulse_width",
            "description": (
                "Pulse Width (in sec/phase) defined as a scalar. All rois in target receive the photostimulation with"
                " the same pulse width."
            ),
            "required": False,
        },
        {
            "name": "power_per_roi",
            "description": "Power (in Watts) defined as an array. Each power value refers to each roi in target.",
            "required": False,
        },
        {
            "name": "frequency_per_roi",
            "description": "Frequency (in Hz) defined as an array. Each frequency value refers to each roi in target.",
            "required": False,
        },
        {
            "name": "pulse_width_per_roi",
            "description": (
                "Pulse Width (in sec/phase) defined as an array. Each pulse width value refers to each roi in target."
            ),
            "required": False,
        },
        {"name": "targets", "description": "Targeted rois for the stimulus onset."},
        {
            "name": "stimulus_pattern",
            "description": "Link to the stimulus pattern.",
        },
        {
            "name": "stimulus_site",
            "description": "Link to the stimulus site.",
        },
    )

    @classmethod
    def check_if_argument_is_not_scalar(cls, colset, field_name):
        for row in range(len(colset[field_name])):
            if not isinstance(colset[field_name][row], (int, float, np.generic)):
                raise ValueError(
                    f"{field_name} should be defined as scalar. Use '{field_name}_per_roi' to store photostimulation"
                    f" at different {field_name}, for each rois in target."
                )

    @classmethod
    def check_length_rois_properties(cls, colset, field_name):
        for row in range(len(colset[field_name])):
            n_targets = len(colset["targets"][row].targeted_rois[:])
            n_elements = len(colset[field_name][row])
            if n_elements != n_targets:
                raise ValueError(
                    f"'{field_name}' has {n_elements} elements but it must have {n_targets} elements to match the"
                    " length of 'targeted_rois'."
                )

    @docval(
        {
            "name": "name",
            "type": str,
            "doc": "Name of this PatternedOptogeneticStimulusTable",
            "default": "PatternedOptogeneticStimulusTable",
        },
        {
            "name": "description",
            "type": str,
            "doc": "Description of what is in this PatternedOptogeneticStimulusTable",
            "default": "stimulation parameters",
        },
        *get_docval(TimeIntervals.__init__, "id", "columns", "colnames"),
    )
    def __init__(self, **kwargs):
        keys_to_set = ()
        args_to_set = popargs_to_dict(keys_to_set, kwargs)

        super().__init__(**kwargs)
        for key, val in args_to_set.items():
            setattr(self, key, val)
        columns = popargs("columns", kwargs)
        if columns is not None:
            colset = {c.name: c for c in columns}
            # First check: power_per_roi and power must not be defined in the same time
            for colname in colset.keys():
                if colname in colset.keys() and f"{colname}_per_roi" in colset.keys():
                    raise ValueError(
                        f"Both '{colname}' and '{colname}_per_roi' have been defined. Only one of them must be defined."
                    )

            # Second check: all elements in "power", "frequency", "pulse_width" must be scalars
            for column_to_check in ["power", "frequency", "pulse_width"]:
                if column_to_check in colset.keys():
                    self.check_if_argument_is_not_scalar(colset=colset, field_name=column_to_check)

            # Third check: all elements in "power_per_roi", "frequency_per_roi", "pulse_width_per_roi" columns
            # must be the same length as the respective targets
            for column_to_check in ["power_per_roi", "frequency_per_roi", "pulse_width_per_roi"]:
                if column_to_check in colset.keys():
                    self.check_length_rois_properties(colset=colset, field_name=column_to_check)

    @docval(
        {"name": "start_time", "doc": "Start time of stimulation, in seconds.", "type": float},
        {"name": "stop_time", "doc": "Stop time of stimulation, in seconds.", "type": float},
        {
            "name": "power",
            "doc": "Power (in Watts) defined as a scalar. All rois in target receive the same photostimulation power.",
            "type": (int, float, Iterable),
            "default": None,
        },
        {
            "name": "frequency",
            "doc": (
                "Frequency (in Hz) defined as a scalar. All rois in target receive the photostimulation at the same"
                " frequency."
            ),
            "type": (int, float, Iterable),
            "default": None,
        },
        {
            "name": "pulse_width",
            "doc": (
                "Pulse Width (in sec/phase) defined as a scalar. All rois in target receive the photostimulation with"
                " the same pulse width."
            ),
            "type": (int, float, Iterable),
            "default": None,
        },
        {
            "name": "power_per_roi",
            "doc": "Power (in Watts) defined as an array. Each power value refers to each roi in target.",
            "type": (int, float, Iterable),
            "default": None,
        },
        {
            "name": "frequency_per_roi",
            "doc": "Frequency (in Hz) defined as an array. Each frequency value refers to each roi in target.",
            "type": (int, float, Iterable),
            "default": None,
        },
        {
            "name": "pulse_width_per_roi",
            "doc": (
                "Pulse Width (in sec/phase) defined as an array. Each pulse width value refers to each roi in target."
            ),
            "type": (int, float, Iterable),
            "default": None,
        },
        {
            "name": "targets",
            "doc": "Targeted rois for the stimulus onset.",
            "type": OptogeneticStimulusTarget,
        },
        {
            "name": "stimulus_pattern",
            "doc": "Link to the stimulus pattern.",
            "type": LabMetaData,
        },
        {
            "name": "stimulus_site",
            "doc": "Link to the stimulus site.",
            "type": PatternedOptogeneticStimulusSite,
        },
        allow_extra=True,
    )
    def add_interval(self, **kwargs):
        """
        Add a stimulation parameters for a specific stimulus onset.
        """
        super(PatternedOptogeneticStimulusTable, self).add_interval(**kwargs)

        if kwargs["power"] is not None and not isinstance(kwargs["power"], (int, float, np.generic)):
            raise ValueError(
                "'power' should be defined as scalar. Use 'power_per_roi' to store photostimulation at different"
                " power, for each rois in target."
            )
        if kwargs["frequency"] is not None and not isinstance(kwargs["frequency"], (int, float, np.generic)):
            raise ValueError(
                "'frequency' should be defined as scalar. Use 'frequency_per_roi' to store photostimulation at"
                " different frequency, for each rois in target."
            )

        if kwargs["pulse_width"] is not None and not isinstance(kwargs["pulse_width"], (int, float, np.generic)):
            raise ValueError(
                "'pulse_width' should be defined as scalar. Use 'pulse_width_per_roi' to store photostimulation with"
                " different pulse width, for each rois in target."
            )

        n_targets = len(kwargs["targets"].targeted_rois[:])

        if kwargs["power_per_roi"] is not None:
            n_elements = len(kwargs["power_per_roi"])
            if n_elements != n_targets:
                raise ValueError(
                    f"'power_per_roi' has {n_elements} elements but it must have"
                    f" {n_targets} elements to match the length of 'targeted_rois'."
                )

        if kwargs["frequency_per_roi"] is not None:
            n_elements = len(kwargs["frequency_per_roi"])
            if n_elements != n_targets:
                raise ValueError(
                    f"'frequency_per_roi' has {n_elements} elements but it must have"
                    f" {n_targets} elements as 'targeted_roi'."
                )

        if kwargs["pulse_width_per_roi"] is not None:
            n_elements = len(kwargs["pulse_width_per_roi"])
            if n_elements != n_targets:
                raise ValueError(
                    f"'pulse_width_per_roi' has {n_elements} elements but it must have"
                    f" {n_targets} elements as 'targeted_roi'."
                )

        if kwargs["power_per_roi"] is None and kwargs["power"] is None:
            raise ValueError(
                "Neither 'power' nor 'power_per_roi' have been defined. At least one of the two must be defined."
            )

        if kwargs["power_per_roi"] is not None and kwargs["power"] is not None:
            raise ValueError("Both 'power' and 'power_per_roi' have been defined. Only one of them must be defined.")
