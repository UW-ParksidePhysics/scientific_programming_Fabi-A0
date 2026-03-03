F = 0

print(f"{'F':>6} {'C':>8}")

print("-" * 14)

while F <= 100:
    C = (F - 32) * 5.0 / 9.0
    print(F, C)
    F = F + 10
