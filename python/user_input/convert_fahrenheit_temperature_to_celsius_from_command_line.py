import sys


def convert_fahrenheit_temperature_to_celsius(fahrenheit_temperature):
    celsius_temperature = (5.0 / 9.0) * (fahrenheit_temperature - 32)
    return celsius_temperature


if __name__ == "__main__":
    fahrenheit_temperature = float(sys.argv[1])
    celsius_temperature = convert_fahrenheit_temperature_to_celsius(fahrenheit_temperature)

    print("Temperature in Fahrenheit:", fahrenheit_temperature)
    print("Temperature in Celsius:", celsius_temperature)
