def convert_fahrenheit_temperature_to_celsius(fahrenheit_temperature):
    celsius_temperature = (5.0 / 9.0) * (fahrenheit_temperature - 32)
    return celsius_temperature


def read_fahrenheit_temperature_from_file(filename):
    infile = open(filename, "r")

    infile.readline()
    infile.readline()
    infile.readline()
    line = infile.readline()

    infile.close()

    words = line.split()
    fahrenheit_temperature = float(words[2])

    return fahrenheit_temperature


if __name__ == "__main__":
    filename = "temperature_data.txt"

    fahrenheit_temperature = read_fahrenheit_temperature_from_file(filename)
    celsius_temperature = convert_fahrenheit_temperature_to_celsius(fahrenheit_temperature)

    print("Temperature in Fahrenheit:", fahrenheit_temperature)
    print("Temperature in Celsius:", celsius_temperature)
