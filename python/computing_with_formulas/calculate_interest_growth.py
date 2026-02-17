# Interest rate pulled from US Treasury website on Feb 11, 2026
interest_rate = 3.55  # percent per year

initial_amount = 1000  # dollars
years = 3

growth_amount = initial_amount * (1 + interest_rate/100)**years

print("Initial amount = $", initial_amount)
print("Interest rate =", interest_rate, "% per year")
print("Amount after", years, "years = $", round(growth_amount, 2))
