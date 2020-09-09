
def power_digit_sum(base, exp):

    value = base**exp # 2^2

    valuestr = str(value)

    sum = 0

    for digit in valuestr:

        sum += int(digit)

    return sum


# print(power_digit_sum(12, 15))

# def power_digit_sum2(base, exp):
#
#     return sum([int(digit) for digit in str(base ** exp)])
#
# print(power_digit_sum2(12, 15))

import pandas as pd

df = pd.DataFrame()
winloss = ["W", "L", "W", "W"]
df["WINLOSS"] = winloss
df['Test'] = [1 if i == "W" else 0 for i in winloss]
print(df)
