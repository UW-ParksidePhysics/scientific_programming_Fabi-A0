a = 3.3
b = 5.3

a2 = a**2
b2 = b**2

binomial_sum_squared_terms = a2 + 2*a*b + b2
binomial_difference_squared_terms = a2 - 2*a*b + b2

binomial_sum_squared = (a + b)**2
binomial_difference_squared = (a - b)**2

print(f"First equation: {binomial_sum_squared:.1f} = {binomial_sum_squared_terms:.1f}")
print(f"Second equation: {binomial_difference_squared:.1f} = {binomial_difference_squared_terms:.1f}")
