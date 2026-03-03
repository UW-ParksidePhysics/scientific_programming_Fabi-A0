maximum_integer = 100

# Compute sum using a for loop
summation = 0
for index in range(1, maximum_integer + 1):
    summation += index

# Compute sum using the formula
formula_sum = maximum_integer * (maximum_integer + 1) / 2

print("n =", maximum_integer)
print("sum(1, n) =", summation)
print("n(n+1)/2 =", formula_sum)
