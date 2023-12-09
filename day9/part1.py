import sys
import numpy as np

sequences = []
with open(sys.argv[1], "r") as f:
    for line in f:
        line = line.strip()
        if line:
            sequences.append(list(map(int, line.split(" "))))

total = 0
for seq in sequences:
    hist = [np.array(seq)]
    while not np.all(hist[-1] == 0):
        hist.append(hist[-1][1:] - hist[-1][:-1])
    hist = [x.tolist() for x in hist]
    for i in range(len(hist)):
        if i == 0:
            hist[-1].append(0)
        else:
            hist[-1-i].append(hist[-1-i][-1] + hist[-i][-1])
    val = hist[0][-1]
    total += val
print(total)
