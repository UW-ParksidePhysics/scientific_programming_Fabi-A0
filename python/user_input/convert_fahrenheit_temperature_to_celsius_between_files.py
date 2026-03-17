def convert_fahrenheit_temperature_to_celsius(fahrenheit_temperature):
    return (5.0 / 9.0) * (fahrenheit_temperature - 32)


def read_fahrenheit_temperatures(filename):
    infile = open(filename, "r")

    lines = infile.readlines()
    infile.close()

    fahrenheit_list = []

    # Skip first 2 lines, then process the rest
    for line in lines[2:]:
        words = line.split()
        fahrenheit_temperature = float(words[2])
        fahrenheit_list.append(fahrenheit_temperature)

    return fahrenheit_list


def write_temperatures_to_file(filename, fahrenheit_list):
    outfile = open(filename, "w")

    outfile.write("Fahrenheit    Celsius\n")

    for f in fahrenheit_list:
        c = convert_fahrenheit_temperature_to_celsius(f)
        outfile.write(f"{f:10.2f} {c:10.2f}\n")

    outfile.close()


if __name__ == "__main__":
    input_file = "temperature_data.txt"
    output_file = "converted_temperatures.txt"

    fahrenheit_list = read_fahrenheit_temperatures(input_file)
    write_temperatures_to_file(output_file, fahrenheit_list)

    print("Conversion complete. Check output file.")
