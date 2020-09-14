# https://projecteuler.net/problem=22
import time

start = time.time()

names = []
with open("p022_names.txt", 'r') as f:

    for line in f:
        names.extend(line.strip().replace('"', "").split(","))

names.sort()


print(names.index("COLIN"))

totalscore = 0
for i in range(len(names)):

    word_value = 0
    for j in names[i].lower():
        word_value += ord(j)-96

    totalscore += word_value * (i+1)

print(totalscore)

print(f"Time: {time.time() - start}")




















# lIST COMPREHENSION

start = time.time()

names = []
with open("p022_names.txt", 'r') as f:

    for line in f:
        names.extend(line.strip().replace('"', "").split(","))

names.sort()

totalscore = sum([(i+1) * sum([ord(j)-96 for j in names[i].lower()]) for i in range(len(names))])
print(totalscore)

print(f"Time: {time.time() - start}")




















# SOME PANDAS AND SOME OF THE PREVIOUS FUNCTIONS
import pandas as pd

start = time.time()

names = pd.read_csv("p022_names.txt", header=None, na_filter=False)
names.sort_values(by=[0], axis=1, inplace=True)
names = names.iloc[0]

totalscore = 0
for i in range(len(names)):

    word_value = 0
    for j in names.iloc[i].lower():
        word_value += ord(j)-96

    totalscore += word_value * (i+1)

print(totalscore)

print(f"Time: {time.time() - start}")

















# ALL PANDAS
import pandas as pd

start = time.time()

names = pd.read_csv("p022_names.txt", header=None, na_filter=False)
names = names.T
names.columns = ["Names"]
names.sort_values(by="Names", inplace=True, ignore_index=True)

names["lower_names"] = names["Names"].apply(lambda x: x.lower())
names["name_sum"] = names["lower_names"].apply(lambda x: sum([ord(i)-96 for i in x]))
names["name_score"] = names["name_sum"] * (names.index + 1)

totalscore = names["name_score"].sum()
print(names)
print(totalscore)

print(f"Time: {time.time() - start}") 
