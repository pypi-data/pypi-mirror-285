"""Test in-memory Python API constructors for the ndx-subjects extension."""

import pytest
from ndx_subjects.testing import mock_CElegansSubject


def test_constructor_c_elegans_subject():
    mock_CElegansSubject()


if __name__ == "__main__":
    pytest.main()  # Required since not a typical package structure
