from math import pi
    
height = 5.0  # cm
base = 2.0    # cm
radius = 1.5  # cm
        
parallelogram_area = height * base
print(f'The area of a parallelogram of height {height} and base {base} cm is {parallelogram_area:3.2f} cm^2')
    
square_area = base**2
print(f'The area of a square of base {base} cm is {parallelogram_area:3.2f} cm^2')
    
circle_area = pi * radius**2
print(f'The area of a circle of radius {radius} cm is {circle_area:3.2f} cm^2')
    
cone_volume = (1./3) * pi * radius**2 * height
print(f'The volume of a cone of radius {radius} cm and height {height} cm is {cone_volume:3.2f} cm^3')
