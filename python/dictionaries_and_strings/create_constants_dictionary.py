def parse_constants_file(filename):
    constants = {}

    with open(filename, 'r') as file:
        lines = file.readlines()

        for line in lines[2:]:
            parts = line.split()

            value = float(parts[-2])
            name = " ".join(parts[:-2])

            constants[name] = value

    return constants


def main():
    filename = "/storage/emulated/0/Download/python-dictionaries-and-strings-main/python-dictionaries-and-strings-main/constants.txt"
    
    constants = parse_constants_file(filename)

    print("Gravitational constant:", constants["gravitational constant"])
    print("Speed of light:", constants["speed of light"])


if __name__ == "__main__":
    main()
