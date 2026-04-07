def main():
    code_snippets = {
        "dictionary_working": {
            "code": "numbers = {}\nnumbers[0] = -5\nnumbers[1] = 10.5",
            "explanation": "This works because dictionaries do not need keys to exist before assigning values. Python creates the key automatically.",
            "fixed": ""
        },
        "list_not_working": {
            "code": "other_numbers = []\nother_numbers[0] = -5\nother_numbers[1] = 10.5",
            "explanation": "This does not work because lists need positions to already exist. The list is empty, so index 0 does not exist.",
            "fixed": "other_numbers = []\nother_numbers.append(-5)\nother_numbers.append(10.5)"
        }
    }

    for name, snippet in code_snippets.items():
        print(f"\n--- {name} ---")

        print("\nCode:")
        print(snippet["code"])

        print("\nReason:")
        print(snippet["explanation"])

        if snippet["fixed"]:
            print("\nFixed Code:")
            print(snippet["fixed"])


if __name__ == "__main__":
    main()
