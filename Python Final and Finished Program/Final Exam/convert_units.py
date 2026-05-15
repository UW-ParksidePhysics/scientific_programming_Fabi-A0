"""Convert between atomic units and conventional units for DFT data."""

__author__ = "Fabian Anguiano"

from scipy import constants


def convert_units(value, from_units, to_units):
    """Convert a value (or NumPy array) from one unit to another.

    Supported conversions
    ---------------------
    Volume per atom:
        'cubic_bohr_per_atom'  <-> 'cubic_angstroms_per_atom'
    Energy per atom:
        'rydberg_per_atom'     <-> 'electron_volts_per_atom'
    Pressure / bulk modulus:
        'rydberg_per_cubic_bohr' <-> 'gigapascals'

    Parameters:
        value: float or ndarray
            The value to be converted.
        from_units: string/name
            The units that ``value`` is currently in.
        to_units: string
            The units to convert ``value`` to.
    Returns:
        converted_value: float or ndarray
            ``value`` expressed in ``to_units``.
    Raises:
        ValueError
            When the requested unit pair is not recognised.
    """
    # Cubic bohr per atom -> cubic angstroms per atom
    # (Bohr radius in m) / (1 Angstrom in m), then cubed
    bohr_to_angstrom = constants.value('Bohr radius') / constants.angstrom
    bohr3_to_angstrom3 = bohr_to_angstrom ** 3

    # Rydberg per atom -> electron volts per atom
    rydberg_to_electron_volt = constants.value(
        'Rydberg constant times hc in eV'
    )

    # Rydberg per cubic bohr -> Pascals -> gigapascals
    rydberg_in_joule = constants.value('Rydberg constant times hc in J')
    bohr_in_meter = constants.value('Bohr radius')
    rydberg_per_bohr3_to_pascal = rydberg_in_joule / bohr_in_meter ** 3
    rydberg_per_bohr3_to_gigapascal = rydberg_per_bohr3_to_pascal / 1.0e9

    forward = {
        ('cubic_bohr_per_atom', 'cubic_angstroms_per_atom'):
            bohr3_to_angstrom3,
        ('rydberg_per_atom', 'electron_volts_per_atom'):
            rydberg_to_electron_volt,
        ('rydberg_per_cubic_bohr', 'gigapascals'):
            rydberg_per_bohr3_to_gigapascal,
    }

    if (from_units, to_units) in forward:
        return value * forward[(from_units, to_units)]
    if (to_units, from_units) in forward:
        return value / forward[(to_units, from_units)]
    if from_units == to_units:
        return value

    raise ValueError(
        f'Conversion from {from_units!r} to {to_units!r} is not supported'
    )


if __name__ == '__main__':
    print('Volume Test 1: 1 cubic bohr per atom in cubic angstroms per atom')
    print('Expected: 0.14818471147216278')
    result = convert_units(1.0, 'cubic_bohr_per_atom',
                           'cubic_angstroms_per_atom')
    print(f'Result:   {result:.18f}')
    print()

    print('Energy Test 2: 1 rydberg per atom in electron volts per atom')
    print('Expected: 13.605693122994')
    result = convert_units(1.0, 'rydberg_per_atom',
                           'electron_volts_per_atom')
    print(f'Result:   {result:.12f}')
    print()

    print('Pressure Test 3: 1 rydberg per cubic bohr in gigapascals')
    print('Expected: 14710.507848260711')
    result = convert_units(1.0, 'rydberg_per_cubic_bohr', 'gigapascals')
    print(f'Result:   {result:.12f}')
