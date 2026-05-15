"""Final exam script for PHYS 241.

Part 1 fits a Murnaghan equation of state to volume-energy data for diamond
carbon (C, Fd-3m, GGA-PBE), produces an annotated plot, and converts the
fit parameters to conventional units (eV/atom, Angstrom^3/atom, GPa).

Part 2 builds a Hamiltonian matrix for a one-dimensional square-well
potential (N_dim = 90, parameter = 1), extracts the three lowest-energy
eigenvectors of the matrix, and plots them against the spatial grid.
"""

__author__ = "Fabian Anguiano"

from datetime import date

import numpy as np
import matplotlib.pyplot as plt

from read_two_columns_text import read_two_columns_text
from calculate_bivariate_statistics import calculate_bivariate_statistics
from calculate_quadratic_fit import calculate_quadratic_fit
from plot_data_with_fit import plot_data_with_fit
from annotate_plot import annotate_plot
from equations_of_state import fit_equation_of_state
from generate_matrix import generate_matrix
from calculate_lowest_eigenvectors import calculate_lowest_eigenvectors
from convert_units import convert_units


def parse_file_name(filename):
    """Pull chemical symbol, crystal symmetry, and DFT acronym from a filename.

    The expected format is
    ``<chemical>.<crystal_symmetry>.<approximation>.volumes_energies.dat``
    (any leading directory is stripped).

    Parameters:
        filename: str
            Name of the data file.
    Returns:
        chemical_symbol: str
        crystal_symmetry: str
        approximation: str
    """
    base = filename.split('/')[-1]
    parts = base.split('.')
    return parts[0], parts[1], parts[2]


def format_crystal_symmetry(symmetry):
    """Return a mathtext label for a space-group symbol.

    Letters render in italic and the bar appears above the digit.
    'Fd-3m' -> r'$Fd\\bar{3}m$', 'Fm-3m' -> r'$Fm\\bar{3}m$'.
    """
    if symmetry == 'Fd-3m':
        return r'$Fd\bar{3}m$'
    if symmetry == 'Fm-3m':
        return r'$Fm\bar{3}m$'
    return symmetry


def data_to_figure_coords(axes, x_data, y_data):
    """Convert (x, y) in data coordinates to figure-relative coordinates."""
    display = axes.transData.transform((x_data, y_data))
    return axes.figure.transFigure.inverted().transform(display)


def fit_equation_of_state_part1(data_filename, equation_of_state_name,
                                 number_of_fit_points=100):
    """Read, fit, and unit-convert volume-energy data; return everything
    needed by the plotting code."""
    chemical_symbol, crystal_symmetry, approximation = \
        parse_file_name(data_filename)

    # Read the raw data: row 0 is volume (bohr^3/cell), row 1 is energy
    # (Ry/cell)
    raw_data = read_two_columns_text(data_filename)

    # Divide by the number of atoms in the primitive cell
    atoms_per_cell = 2 if crystal_symmetry == 'Fd-3m' else 1
    data_per_atom = raw_data / atoms_per_cell

    # Statistics on the per-atom data (not strictly needed for the plot
    # but the assignment asks for the call)
    _ = calculate_bivariate_statistics(data_per_atom)

    # Quadratic fit gives initial parameters for the Murnaghan fit
    quadratic_coefficients = calculate_quadratic_fit(data_per_atom)

    # Murnaghan fit on the atomic-unit data
    eos_energy_curve, eos_parameters = fit_equation_of_state(
        data_per_atom[0], data_per_atom[1],
        quadratic_coefficients,
        equation_of_state=equation_of_state_name,
        number_of_points=number_of_fit_points,
    )
    eos_volume_curve = np.linspace(
        data_per_atom[0, 0], data_per_atom[0, -1],
        num=number_of_fit_points,
    )

    # Unit conversion: bohr^3 -> Angstrom^3, Ry -> eV, Ry/bohr^3 -> GPa
    data_converted = np.vstack((
        convert_units(data_per_atom[0],
                      'cubic_bohr_per_atom', 'cubic_angstroms_per_atom'),
        convert_units(data_per_atom[1],
                      'rydberg_per_atom', 'electron_volts_per_atom'),
    ))
    fit_curve_converted = np.vstack((
        convert_units(eos_volume_curve,
                      'cubic_bohr_per_atom', 'cubic_angstroms_per_atom'),
        convert_units(eos_energy_curve,
                      'rydberg_per_atom', 'electron_volts_per_atom'),
    ))
    equilibrium_volume = convert_units(
        eos_parameters[3],
        'cubic_bohr_per_atom', 'cubic_angstroms_per_atom',
    )
    bulk_modulus = convert_units(
        eos_parameters[1],
        'rydberg_per_cubic_bohr', 'gigapascals',
    )

    return {
        'chemical_symbol': chemical_symbol,
        'crystal_symmetry': crystal_symmetry,
        'approximation': approximation,
        'data': data_converted,
        'fit_curve': fit_curve_converted,
        'equilibrium_volume': equilibrium_volume,
        'bulk_modulus': bulk_modulus,
    }


def render_equation_of_state_plot(fit_result, equation_of_state_name,
                                   signature, display_graph, output_filename):
    """Build the annotated equation-of-state figure for Part 1."""
    figure = plt.figure(figsize=(8, 6))
    axes = figure.add_subplot(1, 1, 1)

    plot_data_with_fit(
        fit_result['data'], fit_result['fit_curve'],
        data_format='bo', fit_format='k-',
    )

    # Axes 10% beyond the data range on every side
    minimum_x = np.min(fit_result['data'][0])
    maximum_x = np.max(fit_result['data'][0])
    minimum_y = np.min(fit_result['data'][1])
    maximum_y = np.max(fit_result['data'][1])
    range_x = maximum_x - minimum_x
    range_y = maximum_y - minimum_y
    x_left = minimum_x - 0.1 * range_x
    x_right = maximum_x + 0.1 * range_x
    y_bottom = minimum_y - 0.1 * range_y
    y_top = maximum_y + 0.1 * range_y
    axes.set_xlim(x_left, x_right)
    axes.set_ylim(y_bottom, y_top)

    # Axis labels with mathtext (italic E, V; roman units)
    axes.set_xlabel(r'$V$ (Å$^3$/atom)')
    axes.set_ylabel(r'$E$ (eV/atom)')

    # Dashed vertical line at the equilibrium volume, from the bottom of the
    # axes up to the minimum of the fit curve
    equilibrium_volume = fit_result['equilibrium_volume']
    fit_minimum_energy = np.min(fit_result['fit_curve'][1])
    axes.plot(
        [equilibrium_volume, equilibrium_volume],
        [y_bottom, fit_minimum_energy],
        'k--',
    )

    # Title
    axes.set_title(
        f"{equation_of_state_name.capitalize()} Equation of State for "
        f"{fit_result['chemical_symbol']} in DFT "
        f"{fit_result['approximation']}"
    )

    # Now figure out figure-relative positions for the annotations. The
    # axes must already be laid out so we draw the canvas once.
    figure.canvas.draw()

    chemical_position = data_to_figure_coords(
        axes,
        x_left + 0.04 * (x_right - x_left),
        y_top - 0.04 * (y_top - y_bottom),
    )
    # Crystal symmetry above the curve's minimum (which is at V_0), and
    # the bulk modulus a step further above it, both staying inside the
    # axes box so they do not collide with the title.
    middle_x = 0.5 * (x_left + x_right)
    interior_top_y = y_top - 0.05 * (y_top - y_bottom)
    symmetry_y = (
        fit_minimum_energy
        + 0.50 * (interior_top_y - fit_minimum_energy)
    )
    bulk_modulus_y = (
        fit_minimum_energy
        + 0.78 * (interior_top_y - fit_minimum_energy)
    )
    symmetry_position = data_to_figure_coords(axes, middle_x, symmetry_y)
    bulk_modulus_position = data_to_figure_coords(
        axes, middle_x, bulk_modulus_y,
    )
    volume_label_y = 0.5 * (y_bottom + fit_minimum_energy)
    volume_label_position = data_to_figure_coords(
        axes,
        equilibrium_volume + 0.015 * (x_right - x_left),
        volume_label_y,
    )

    annotations = {
        fit_result['chemical_symbol']: {
            'position': chemical_position,
            'alignment': ('left', 'top'),
            'fontsize': 18.0,
        },
        f"$K_0$ = {fit_result['bulk_modulus']:.1f} GPa": {
            'position': bulk_modulus_position,
            'alignment': ('center', 'center'),
            'fontsize': 11.0,
        },
        format_crystal_symmetry(fit_result['crystal_symmetry']): {
            'position': symmetry_position,
            'alignment': ('center', 'center'),
            'fontsize': 13.0,
        },
        (f"$V_0$ = {fit_result['equilibrium_volume']:.2f} "
         r"Å$^3$/atom"): {
            'position': volume_label_position,
            'alignment': ('left', 'center'),
            'fontsize': 10.0,
        },
        signature: {
            'position': np.array([0.02, 0.02]),
            'alignment': ('left', 'bottom'),
            'fontsize': 8.0,
        },
    }
    annotate_plot(annotations)

    if display_graph:
        plt.show()
    else:
        plt.savefig(output_filename)
    plt.close(figure)


def render_wavefunctions_plot(potential_name, number_of_dimensions,
                               potential_parameter, selected_indices,
                               minimum_x, maximum_x,
                               signature, display_graph, output_filename):
    """Build the wavefunctions figure for Part 2."""
    matrix = generate_matrix(
        minimum_x, maximum_x, number_of_dimensions,
        potential_name, potential_parameter,
    )
    number_of_eigenvectors = max(selected_indices) + 1
    eigenvalues, eigenvectors = calculate_lowest_eigenvectors(
        matrix, number_of_eigenvectors=number_of_eigenvectors,
    )

    spatial_grid = np.linspace(minimum_x, maximum_x, number_of_dimensions)

    # The ground-state wavefunction should be drawn positive; flip it if
    # its components came out negative
    if 0 in selected_indices and np.sum(eigenvectors[0]) < 0:
        eigenvectors[0] = -eigenvectors[0]

    figure = plt.figure(figsize=(8, 6))
    axes = figure.add_subplot(1, 1, 1)

    contrasting_colors = ['tab:red', 'tab:green', 'tab:blue',
                          'tab:orange', 'tab:purple']
    largest_component = 0.0
    for plot_index, eigen_index in enumerate(selected_indices):
        vector = eigenvectors[eigen_index]
        largest_component = max(largest_component, np.max(np.abs(vector)))
        axes.plot(
            spatial_grid, vector,
            color=contrasting_colors[plot_index % len(contrasting_colors)],
            linestyle='-',
            label=(rf'$\psi_{{{eigen_index}}}$, '
                   rf'$E_{{{eigen_index}}}$ = '
                   rf'{eigenvalues[eigen_index]:.3f} a.u.'),
        )

    axes.axhline(y=0.0, color='black', linestyle='-')
    axes.set_xlabel(r'$x$ [a.u.]')
    axes.set_ylabel(r'$\psi_n(x)$ [a.u.]')
    axes.set_ylim(-2.0 * largest_component, 2.0 * largest_component)
    axes.legend(loc='upper right')

    axes.set_title(
        f'Select Wavefunctions for {potential_name.capitalize()} '
        f'Potential on a Spatial Grid of {number_of_dimensions} Points'
    )

    annotate_plot({
        signature: {
            'position': np.array([0.02, 0.02]),
            'alignment': ('left', 'bottom'),
            'fontsize': 8.0,
        },
    })

    if display_graph:
        plt.show()
    else:
        plt.savefig(output_filename)
    plt.close(figure)


if __name__ == '__main__':
    # Set to False to write PNG files, True to view interactively.
    display_graph = True

    today_iso = date.today().isoformat()
    signature = f'Created by Fabian Anguiano {today_iso}'

    # ------------------------------------------------------------------
    # Part 1: Fit an equation of state to volume-energy data
    # ------------------------------------------------------------------
    data_filename = 'C.Fd-3m.GGA-PBE.volumes_energies.dat'
    equation_of_state_name = 'murnaghan'

    fit_result = fit_equation_of_state_part1(
        data_filename, equation_of_state_name,
    )

    eos_plot_filename = (
        f"Anguiano.{fit_result['chemical_symbol']}."
        f"{fit_result['crystal_symmetry']}."
        f"{fit_result['approximation']}."
        f"{equation_of_state_name.capitalize()}EquationOfState.png"
    )
    render_equation_of_state_plot(
        fit_result, equation_of_state_name,
        signature, display_graph, eos_plot_filename,
    )

    # ------------------------------------------------------------------
    # Part 2: Visualise wavefunctions on a spatial grid
    # ------------------------------------------------------------------
    potential_name = 'square'
    number_of_dimensions = 90
    potential_parameter = 1.0
    selected_indices = [0, 1, 2]
    minimum_x = -10.0
    maximum_x = 10.0

    indices_string = '_'.join(str(i) for i in selected_indices)
    wavefunctions_plot_filename = (
        f'Anguiano.{potential_name.capitalize()}.'
        f'Eigenvector{indices_string}.png'
    )
    render_wavefunctions_plot(
        potential_name, number_of_dimensions, potential_parameter,
        selected_indices, minimum_x, maximum_x,
        signature, display_graph, wavefunctions_plot_filename,
    )
