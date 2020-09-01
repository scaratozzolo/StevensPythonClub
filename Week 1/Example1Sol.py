# Define a function called sum_fib that has one parameter, 'max', with a default value of 4 million.
# The function should return the sum of all even numbers in the Fibonacci sequence that are less than our max value.


# Define the function as sum_fib.
# This function takes in a paramter 'max' and I'm giving it a default value of 4000000.
# This default value means I don't have to pass a value into the function, but can if I want to.
def sum_fib(max=4000000):

    # These are our first two values of the Fibonacci sequence
    x = 0
    y = 1
    # The sequence follows that the value of any number is the sum of the previous two values
    z = x + y
    # What we are saying is that x is the first value, y is the second value, and z is the third being it's the sum of the previous two values

    # This is a variable to store the sum as we go through the sequence.
    sum = 0

    # z is going to be the number we are going to be testing and adding to the sum.
    # We will keep going through the sequence while z is less than the max we have set, which is 4000000.
    while z < max:

        # If the value of z / 2 has a remainder of 0, that means it is even and we will add it to our sum.
        if z % 2 == 0:
            sum += z

        # We now want to go to the next values of the sequence.
        # We set x equal to the next value which is y
        x = y
        # We set y equal to the next value which is z
        y = z
        # We set z equal to the next value which is the sum of the previous two values, x + y
        z = x + y

    # Once the loop has finished (when z is greater than our max value) return the sum we have calculated.
    return sum

print(sum_fib(1000))
# print(sum_fib(10**4))
