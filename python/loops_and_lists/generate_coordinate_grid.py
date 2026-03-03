a = 1
b = 2
n = 20

h = (b - a) / n

print("For x in [", a, ",", b, "] with", n, "intervals, the interval length is h =", h)
print("Using a for loop:")

x_values = []
for i in range(n + 1):
    x = a + i * h
    x_values.append(round(x, 2))

print("x =", x_values)

print("Using list comprehension:")

x_list_comp = [round(a + i * h, 2) for i in range(n + 1)]

print("x =", x_list_comp)
