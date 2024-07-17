import os
os.system("")

for i in range(0, 16):
    print(u"\u001b[48;5;" + str(i) + "m " + str(i).ljust(4), end="")
    if i == 7:
        print(u"\u001b[0m")

print(u"\u001b[0m")
print()


counter = {"block": 0, "row": 0}
for i in range(16, 232):
    counter["block"] += 1
    counter["row"] += 1
    print(u"\u001b[48;5;" + str(i) + "m " + str(i).ljust(4), end="")
    if counter["block"] == 6:
        counter["block"] = 0
        print(u"\u001b[0m    ", end="")
    if counter["row"] == 36:
        counter["row"] = 0
        print(u"\u001b[0m")

print(u"\u001b[0m")

for i in range(232, 256):
    print(u"\u001b[48;5;" + str(i) + "m " + str(i).ljust(4), end="")
print(u"\u001b[0m")
