# OG code

# summation = 0
# starting_index = 1
# index = starting_index
# maximum_index = 100
#
# while index < maximum_index:
#     summation += 1/index
#
# print(f'sum(k = {starting_index}, {maximum_index}) 1/k = {summation}')


# ------------------------------------------------
# Errors
# 1. index never increases so infinite loop
# 2. condition should include maximum_index
# 3. summation should be a float (0.0)
# ------------------------------------------------


# working results 

summation = 0.0
starting_index = 1
index = starting_index
maximum_index = 3

while index <= maximum_index:
    summation = summation + 1.0/index
    index = index + 1

print(f'sum(k = {starting_index}, {maximum_index}) 1/k = {summation}')


# Now test for kmax = 100

summation = 0.0
starting_index = 1
index = starting_index
maximum_index = 100

while index <= maximum_index:
    summation = summation + 1.0/index
    index = index + 1

print(f'sum(k = {starting_index}, {maximum_index}) 1/k = {summation}')

