# Table of t and y(t)
#
# y(t) = v0*t - (1/2)*g*t^2
#
# n + 1 uniformly spaced t values
# interval [0, 2*v0/g]


# pick two solid objects
solid_objects = ['Earth', 'Moon']
gravitational_accelerations = [9.81, 1.63]  # m/s^2

# pick positive initial velocity v0
initial_velocity = 5.0  # m/s

# Set the number of intervals (n)
number_of_times = 9

# Store times and positions for each object
all_times = []
all_positions = []

for g in gravitational_accelerations:
    # End of the time interval
    end_time = 2 * initial_velocity / g

    # n + 1 times from 0 to end_time
    times = []
    for index in range(number_of_times + 1):
        t = index * end_time / number_of_times
        times.append(t)

    # positions at those times
    positions = []
    for t in times:
        y = initial_velocity * t - 0.5 * g * t**2
        positions.append(y)

    all_times.append(times)
    all_positions.append(positions)

# Print the table header
print(f"For initial velocity of {initial_velocity:.2f} m/s:")
print("-" * 62)

header_string = ""
for solid_object, g in zip(solid_objects, gravitational_accelerations):
    header_string += f"{solid_object:13} (g = {g:.2f} m/s/s) "
print(header_string)

print("-" * 62)

# Column headers (t and y for each object)
column_headers = ""
column_underlines = ""

for _ in solid_objects:
    column_headers += " " * 4
    column_headers += "t (s)"
    column_headers += " " * 9
    column_headers += "y (m)"
    column_headers += " " * 5

    column_underlines += " " * 4
    column_underlines += "-" * 5
    column_underlines += " " * 9
    column_underlines += "-" * 5
    column_underlines += " " * 5

print(column_headers)
print(column_underlines)

# Print rows (PART A: using a for loop)
for i in range(len(all_times[0])):
    row_values = ""
    for times, positions in zip(all_times, all_positions):
        row_values += f"{times[i]:9.3f}"
        row_values += f"{positions[i]:14.3f}"
        row_values += " " * 5
    print(row_values)

print("\nusing a while loop:")

# PART B: print the SAME table using a while loop
i = 0
while i < len(all_times[0]):
    row_values = ""
    for times, positions in zip(all_times, all_positions):
        row_values += f"{times[i]:9.3f}"
        row_values += f"{positions[i]:14.3f}"
        row_values += " " * 5
    print(row_values)
    i = i + 1
