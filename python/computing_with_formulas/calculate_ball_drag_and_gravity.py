from math import pi

# Given constants
drag_coefficient = 0.2              # dimensionless
air_density = 1.2                   # kg/m^3
ball_mass = 0.43                    # kg
gravitational_acceleration = 9.81   # m/s^2
radius = 0.11                       # m (11 cm converted to meters)

# Cross-sectional area A = πa^2
cross_area = pi * radius**2         # m^2

# Hard kick velocity
ball_velocity = 120 * 1000 / 3600   # m/s (converted from km/h)

# Forces for hard kick
drag_force = 0.5 * drag_coefficient * air_density * cross_area * ball_velocity**2
gravitational_force = ball_mass * gravitational_acceleration

print("Hard kick (120 km/h)")
print(f"Velocity = {ball_velocity:.1f} m/s")
print(f"Drag force = {drag_force:.1f} N")
print(f"Gravity force = {gravitational_force:.1f} N")
print(f"Ratio (Drag/Gravity) = {drag_force/gravitational_force:.2f}")
print()

# Soft kick velocity
ball_velocity = 10 * 1000 / 3600    # m/s (converted from km/h)

# Forces for soft kick
drag_force = 0.5 * drag_coefficient * air_density * cross_area * ball_velocity**2

print("Soft kick (10 km/h)")
print(f"Velocity = {ball_velocity:.1f} m/s")
print(f"Drag force = {drag_force:.1f} N")
print(f"Gravity force = {gravitational_force:.1f} N")
print(f"Ratio (Drag/Gravity) = {drag_force/gravitational_force:.2f}")
