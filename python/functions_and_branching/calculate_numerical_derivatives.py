import math


def calculate_difference_quotient(function, position, interval=1e-5):

    return (function(position + interval) - function(position - interval)) / (2 * interval)


def test_difference_quotient():

    h = 0.01

    tests = [
        ("exp(x)", math.exp, 0),
        ("exp(-2x)", lambda x: math.exp(-2 * x), 0),
        ("cos(x)", math.cos, 2 * math.pi),
        ("ln(x)", math.log, 1)
    ]

    print(f"{'Function':>10} {'x':>10} {'Approx Derivative':>20}")
    print("-" * 45)

    for name, function, position in tests:

        derivative = calculate_difference_quotient(function, position, h)

        print(f"{name:>10} {position:10.3f} {derivative:20.6f}")


def run_tests():
    test_difference_quotient()


run_tests()
