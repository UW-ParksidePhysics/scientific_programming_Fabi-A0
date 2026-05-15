"""
Contains energy-volume equations of state together with a function for fitting them
given energy-volume data and starting-guess coefficients
"""

__author__ = 'Ryan Glusic and William Parker'

import numpy as np


def fit_equation_of_state(volumes, energies, quadratic_coefficients, equation_of_state='vinet', number_of_points=50):
    """
    Returns a NumPy array of values evaluated to an equation of state fit
    :param volumes:                 NumPy array(N) :: volumes (x-values) to be fit
    :param energies:                NumPy array(N) :: energies (y-values) to be fit
    :param quadratic_coefficients:  list(3) :: coefficients of the quadratic polynomial already fit to the data
    :param equation_of_state:                     str :: equation of state name ('murnaghan', 'birch-murnaghan', 'vinet')
    :param number_of_points:        int, optional :: number of points to evaluate fit function on
    :return:                        NumPy array(number_of_points) :: equation of state fit evaluated on grid,

    starting at volumes[0] and ending at volume[-1]
    """
    from scipy.optimize import curve_fit

    # Dictionary holding lambda functions from current module.
    lambda_dictionary = {
        'vinet': globals()['vinet'],
        'murnaghan': globals()['murnaghan'],
        'birch-murnaghan': globals()['birch_murnaghan']
    }

    # Get extremes of data and calculate range

    minimum_volume = np.amin(volumes)
    maximum_volume = np.amax(volumes)

    # for y = c0 + c1 x + c2 x^2
    #   axis of symmetry: x = -c1 / (2 c2)
    quadratic_axis_of_symmetry = -quadratic_coefficients[1] / (2 * quadratic_coefficients[2])
    #   minimum: y = -c1^2 / (4 c2)  + c0
    quadratic_minimum = -quadratic_coefficients[1] ** 2 / (4 * quadratic_coefficients[2]) + quadratic_coefficients[0]
    #   bulk modulus: K_0 = 2 * a / V_0 for E(V) = c2*V^2 + c1*V + E0
    quadratic_bulk_modulus = 2. * quadratic_coefficients[2] / quadratic_axis_of_symmetry

    bulk_modulus_derivative = 3.7

    # Get realistic equation of state fit

    initial_parameters = [quadratic_minimum, quadratic_bulk_modulus,
                          bulk_modulus_derivative, quadratic_axis_of_symmetry]

    equation_parameters, equation_covariances = curve_fit(lambda_dictionary[equation_of_state.lower()], volumes, energies,
                                                p0=initial_parameters, method='trf')  # ,
    # x_scale=[10**np.floor(np.log10(np.amin(np.abs(energies)))), 100, 1,
    #         10**np.floor(np.log10(np.amin(np.abs(volumes))))])
    fit_curve_volumes = np.linspace(minimum_volume, maximum_volume, num=number_of_points)
    equation_fit_curve = lambda_dictionary[equation_of_state.lower()](fit_curve_volumes,
                                                                 equation_parameters[0], equation_parameters[1], equation_parameters[2],
                                                                 equation_parameters[3])

    return equation_fit_curve, equation_parameters


def murnaghan(volumes, equilibrium_energy, bulk_modulus, bulk_modulus_derivative, equilibrium_volume):
    """
    Murnaghan equation of state: E(V) = E_0 + K_0 V_0 [ (1 / (K_0' (K_0' - 1))) (V / V_0)^(-(K_0' - 1)) +
                                                        (1 / K_0') (V / V_0) -

                                                        (1 / (K_0' - 1)) ]

    :param volumes:                 NumPy array of volumes per atom

    :param equilibrium_energy:      equilibrium energy E_0

    :param bulk_modulus:            bulk modulus K_0 = ∂^E/(∂V)^2 / V_0

    :param bulk_modulus_derivative: pressure derivative of bulk modulus ∂K_0/∂P

    :param equilibrium_volume:      equilibrium volume V_0

    :return:                        NumPy array of Murnaghan equation of state values at input volumes
    """
    k0pm1 = bulk_modulus_derivative - 1.0  # K_0' - 1
    return equilibrium_energy + (bulk_modulus * equilibrium_volume *
                                 (((1.0 / (bulk_modulus_derivative * k0pm1)) *
                                   np.power((volumes / equilibrium_volume), (-k0pm1))) +
                                  (volumes / (bulk_modulus_derivative * equilibrium_volume)) - (1.0 / k0pm1)))


def birch_murnaghan(volumes, equilibrium_energy, bulk_modulus, bulk_modulus_derivative, equilibrium_volume):
    """
    Birch-Murnaghan equation of state: E(V) = E_0 + (9/16) K_0 V_0 {[ (V / V_0)^(-(2/3)) - 1 ]^3 K_0' +
                                                                    [ (V / V_0)^(-(2/3)) - 1]^2 *
                                                                    [ 6 - 4 (V / V_0)^(-(2/3)) ]}

    :param volumes:                 NumPy array of volumes per atom

    :param equilibrium_energy:      equilibrium energy E_0

    :param bulk_modulus:            bulk modulus K_0 = ∂^E/(∂V)^2 / V_0

    :param bulk_modulus_derivative: pressure derivative of bulk modulus ∂K_0/∂P

    :param equilibrium_volume:      equilibrium volume V_0

    :return:                        NumPy array of the Birch-Murnaghan equation of state values at input volumes
    """
    reduced_volume_area = np.power(volumes / equilibrium_volume, -2. / 3.)
    return equilibrium_energy + (9. * bulk_modulus * equilibrium_volume / 16.) * (
            np.power(reduced_volume_area - 1., 3.) * bulk_modulus_derivative +
            np.power(reduced_volume_area - 1., 2.) * (6. - 4. * reduced_volume_area))


def vinet(volumes, equilibrium_energy, bulk_modulus, bulk_modulus_derivative, equilibrium_volume):
    """
    Vinet equation of state: E(V) = E_0 + (2 K_0 V_0 / (K_0' - 1)^2) *
                                        - {2 - [5 + 3 (V / V_0)^(1/3) (K_0' - 1) - 3 K_0']
                                               exp(- (3/2) (K_0' - 1) (1 - (V / V_0)^(1/3))})

    :param volumes:                 NumPy array of volumes per atom

    :param equilibrium_energy:      equilibrium energy E_0

    :param bulk_modulus:            bulk modulus K_0 = ∂^E/(∂V)^2 / V_0

    :param bulk_modulus_derivative: pressure derivative of bulk modulus ∂K_0/∂P

    :param equilibrium_volume:      equilibrium volume V_0

    :return: NumPy array of the Vinet equation of state values at input volumes
    """
    k0pm1 = bulk_modulus_derivative - 1  # K_0' - 1
    k0pm1_squared = np.power(k0pm1, 2)
    reduced_volume_lengths = np.cbrt(volumes / equilibrium_volume)

    exponential_argument = -1.5 * k0pm1 * (reduced_volume_lengths - 1.)
    try:
        exponential_factor = np.exp(exponential_argument)
        vinet_eos = equilibrium_energy + \
                    (2. * bulk_modulus * equilibrium_volume / k0pm1_squared) * \
                    (2. - (5. + 3. * reduced_volume_lengths * k0pm1 - 3 * bulk_modulus_derivative) *
                     exponential_factor)
    except:
        # assuming the failure is the exponential factor
        vinet_eos = equilibrium_energy + \
                    (2. * bulk_modulus * equilibrium_volume / k0pm1_squared) * \
                    (2. - (5. + 3. * reduced_volume_lengths * k0pm1 - 3 * bulk_modulus_derivative))

    return vinet_eos


if __name__ == "__main__":
    # import matplotlib
    # matplotlib.use('macosx')

    import matplotlib.pyplot as plt

    fit_point_number = 50
    test_energies = np.array([-18, -21, -22, -21, -18.5])

    test_volumes = np.array([10, 11, 12, 13, 14])
    starting_coefficients = np.polynomial.polynomial.polyfit(test_volumes, test_energies, 2)

    equations_of_state = ['murnaghan', 'birch-murnaghan', 'vinet']
    figures, axes = plt.subplots(nrows=len(equations_of_state))

    for index, equation_form in enumerate(equations_of_state):
        equation_of_state, equation_parameters = fit_equation_of_state(test_volumes, test_energies, starting_coefficients, equation_of_state=equation_form,
                                                                       number_of_points=fit_point_number)
        axes[index].plot(np.linspace(10, 14, num=fit_point_number), equation_of_state)
        axes[index].scatter(test_volumes, test_energies)
        axes[index].text(12, -19, equation_form.title(), ha='center', va='center')
        axes[index].set(xlabel=r'$V$', ylabel=r'$E$')
    plt.show()
