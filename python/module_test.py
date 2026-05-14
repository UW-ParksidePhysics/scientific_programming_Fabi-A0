import os


modules = [
    'read_two_columns_text',
    'calculate_bivariate_statistics',
    'calculate_quadratic_fit',
    'fit_curve_array',
    'plot_data_with_fit',
    'calculate_lowest_eigenvectors',
    'annotate_plot'
]

for module in modules:
    filename = module + '.py'
    if not os.path.exists(filename):
        with open(filename, 'w') as file:
            file.write('')
    with open(filename) as module_file:
        exec(module_file.read())
