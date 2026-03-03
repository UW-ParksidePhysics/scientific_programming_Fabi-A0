F = 0

print(f"{'F':>6} {'C_exact':>10} {'C_approx':>12}")
print("-" * 30)

while F <= 100:
    C_exact = (F - 32) * 5.0 / 9.0
    C_approx = (F - 30) / 2.0

    print(f"{F:6.0f} {C_exact:10.2f} {C_approx:12.2f}")

    F = F + 10
