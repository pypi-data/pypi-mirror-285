"""Test roundtrip (write and read back) of the Python API for the ndx-subjects extension."""

import pytest
from ndx_subjects.testing import mock_CElegansSubject
from pynwb.testing import TestCase as pynwb_TestCase
from pynwb.testing.mock.file import mock_NWBFile

import pynwb


class TestCElegansSubjectSimpleRoundtrip(pynwb_TestCase):
    """Simple roundtrip test for CElegansSubject."""

    def setUp(self):
        self.nwbfile_path = "test_c_elegans_subject_roundtrip.nwb"

    def tearDown(self):
        pynwb.testing.remove_test_file(self.nwbfile_path)

    def test_roundtrip(self):
        c_elegans_subject = mock_CElegansSubject()

        nwbfile = mock_NWBFile(subject=c_elegans_subject)

        with pynwb.NWBHDF5IO(path=self.nwbfile_path, mode="w") as io:
            io.write(nwbfile)

        with pynwb.NWBHDF5IO(path=self.nwbfile_path, mode="r", load_namespaces=True) as io:
            read_nwbfile = io.read()

            self.assertContainerEqual(c_elegans_subject, read_nwbfile.subject)


if __name__ == "__main__":
    pytest.main()  # Required since not a typical package structure
