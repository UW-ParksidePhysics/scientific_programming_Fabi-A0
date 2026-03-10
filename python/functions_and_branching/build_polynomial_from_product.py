def construct_polynomial_from_roots(x, roots):

    product = 1

    for r in roots:
        product = product * (x - r)

    return product


print(f"{'x':>6} {'p(x)':>10}")
print("-" * 18)

roots = [1, 2, 3]

test_values = [0, 1, 2, 3, 4]

for x in test_values:

    value = construct_polynomial_from_roots(x, roots)

    print(f"{x:6} {value:10}")
