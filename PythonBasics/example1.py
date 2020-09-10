
def sum_fib(max=4000000):

    x = 0
    y = 1
    z = x + y
    sum = 0

    while z < max:

        if z % 2 == 0:
            sum += z


        x = y
        y = z
        z = x + y

    return sum



print(sum_fib(100))
print(sum_fib(max=10000000000))
