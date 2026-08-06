"""Tests for OVON core domain models."""

import pytest
import packages.ovon_core as ovon_core

def test_ovon_core_version():
    assert ovon_core.__version__ == "0.1.0"
