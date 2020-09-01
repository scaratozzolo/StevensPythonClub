# Define a function called "ssd" that has one parameter, "x", that finds the difference between the sum of the squares of the first x natural numbers and the square of the sum.
# Brownie points if you can do it in one line.

# Define the function with our parameter
def ssd(x):

    # Create two variables that will store our sums.
    sumofsquares = 0
    squareofsum = 0

    # Loop through each number up to x
    # Reminder that the range fucntion is used as the number range from x up to but not including y [x,y) which is why I use x+1
    for i in range(1, x+1):
        # For each number I add the squared value to the sum or just the regular value to the sum
        sumofsquares += i**2
        squareofsum += i

    # I square the squareofsum and overwrite it.
    squareofsum = squareofsum**2

    # Return the difference
    return squareofsum - sumofsquares

print(ssd(10))



def ssd_2(x):

    return sum([i for i in range(1, x+1)])**2 - sum([i**2 for i in range(1, x+1)])

print(ssd_2(10))
