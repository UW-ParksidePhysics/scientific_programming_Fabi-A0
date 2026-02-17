life_expectancy = 78.4  # years (CDC)

billion_seconds_in_years = (10**9) / (60*60*24*365)

print("1 billion seconds in years =", billion_seconds_in_years)
print("CDC life expectancy in years =", life_expectancy)

print("Can a newborn baby in the United States expect to live for one billion seconds?")

if life_expectancy >= billion_seconds_in_years:
    print("yes")
else:
    print("no")
