

def ssd(x):

    sumofsquares = 0
    squareofsum = 0

    for i in range(1, x+1):

        sumofsquares += i**2
        squareofsum += i

    squareofsum = squareofsum **2

    return squareofsum - sumofsquares

print(ssd(10))


def ssd_2(x):

    return (x*(x+1)/2)**2 - (x*(x+1)*(2*x+1))/6



print(ssd_2(10))

print(10/5)
print(10//4)
