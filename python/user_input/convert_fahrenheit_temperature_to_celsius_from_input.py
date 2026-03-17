def convert_fahrenheit_temperature_to_celsius(fahrenheit_temperature):
    celsius_temperature = (5.0 / 9.0) * (fahrenheit_temperature - 32)
    return celsius_temperature


def main():
    fahrenheit_temperature = float(input("Enter temp in Fahrenheit: "))
    celsius_temperature = convert_fahrenheit_temperature_to_celsius(fahrenheit_temperature)

    print(f"Temperature in Fahrenheit: {fahrenheit_temperature}")
    print(f"Temperature in Celsius: {celsius_temperature:.2f}")


if __name__ == "__main__":
    main()
