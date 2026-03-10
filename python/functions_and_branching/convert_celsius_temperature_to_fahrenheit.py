def convert_celsius_temperature_to_fahrenheit(celsius_temperature):
  """Convert input temperature in degrees Celsius to degrees Fahrenheit."""
  return (9./5)*celsius_temperature + 32

def convert_fahrenheit_temperature_to_celsius(fahrenheit_temperature):
  """Convert input temperature in degrees Fahrenheit to degrees Celsius."""
  return (5./9)*(fahrenheit_temperature - 32)

if __name__ == "__main__":
  print('T_C\t\tT_C(T_F(T_C))')

  celsius_temperatures = [0, 10, 20, 30, 40]

  for some_celsius_temperature in celsius_temperatures:
      converted_temperature = convert_fahrenheit_temperature_to_celsius(
          convert_celsius_temperature_to_fahrenheit(some_celsius_temperature))
    
      print(f'{some_celsius_temperature}\t\t{converted_temperature:.0f}')
