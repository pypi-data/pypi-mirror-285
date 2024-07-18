"""Unit and integration tests for the PatternedOptogeneticStimulusTable extension neurodata type."""

import numpy as np
from hdmf.common.table import VectorData
from pynwb import NWBHDF5IO, NWBFile
from pynwb.testing.mock.file import mock_NWBFile
from pynwb.testing import TestCase, remove_test_file, NWBH5IOFlexMixin

from ndx_patterned_ogen import PatternedOptogeneticStimulusTable
from .mock.patternedogen import (
    mock_OptogeneticStimulus2DPattern,
    mock_OptogeneticStimulusTarget,
    mock_PatternedOptogeneticStimulusSite,
)


def set_up_nwbfile(nwbfile: NWBFile = None):
    """Create an NWBFile with a Device"""
    nwbfile = nwbfile or mock_NWBFile()
    return nwbfile


class TestPatternedOgenConstructor(TestCase):
    """Simple unit test for creating a PatternedOptogeneticStimulusTable."""

    def setUp(self):
        """Set up an NWB file."""
        self.nwbfile = set_up_nwbfile()

    def test_constructor(self):
        """Test that the constructor for PatternedOptogeneticStimulusTable sets values as expected,
        when 'columns' is passed as argument."""

        start_time = VectorData(name="start_time", description="start time", data=[0.0, 0.0, 0.0])
        stop_time = VectorData(name="stop_time", description="stop time", data=[1.0, 1.0, 1.0])
        power = VectorData(name="power", description="power", data=[0.0, 0.0, 0.0])
        frequency = VectorData(name="frequency", description="frequency", data=[0.0, 0.0, 0.0])
        pulse_width = VectorData(name="pulse_width", description="pulse_width", data=[0.0, 0.0, 0.0])
        stimulus_pattern_s = mock_OptogeneticStimulus2DPattern(nwbfile=self.nwbfile)
        stimulus_pattern = VectorData(
            name="stimulus_pattern",
            description="stimulus_pattern",
            data=[stimulus_pattern_s, stimulus_pattern_s, stimulus_pattern_s],
        )
        targets_s = mock_OptogeneticStimulusTarget(nwbfile=self.nwbfile)
        targets = VectorData(name="targets", description="targets", data=[targets_s, targets_s, targets_s])
        stimulus_site_s = mock_PatternedOptogeneticStimulusSite(nwbfile=self.nwbfile)
        stimulus_site = VectorData(
            name="stimulus_site", description="stimulus_site", data=[stimulus_site_s, stimulus_site_s, stimulus_site_s]
        )
        columns = [start_time, stop_time, power, frequency, pulse_width, stimulus_pattern, targets, stimulus_site]

        stimulus_table = PatternedOptogeneticStimulusTable(
            name="PatternedOptogeneticStimulusTable",
            description="description",
            columns=columns,
        )

        self.assertEqual(stimulus_table.name, "PatternedOptogeneticStimulusTable")
        self.assertEqual(stimulus_table.description, "description")
        np.testing.assert_array_equal(stimulus_table.start_time[:], start_time)
        np.testing.assert_array_equal(stimulus_table.stop_time[:], stop_time)

    def test_constructor_power_as_array_fail(self):
        """Test that the constructor for PatternedOptogeneticStimulusTable fails when defining
        an element of 'power' as a list, when 'columns' is passed as argument."""

        start_time = VectorData(name="start_time", description="start time", data=[0.0, 0.0, 0.0])
        stop_time = VectorData(name="stop_time", description="stop time", data=[1.0, 1.0, 1.0])
        power = VectorData(name="power", description="power", data=[np.ones((3)), 1.0, 1.0])
        frequency = VectorData(name="frequency", description="frequency", data=[0.0, 0.0, 0.0])
        pulse_width = VectorData(name="pulse_width", description="pulse_width", data=[0.0, 0.0, 0.0])
        stimulus_pattern_s = mock_OptogeneticStimulus2DPattern(nwbfile=self.nwbfile)
        stimulus_pattern = VectorData(
            name="stimulus_pattern",
            description="stimulus_pattern",
            data=[stimulus_pattern_s, stimulus_pattern_s, stimulus_pattern_s],
        )
        targets_s = mock_OptogeneticStimulusTarget(nwbfile=self.nwbfile)
        targets = VectorData(name="targets", description="targets", data=[targets_s, targets_s, targets_s])
        stimulus_site_s = mock_PatternedOptogeneticStimulusSite(nwbfile=self.nwbfile)
        stimulus_site = VectorData(
            name="stimulus_site", description="stimulus_site", data=[stimulus_site_s, stimulus_site_s, stimulus_site_s]
        )
        columns = [start_time, stop_time, power, frequency, pulse_width, stimulus_pattern, targets, stimulus_site]

        with self.assertRaises(ValueError):
            _ = PatternedOptogeneticStimulusTable(
                name="PatternedOptogeneticStimulusTable",
                description="description",
                columns=columns,
            )

    def test_constructor_power_per_roi(self):
        """Test that the constructor for PatternedOptogeneticStimulusTable sets values as expected,
        when 'columns' is passed as argument."""

        start_time = VectorData(name="start_time", description="start time", data=[0.0, 0.0, 0.0])
        stop_time = VectorData(name="stop_time", description="stop time", data=[1.0, 1.0, 1.0])

        targets_s = mock_OptogeneticStimulusTarget(nwbfile=self.nwbfile)
        targets = VectorData(name="targets", description="targets", data=[targets_s, targets_s, targets_s])

        per_rois = np.ones((len(targets_s.targeted_rois[:])))
        power_per_roi = VectorData(
            name="power_per_roi", description="power_per_roi", data=[per_rois, per_rois, per_rois]
        )
        stimulus_pattern_s = mock_OptogeneticStimulus2DPattern(nwbfile=self.nwbfile)
        stimulus_pattern = VectorData(
            name="stimulus_pattern",
            description="stimulus_pattern",
            data=[stimulus_pattern_s, stimulus_pattern_s, stimulus_pattern_s],
        )

        stimulus_site_s = mock_PatternedOptogeneticStimulusSite(nwbfile=self.nwbfile)
        stimulus_site = VectorData(
            name="stimulus_site", description="stimulus_site", data=[stimulus_site_s, stimulus_site_s, stimulus_site_s]
        )
        columns = [start_time, stop_time, power_per_roi, stimulus_pattern, targets, stimulus_site]
        stimulus_table = PatternedOptogeneticStimulusTable(
            name="PatternedOptogeneticStimulusTable",
            description="description",
            columns=columns,
        )

        self.assertEqual(stimulus_table.name, "PatternedOptogeneticStimulusTable")
        self.assertEqual(stimulus_table.description, "description")
        np.testing.assert_array_equal(stimulus_table.power_per_roi[:], power_per_roi)

    def test_constructor_power_per_roi_fail_for_mismatch_dim(self):
        """Test that the constructor for PatternedOptogeneticStimulusTable fails when defining
        the elements of 'power_per_roi' with a different length with respect to 'targets',
        when 'columns' is passed as argument."""

        start_time = VectorData(name="start_time", description="start time", data=[0.0, 0.0, 0.0])
        stop_time = VectorData(name="stop_time", description="stop time", data=[1.0, 1.0, 1.0])

        targets_s = mock_OptogeneticStimulusTarget(nwbfile=self.nwbfile)
        targets = VectorData(name="targets", description="targets", data=[targets_s, targets_s, targets_s])

        per_rois = np.ones((len(targets_s.targeted_rois[:]) + 2))
        power_per_roi = VectorData(
            name="power_per_roi", description="power_per_roi", data=[per_rois, per_rois, per_rois]
        )
        stimulus_pattern_s = mock_OptogeneticStimulus2DPattern(nwbfile=self.nwbfile)
        stimulus_pattern = VectorData(
            name="stimulus_pattern",
            description="stimulus_pattern",
            data=[stimulus_pattern_s, stimulus_pattern_s, stimulus_pattern_s],
        )

        stimulus_site_s = mock_PatternedOptogeneticStimulusSite(nwbfile=self.nwbfile)
        stimulus_site = VectorData(
            name="stimulus_site", description="stimulus_site", data=[stimulus_site_s, stimulus_site_s, stimulus_site_s]
        )
        columns = [start_time, stop_time, power_per_roi, stimulus_pattern, targets, stimulus_site]

        with self.assertRaises(ValueError) as context:
            _ = PatternedOptogeneticStimulusTable(
                name="PatternedOptogeneticStimulusTable",
                description="description",
                columns=columns,
            )

        # Assert that the error message matches the expected one
        expected_error_message = (
            f"'power_per_roi' has {len(per_rois)} elements but it must have"
            f" {targets_s.targeted_rois.shape[0]} elements to match the length of 'targeted_rois'."
        )
        self.assertEqual(str(context.exception), expected_error_message)

    def test_constructor_power_and_power_per_roi_both_defined_fail(self):
        """Test that the constructor for PatternedOptogeneticStimulusTable fails when defining
        both 'power_per_roi' and 'power', when 'columns' is passed as argument."""

        start_time = VectorData(name="start_time", description="start time", data=[0.0, 0.0, 0.0])
        stop_time = VectorData(name="stop_time", description="stop time", data=[1.0, 1.0, 1.0])

        targets_s = mock_OptogeneticStimulusTarget(nwbfile=self.nwbfile)
        targets = VectorData(name="targets", description="targets", data=[targets_s, targets_s, targets_s])

        per_rois = np.ones((len(targets_s.targeted_rois[:])))
        power_per_roi = VectorData(
            name="power_per_roi", description="power_per_roi", data=[per_rois, per_rois, per_rois]
        )
        power = VectorData(name="power", description="power", data=[0.0, 0.0, 0.0])

        stimulus_pattern_s = mock_OptogeneticStimulus2DPattern(nwbfile=self.nwbfile)
        stimulus_pattern = VectorData(
            name="stimulus_pattern",
            description="stimulus_pattern",
            data=[stimulus_pattern_s, stimulus_pattern_s, stimulus_pattern_s],
        )

        stimulus_site_s = mock_PatternedOptogeneticStimulusSite(nwbfile=self.nwbfile)
        stimulus_site = VectorData(
            name="stimulus_site", description="stimulus_site", data=[stimulus_site_s, stimulus_site_s, stimulus_site_s]
        )
        columns = [start_time, stop_time, power, power_per_roi, stimulus_pattern, targets, stimulus_site]

        with self.assertRaises(ValueError) as context:
            _ = PatternedOptogeneticStimulusTable(
                name="PatternedOptogeneticStimulusTable",
                description="description",
                columns=columns,
            )

        # Assert that the error message matches the expected one
        expected_error_message = "Both 'power' and 'power_per_roi' have been defined. Only one of them must be defined."
        self.assertEqual(str(context.exception), expected_error_message)

    def test_constructor_add_interval(self):
        """Test that the constructor for PatternedOptogeneticStimulusTable sets values as expected,
        using add_interval() function."""

        stimulus_table = PatternedOptogeneticStimulusTable(
            name="PatternedOptogeneticStimulusTable",
            description="description",
        )

        start_time = 0.0
        stop_time = 1.0
        power = 70.0
        frequency = 20.0
        pulse_width = 0.1

        stimulus_table.add_interval(
            start_time=start_time,
            stop_time=stop_time,
            power=power,
            frequency=frequency,
            pulse_width=pulse_width,
            stimulus_pattern=mock_OptogeneticStimulus2DPattern(nwbfile=self.nwbfile),
            targets=mock_OptogeneticStimulusTarget(nwbfile=self.nwbfile),
            stimulus_site=mock_PatternedOptogeneticStimulusSite(nwbfile=self.nwbfile),
        )

        self.assertEqual(stimulus_table.name, "PatternedOptogeneticStimulusTable")
        self.assertEqual(stimulus_table.description, "description")
        np.testing.assert_array_equal(stimulus_table.start_time[:], [start_time])
        np.testing.assert_array_equal(stimulus_table.stop_time[:], [stop_time])

    def test_constructor_add_interval_power_as_array_fail(self):
        """Test that the constructor for PatternedOptogeneticStimulusTable fails when defining
        an element of 'power' as a list, using add_interval() function."""

        stimulus_table = PatternedOptogeneticStimulusTable(
            name="PatternedOptogeneticStimulusTable",
            description="description",
        )

        start_time = 0.0
        stop_time = 1.0

        targets = mock_OptogeneticStimulusTarget(nwbfile=self.nwbfile)
        power = np.random.uniform(50e-3, 70e-3, targets.targeted_rois.shape[0])

        interval_parameter = dict(
            start_time=start_time,
            stop_time=stop_time,
            power=power,
            stimulus_pattern=mock_OptogeneticStimulus2DPattern(nwbfile=self.nwbfile),
            targets=targets,
            stimulus_site=mock_PatternedOptogeneticStimulusSite(nwbfile=self.nwbfile),
        )

        with self.assertRaises(ValueError):
            stimulus_table.add_interval(**interval_parameter)

    def test_constructor_add_interval_power_per_roi(self):
        """Test that the constructor for PatternedOptogeneticStimulusTable sets values as expected,
        using add_interval() function."""

        stimulus_table = PatternedOptogeneticStimulusTable(
            name="PatternedOptogeneticStimulusTable",
            description="description",
        )

        start_time = 0.0
        stop_time = 1.0

        targets = mock_OptogeneticStimulusTarget(nwbfile=self.nwbfile)
        power_per_roi = np.random.uniform(50e-3, 70e-3, targets.targeted_rois.shape[0])
        frequency_per_roi = np.random.uniform(20.0, 100.0, targets.targeted_rois.shape[0])
        pulse_width_per_roi = np.random.uniform(0.1, 0.2, targets.targeted_rois.shape[0])

        stimulus_table.add_interval(
            start_time=start_time,
            stop_time=stop_time,
            power_per_roi=power_per_roi,
            frequency_per_roi=frequency_per_roi,
            pulse_width_per_roi=pulse_width_per_roi,
            stimulus_pattern=mock_OptogeneticStimulus2DPattern(nwbfile=self.nwbfile),
            targets=targets,
            stimulus_site=mock_PatternedOptogeneticStimulusSite(nwbfile=self.nwbfile),
        )

        self.assertEqual(stimulus_table.name, "PatternedOptogeneticStimulusTable")
        self.assertEqual(stimulus_table.description, "description")
        np.testing.assert_array_equal(stimulus_table.power_per_roi[:], [power_per_roi])
        np.testing.assert_array_equal(stimulus_table.frequency_per_roi[:], [frequency_per_roi])
        np.testing.assert_array_equal(stimulus_table.pulse_width_per_roi[:], [pulse_width_per_roi])

    def test_constructor_add_interval_power_per_roi_fail_for_mismatch_dim(self):
        """Test that the constructor for PatternedOptogeneticStimulusTable fails when defining
        the elements of 'power_per_roi' with a different length with respect to 'targets'
        using add_interval() function."""

        stimulus_table = PatternedOptogeneticStimulusTable(
            name="PatternedOptogeneticStimulusTable",
            description="description",
        )

        start_time = 0.0
        stop_time = 1.0

        targets = mock_OptogeneticStimulusTarget(nwbfile=self.nwbfile)
        power_per_roi = np.random.uniform(50e-3, 70e-3, targets.targeted_rois.shape[0] + 2)
        frequency_per_roi = np.random.uniform(20.0, 100.0, targets.targeted_rois.shape[0])
        pulse_width_per_roi = np.random.uniform(0.1, 0.2, targets.targeted_rois.shape[0])

        interval_parameter = dict(
            start_time=start_time,
            stop_time=stop_time,
            power_per_roi=power_per_roi,
            frequency_per_roi=frequency_per_roi,
            pulse_width_per_roi=pulse_width_per_roi,
            stimulus_pattern=mock_OptogeneticStimulus2DPattern(nwbfile=self.nwbfile),
            targets=targets,
            stimulus_site=mock_PatternedOptogeneticStimulusSite(nwbfile=self.nwbfile),
        )

        with self.assertRaises(ValueError) as context:
            stimulus_table.add_interval(**interval_parameter)

        # Assert that the error message matches the expected one
        expected_error_message = (
            f"'power_per_roi' has {targets.targeted_rois.shape[0]+2} elements but it must have"
            f" {targets.targeted_rois.shape[0]} elements to match the length of 'targeted_rois'."
        )
        self.assertEqual(str(context.exception), expected_error_message)

    def test_constructor_add_interval_power_and_power_per_roi_both_defined_fail(self):
        """Test that the constructor for PatternedOptogeneticStimulusTable fails when defining
        both 'power_per_roi' and 'power', using add_interval() function."""

        stimulus_table = PatternedOptogeneticStimulusTable(
            name="PatternedOptogeneticStimulusTable",
            description="description",
        )

        start_time = 0.0
        stop_time = 1.0

        targets = mock_OptogeneticStimulusTarget(nwbfile=self.nwbfile)
        power_per_roi = np.random.uniform(50e-3, 70e-3, targets.targeted_rois.shape[0])
        power = 50e-3

        interval_parameter = dict(
            start_time=start_time,
            stop_time=stop_time,
            power_per_roi=power_per_roi,
            power=power,
            stimulus_pattern=mock_OptogeneticStimulus2DPattern(nwbfile=self.nwbfile),
            targets=targets,
            stimulus_site=mock_PatternedOptogeneticStimulusSite(nwbfile=self.nwbfile),
        )

        with self.assertRaises(ValueError) as context:
            stimulus_table.add_interval(**interval_parameter)

        # Assert that the error message matches the expected one
        expected_error_message = "Both 'power' and 'power_per_roi' have been defined. Only one of them must be defined."
        self.assertEqual(str(context.exception), expected_error_message)

    def test_constructor_add_interval_power_and_power_per_roi_both_not_defined_fail(self):
        """Test that the constructor for PatternedOptogeneticStimulusTable fails when not defining
        'power_per_roi' or 'power', using add_interval() function."""

        stimulus_table = PatternedOptogeneticStimulusTable(
            name="PatternedOptogeneticStimulusTable",
            description="description",
        )

        start_time = 0.0
        stop_time = 1.0

        targets = mock_OptogeneticStimulusTarget(nwbfile=self.nwbfile)

        interval_parameter = dict(
            start_time=start_time,
            stop_time=stop_time,
            stimulus_pattern=mock_OptogeneticStimulus2DPattern(nwbfile=self.nwbfile),
            targets=targets,
            stimulus_site=mock_PatternedOptogeneticStimulusSite(nwbfile=self.nwbfile),
        )

        with self.assertRaises(ValueError) as context:
            stimulus_table.add_interval(**interval_parameter)

        # Assert that the error message matches the expected one
        expected_error_message = (
            "Neither 'power' nor 'power_per_roi' have been defined. At least one of the two must be defined."
        )
        self.assertEqual(str(context.exception), expected_error_message)


class TestPatternedOptogeneticStimulusTableSimpleRoundtrip(TestCase):
    """Simple roundtrip test for PatternedOptogeneticStimulusTable."""

    def setUp(self):
        self.nwbfile = set_up_nwbfile()
        self.path = "test.nwb"

    def tearDown(self):
        remove_test_file(self.path)

    def test_roundtrip(self):
        """
        Add a PatternedOptogeneticStimulusTable to an NWBFile, write it to file,
        read the file, and test that the PatternedOptogeneticStimulusTable from the
        file matches the original PatternedOptogeneticStimulusTable.
        """

        start_time = VectorData(name="start_time", description="start time", data=[0.0, 0.0, 0.0])
        stop_time = VectorData(name="stop_time", description="stop time", data=[1.0, 1.0, 1.0])
        power = VectorData(name="power", description="power", data=[0.0, 0.0, 0.0])
        frequency = VectorData(name="frequency", description="frequency", data=[0.0, 0.0, 0.0])
        pulse_width = VectorData(name="pulse_width", description="pulse_width", data=[0.0, 0.0, 0.0])
        stimulus_pattern_s = mock_OptogeneticStimulus2DPattern(nwbfile=self.nwbfile)
        stimulus_pattern = VectorData(
            name="stimulus_pattern",
            description="stimulus_pattern",
            data=[stimulus_pattern_s, stimulus_pattern_s, stimulus_pattern_s],
        )
        targets_s = mock_OptogeneticStimulusTarget(nwbfile=self.nwbfile)
        targets = VectorData(name="targets", description="targets", data=[targets_s, targets_s, targets_s])
        stimulus_site_s = mock_PatternedOptogeneticStimulusSite(nwbfile=self.nwbfile)
        stimulus_site = VectorData(
            name="stimulus_site", description="stimulus_site", data=[stimulus_site_s, stimulus_site_s, stimulus_site_s]
        )
        columns = [start_time, stop_time, power, frequency, pulse_width, stimulus_pattern, targets, stimulus_site]

        stimulus_table = PatternedOptogeneticStimulusTable(
            name="PatternedOptogeneticStimulusTable",
            description="description",
            columns=columns,
        )

        self.nwbfile.add_time_intervals(stimulus_table)

        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            self.assertContainerEqual(stimulus_table, read_nwbfile.intervals["PatternedOptogeneticStimulusTable"])

    def test_roundtrip_power_as_array(self):
        """
        Add a PatternedOptogeneticStimulusTable to an NWBFile, write it
        to file, read the file, and test that the PatternedOptogeneticStimulusTable
        from the file matches the original PatternedOptogeneticStimulusTable.
        """

        start_time = VectorData(name="start_time", description="start time", data=[0.0, 0.0, 0.0])
        stop_time = VectorData(name="stop_time", description="stop time", data=[1.0, 1.0, 1.0])

        targets_s = mock_OptogeneticStimulusTarget(nwbfile=self.nwbfile)
        targets = VectorData(name="targets", description="targets", data=[targets_s, targets_s, targets_s])

        per_rois = np.ones((len(targets_s.targeted_rois[:])))
        power_per_roi = VectorData(
            name="power_per_roi", description="power_per_roi", data=[per_rois, per_rois, per_rois]
        )
        stimulus_pattern_s = mock_OptogeneticStimulus2DPattern(nwbfile=self.nwbfile)
        stimulus_pattern = VectorData(
            name="stimulus_pattern",
            description="stimulus_pattern",
            data=[stimulus_pattern_s, stimulus_pattern_s, stimulus_pattern_s],
        )

        stimulus_site_s = mock_PatternedOptogeneticStimulusSite(nwbfile=self.nwbfile)
        stimulus_site = VectorData(
            name="stimulus_site", description="stimulus_site", data=[stimulus_site_s, stimulus_site_s, stimulus_site_s]
        )
        columns = [start_time, stop_time, power_per_roi, stimulus_pattern, targets, stimulus_site]
        stimulus_table = PatternedOptogeneticStimulusTable(
            name="PatternedOptogeneticStimulusTable",
            description="description",
            columns=columns,
        )

        self.nwbfile.add_time_intervals(stimulus_table)

        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            self.assertContainerEqual(stimulus_table, read_nwbfile.intervals["PatternedOptogeneticStimulusTable"])

    def test_roundtrip_add_interval(self):
        """
        Add a PatternedOptogeneticStimulusTable to an NWBFile, write it to file,
        read the file, and test that the PatternedOptogeneticStimulusTable from the
        file matches the original PatternedOptogeneticStimulusTable.
        """

        stimulus_table = PatternedOptogeneticStimulusTable(
            name="PatternedOptogeneticStimulusTable",
            description="description",
        )

        start_time = 0.0
        stop_time = 1.0
        power = 70.0
        frequency = 20.0
        pulse_width = 0.1

        stimulus_table.add_interval(
            start_time=start_time,
            stop_time=stop_time,
            power=power,
            frequency=frequency,
            pulse_width=pulse_width,
            stimulus_pattern=mock_OptogeneticStimulus2DPattern(nwbfile=self.nwbfile),
            targets=mock_OptogeneticStimulusTarget(nwbfile=self.nwbfile),
            stimulus_site=mock_PatternedOptogeneticStimulusSite(nwbfile=self.nwbfile),
        )

        self.nwbfile.add_time_intervals(stimulus_table)

        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            self.assertContainerEqual(stimulus_table, read_nwbfile.intervals["PatternedOptogeneticStimulusTable"])

    def test_roundtrip_add_interval_power_as_array(self):
        """
        Add a PatternedOptogeneticStimulusTable to an NWBFile, write it
        to file, read the file, and test that the PatternedOptogeneticStimulusTable
        from the file matches the original PatternedOptogeneticStimulusTable.
        """

        stimulus_table = PatternedOptogeneticStimulusTable(
            name="PatternedOptogeneticStimulusTable",
            description="description",
        )

        start_time = 0.0
        stop_time = 1.0
        targets = mock_OptogeneticStimulusTarget(nwbfile=self.nwbfile)
        power_per_roi = np.random.uniform(50e-3, 70e-3, targets.targeted_rois.shape[0])
        frequency_per_roi = np.random.uniform(20.0, 100.0, targets.targeted_rois.shape[0])
        pulse_width_per_roi = np.random.uniform(0.1, 0.2, targets.targeted_rois.shape[0])

        stimulus_table.add_interval(
            start_time=start_time,
            stop_time=stop_time,
            power_per_roi=power_per_roi,
            frequency_per_roi=frequency_per_roi,
            pulse_width_per_roi=pulse_width_per_roi,
            stimulus_pattern=mock_OptogeneticStimulus2DPattern(nwbfile=self.nwbfile),
            targets=targets,
            stimulus_site=mock_PatternedOptogeneticStimulusSite(nwbfile=self.nwbfile),
        )

        self.nwbfile.add_time_intervals(stimulus_table)

        with NWBHDF5IO(self.path, mode="w") as io:
            io.write(self.nwbfile)

        with NWBHDF5IO(self.path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()
            self.assertContainerEqual(stimulus_table, read_nwbfile.intervals["PatternedOptogeneticStimulusTable"])


class TestPatternedOptogeneticStimulusTableRoundtripPyNWB(NWBH5IOFlexMixin, TestCase):
    """
    Complex, more complete roundtrip test for PatternedOptogeneticStimulusTable
    using pynwb.testing infrastructure.
    """

    def getContainerType(self):
        return "PatternedOptogeneticStimulusTable"

    def addContainer(self):
        set_up_nwbfile(self.nwbfile)

        stimulus_table = PatternedOptogeneticStimulusTable(
            name="PatternedOptogeneticStimulusTable",
            description="description",
        )

        start_time = 0.0
        stop_time = 1.0
        power = 70.0
        frequency = 20.0
        pulse_width = 0.1

        stimulus_table.add_interval(
            start_time=start_time,
            stop_time=stop_time,
            power=power,
            frequency=frequency,
            pulse_width=pulse_width,
            stimulus_pattern=mock_OptogeneticStimulus2DPattern(nwbfile=self.nwbfile),
            targets=mock_OptogeneticStimulusTarget(nwbfile=self.nwbfile),
            stimulus_site=mock_PatternedOptogeneticStimulusSite(nwbfile=self.nwbfile),
        )

        self.nwbfile.add_time_intervals(stimulus_table)

    def getContainer(self, nwbfile: NWBFile):
        return nwbfile.intervals["PatternedOptogeneticStimulusTable"]
