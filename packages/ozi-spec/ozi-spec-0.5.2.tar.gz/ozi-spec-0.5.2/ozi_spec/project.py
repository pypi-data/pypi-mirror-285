# ozi/spec/project.py
# Part of the OZI Project.
# See LICENSE.txt for license information.
# SPDX-License-Identifier: Unlicense
"""Project specification metadata."""
from dataclasses import dataclass

from ozi_spec.base import Default
from ozi_spec.ci import CI
from ozi_spec.ci import Build
from ozi_spec.ci import CheckpointSuite
from ozi_spec.ci import ClassicDist
from ozi_spec.ci import ClassicLint
from ozi_spec.ci import ClassicTest
from ozi_spec.ci import RuffLint
from ozi_spec.pkg import Pkg
from ozi_spec.python import Support
from ozi_spec.src import Src


@dataclass(slots=True, frozen=True, eq=True, repr=False)
class PythonProject(Default):
    """Base class for Python Project specification metadata."""

    ci: CI = CI()
    support: Support = Support()
    dist: CheckpointSuite = ClassicDist()
    lint: CheckpointSuite = ClassicLint()
    test: CheckpointSuite = ClassicTest()
    build: Build = Build()
    pkg: Pkg = Pkg()
    src: Src = Src()


@dataclass(slots=True, frozen=True, eq=True, repr=False)
class ClassicProject(PythonProject):
    """OZI project using classic Python checkpoint toolchains."""


@dataclass(slots=True, frozen=True, eq=True, repr=False)
class RuffProject(PythonProject):
    """Alternative to classic project using ruff for linting and formatting."""

    lint: RuffLint = RuffLint()
