mass = open(r"").read().split(' ,')
res = []
for i in range(len(mass)):
    if mass[i][0] == " ":
        res.append(mass[i][1:])
    else:
        res.append(mass[i])
f = open("", 'w')
