import sys


def celsius_to_fahrenheit(celsius_temperature):
    fahrenheit_temperature = (9.0 / 5.0) * celsius_temperature + 32
    return fahrenheit_temperature


def fahrenheit_to_celsius(fahrenheit_temperature):
    celsius_temperature = (5.0 / 9.0) * (fahrenheit_temperature - 32)
    return celsius_temperature


def celsius_to_kelvin(celsius_temperature):
    kelvin_temperature = celsius_temperature + 273.15
    return kelvin_temperature


def kelvin_to_celsius(kelvin_temperature):
    celsius_temperature = kelvin_temperature - 273.15
    return celsius_temperature


def fahrenheit_to_kelvin(fahrenheit_temperature):
    kelvin_temperature = celsius_to_kelvin(fahrenheit_to_celsius(fahrenheit_temperature))
    return kelvin_temperature


def kelvin_to_fahrenheit(kelvin_temperature):
    fahrenheit_temperature = celsius_to_fahrenheit(kelvin_to_celsius(kelvin_temperature))
    return fahrenheit_temperature


def test_conversion():
    test_values = [0, 32, 67.2, 100, -40]

    for value in test_values:
        assert abs(celsius_to_fahrenheit(fahrenheit_to_celsius(value)) - value) < 1e-6
        assert abs(kelvin_to_celsius(celsius_to_kelvin(value)) - value) < 1e-6
        assert abs(kelvin_to_fahrenheit(fahrenheit_to_kelvin(value)) - value) < 1e-6

    print("All tests passed!")


def user_interface():
    temperature = float(sys.argv[1])
    scale = sys.argv[2]

    if scale == "C":
        fahrenheit_temperature = celsius_to_fahrenheit(temperature)
        kelvin_temperature = celsius_to_kelvin(temperature)
        print(f"{fahrenheit_temperature:.1f} F {kelvin_temperature:.1f} K")

    elif scale == "F":
        celsius_temperature = fahrenheit_to_celsius(temperature)
        kelvin_temperature = fahrenheit_to_kelvin(temperature)
        print(f"{celsius_temperature:.1f} C {kelvin_temperature:.1f} K")

    elif scale == "K":
        celsius_temperature = kelvin_to_celsius(temperature)
        fahrenheit_temperature = kelvin_to_fahrenheit(temperature)
        print(f"{celsius_temperature:.1f} C {fahrenheit_temperature:.1f} F")

    else:
        print("Wrong temperature scale. Use C, F, or K.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        test_conversion()
    else:
        user_interface()
