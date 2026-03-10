nearby_star_data = [
    ('Alpha Centauri A', 4.3, 0.26, 1.56),
    ('Alpha Centauri B', 4.3, 0.077, 0.45),
    ('Alpha Centauri C', 4.2, 0.00001, 0.00006),
    ("Barnard's Star", 6.0, 0.00004, 0.0005),
    ('Wolf 359', 7.7, 0.000001, 0.00002),
    ('BD +36 degrees 2147', 8.2, 0.0003, 0.006),
    ('Luyten 726-8 A', 8.4, 0.00003, 0.00006),
    ('Luyten 726-8 B', 8.4, 0.00002, 0.00004),
    ('Sirius A', 8.6, 1.00, 23.6),
    ('Sirius B', 8.6, 0.001, 0.003),
    ('Ross 154', 9.4, 0.00002, 0.0005)
]


def print_sorted_table(star_data, index, title, column_name):

    sorted_data = sorted(star_data, key=lambda item: item[index])

    print(title)
    print(f"{'Star name':<25} {column_name:>20}")
    print("-" * 45)

    for star in sorted_data:
        print(f"{star[0]:<25} {star[index]:>20}")

    print()


print_sorted_table(nearby_star_data, 1, "Stars sorted by distance", "Distance")
print_sorted_table(nearby_star_data, 2, "Stars sorted by apparent brightness", "Apparent brightness")
print_sorted_table(nearby_star_data, 3, "Stars sorted by luminosity", "Luminosity")
