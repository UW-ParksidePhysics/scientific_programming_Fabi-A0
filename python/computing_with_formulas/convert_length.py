# I enter 13 Km for my running of the code
# conversions given by the problem
cm_per_inch = 2.54
inches_per_foot = 12
feet_per_yard = 3
yards_per_mile = 1760

# pick your real distance from campus to your home (km)
km = float(input("Enter distance in kilometers: "))

# km -> cm
cm = km * 100000  # because 1 km = 1000 m and 1 m = 100 cm

# cm -> inches
inches = cm / cm_per_inch

# inches -> feet
feet = inches / inches_per_foot

# feet -> yards
yards = feet / feet_per_yard

# yards -> miles
miles = yards / yards_per_mile

print(f"{km} kilometers is equal to:")
print(f"{inches:.2f} inches")
print(f"{feet:.2f} feet")
print(f"{yards:.2f} yards")
print(f"{miles:.4f} miles")
