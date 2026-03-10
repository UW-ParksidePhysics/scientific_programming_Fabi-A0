import math


def compute_smoothed_heaviside(position, epsilon=0.01):

    if position < -epsilon:
        return 0

    elif -epsilon <= position <= epsilon:
        return 0.5 + position/(2 * epsilon) + (1/(2 * math.pi)) * math.sin(math.pi * position / epsilon)

    else:
        return 1


epsilon = 0.01
test_positions = [-0.02, -epsilon, 0, epsilon, 0.02]

print(f"{'x':>10} {'H_e(x)':>15}")
print("-" * 26)

for position in test_positions:
    value = compute_smoothed_heaviside(position, epsilon)
    print(f"{position:10.3f} {value:15.6f}")
