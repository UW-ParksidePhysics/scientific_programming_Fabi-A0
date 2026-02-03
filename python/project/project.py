#### RENAME THIS FILE
# Rename `project.py` to `(your_project_short_name).py`
# Example: `orbit_simulation.py`, `wave_packet.py`, `two_body_problem.py`

# -----------------------------------------------------------------------------
# PROJECT FILE STRUCTURE (CONTEMPORARY PYTHON BEST PRACTICES)
# -----------------------------------------------------------------------------
# The goal is clarity, testability, and “import safety” (importing your module
# should NOT start the simulation or pop up plots).
#
# Recommended top-to-bottom order:
# 1) Module docstring (100–200 words): what the project does, key assumptions,
#    inputs/outputs, and how to run it.
# 2) Imports (grouped per PEP 8).
# 3) Module-level constants (only if truly global and stable).
# 4) Function definitions (each with a PEP 257-compliant docstring).
# 5) main() function: the single clear entry point for running the program.
# 6) Script guard: if __name__ == "__main__": main()
#
# References:
# - PEP 8 (imports and general style): https://peps.python.org/pep-0008/  (see “Imports”)
# - SciPy physical constants (use inside functions when appropriate):
#   https://docs.scipy.org/doc/scipy/reference/constants.html
#
# -----------------------------------------------------------------------------
# IMPORTS: ORDER + PRACTICES (PEP 8)
# -----------------------------------------------------------------------------
# Put imports at the top, after the module docstring, before constants.
# Group imports in THIS order, separated by blank lines:
#   1) Standard library imports (e.g., math, pathlib, dataclasses)
#   2) Third-party imports (e.g., numpy, scipy, matplotlib, plotly)
#   3) Local/project imports (your own modules in this repo/package)
#
# Examples:
#   # 1) Standard library
#   from __future__ import annotations
#   from dataclasses import dataclass
#   from pathlib import Path
#
#   # 2) Third-party
#   import numpy as np
#   from scipy import constants as scipy_constants
#
#   # 3) Local imports (if your project is a package)
#   # from .helpers import integrate
#
# Avoid:
# - wildcard imports: `from module import *`
# - hiding heavy work at import time (reading big files / launching plots)
#
# -----------------------------------------------------------------------------
# SIMULATION / VISUALIZATION FUNCTIONS (FUNCTIONAL STYLE)
# -----------------------------------------------------------------------------
# Keep “work” inside functions. This makes your code testable and reusable.
#
# Typical breakdown:
# - read_data(...): load/validate input data
# - compute_derived_parameters(...): compute values that depend on inputs
# - simulate(...): compute arrays / time series (no plotting)
# - build_figure(...): create a plot/animation object (no file I/O)
# - save_outputs(...): optional, write files if required
#
# Each function must have:
# - clear, full-word parameter names (PEP 8: lower_case_with_underscores)
# - units in comments or docstrings (meters, seconds, kg, etc.)
# - a docstring describing: parameters, returns, and assumptions
#
# -----------------------------------------------------------------------------
# SciPy CONSTANTS: WHERE TO USE THEM
# -----------------------------------------------------------------------------
# Prefer importing SciPy constants inside the function that uses them, so the
# dependency is obvious and to keep module import fast/lightweight.
#
# Example pattern (inside a function):
#   from scipy import constants as scipy_constants
#   speed_of_light = scipy_constants.c
#
# Docs: https://docs.scipy.org/doc/scipy/reference/constants.html
#
# -----------------------------------------------------------------------------
# main(): THE STANDARD ENTRY POINT
# -----------------------------------------------------------------------------
# It is now standard practice to put the “run the program” logic in a main()
# function and call it under the script guard. This prevents side effects when
# importing your module.
#
# Skeleton:
#   def main() -> None:
#       """Run the simulation and display/save results."""
#       # 1) Define simulation parameters (with units)
#       # 2) Compute derived parameters
#       # 3) Call read_data / simulate / build_figure
#       # 4) Show or save outputs
#
#   if __name__ == "__main__":
#       main()
#
# -----------------------------------------------------------------------------
# PRIMARY SIMULATION FUNCTION STRUCTURE (SUGGESTED)
# -----------------------------------------------------------------------------
# Inside your primary simulation function (often called by main()):
# 1) Parameters (named clearly, units documented)
# 2) Derived parameters (computed from inputs)
# 3) Call helpers for:
#    - data read-in / validation
#    - simulation computation
#    - visualization creation
# 4) Return results (arrays, figure objects) instead of printing everything
#
# Keep plotting separate from physics/math wherever practical.