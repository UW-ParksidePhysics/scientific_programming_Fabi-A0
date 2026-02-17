initial_velocity = 3  # m/s
time = 1  # s
acceleration = 2  # m/s**2

displacement = initial_velocity * time + 0.5 * acceleration * time**2

print(f's(t = {time:.0f} s) = {displacement:.1f} m')
