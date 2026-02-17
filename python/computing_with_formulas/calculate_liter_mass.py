# 1 liter = 1000 cm^3
V = 1000  # cm^3

# densities in g/cm^3
iron = 7.87
air = 0.0012
gasoline = 0.755
ice = 0.9167
human_body = 1.1
silver = 10.50
platinum = 21.45

mass_iron = iron * V
mass_air = air * V
mass_gasoline = gasoline * V
mass_ice = ice * V
mass_human_body = human_body * V
mass_silver = silver * V
mass_platinum = platinum * V

print("Mass of 1 liter (in grams):")
print("Iron =", mass_iron, "g")
print("Air =", mass_air, "g")
print("Gasoline =", mass_gasoline, "g")
print("Ice =", mass_ice, "g")
print("Human body =", mass_human_body, "g")
print("Silver =", mass_silver, "g")
print("Platinum =", mass_platinum, "g")
