from math import pi, sqrt, exp

mean = 0
standard_deviation = 2
input_value = 1

gaussian_value = (1 / (sqrt(2*pi) * standard_deviation)) * exp(
    -0.5 * ((input_value - mean) / standard_deviation)**2
)

print("mean =", mean)
print("standard_deviation =", standard_deviation)
print("input_value =", input_value)
print("gaussian_value =", gaussian_value)
