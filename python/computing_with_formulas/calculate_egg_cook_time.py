from math import pi, log

# Constants
rho = 1.038          # g/cm^3
c = 3.7              # J/(g K)
k = 5.4e-3           # W/(cm K)  (same as J/(s cm K))
Tw = 100             # C (boiling water)
Ty = 70              # C (target yolk temperature)

# Egg masses
small_egg_mass = 47  # g
large_egg_mass = 67  # g

# Starting temperatures
fridge_temp = 4      # C
room_temp = 20       # C

def cook_time_seconds(mass, To):
    # t = [m^(2/3) * c * rho^(1/3)] / [k * pi^2 * (4*pi/3)^(2/3)] * ln( 0.76 * (To-Tw)/(Ty-Tw) )

    numerator = (mass ** (2/3)) * c * (rho ** (1/3))
    denominator = k * (pi ** 2) * ((4 * pi / 3) ** (2/3))
    ln_part = log(0.76 * (To - Tw) / (Ty - Tw))

    t = (numerator / denominator) * ln_part
    return t

# Four Egg Types
cases = [
    ("Small egg from fridge", small_egg_mass, fridge_temp),
    ("Small egg from room temp", small_egg_mass, room_temp),
    ("Large egg from fridge", large_egg_mass, fridge_temp),
    ("Large egg from room temp", large_egg_mass, room_temp),
]

for label, mass, To in cases:
    t_seconds = cook_time_seconds(mass, To)
    t_minutes = t_seconds / 60
    print(f"{label}: cook time = {t_seconds:.0f} s = {t_minutes:.1f} min")
