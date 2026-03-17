import sys


def convert_fahrenheit_temperature_to_celsius(fahrenheit_temperature):
    return (5.0 / 9.0) * (fahrenheit_temperature - 32)


if __name__ == "__main__":
    try:
        fahrenheit_temperature = float(sys.argv[1])

        celsius_temperature = convert_fahrenheit_temperature_to_celsius(fahrenheit_temperature)

        print("Temperature in Fahrenheit:", fahrenheit_temperature)
        print("Temperature in Celsius:", celsius_temperature)

    except:
        print("Error: Please provide a temperature value on the command line.")
