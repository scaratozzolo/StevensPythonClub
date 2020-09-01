# Define a function called power_digit_sum that has two parameters, 'base' and 'exp'.
# The function should calculate the value of base^exp and then return the sum of the digits of that value.
# 2^15 = 32768 and the sum of its digits is 3 + 2 + 7 + 6 + 8 = 26.
# Brownie points if you can do it in one line.


# Define the function
def power_digit_sum(base, exp):

    # I calculate the value of base^exp
    value = base**exp
    # I convert to the value to a string because a string can be manipulated
    valuestr = str(value)

    # A sum variable to store our current sum
    sum = 0
    # I loop through each digit in the string
    for digit in valuestr:
        # I convert the digit back to an integer and add it to the current sum
        sum += int(digit)

    # Finally, return the sum
    return sum

print(power_digit_sum(2, 15))





def power_digit_sum_2(base, exp):

    return sum([int(digit) for digit in str(base ** exp)])

print(power_digit_sum_2(2, 15))
