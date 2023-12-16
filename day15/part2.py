import sys
from collections import defaultdict

with open(sys.argv[1], 'r') as f:
    inps = f.read().strip().split(',')

def do_hash(st):
    output = 0
    for c in st:
        output = ((output + ord(c)) * 17) % 256
    return output

def safe_index(lst, val):
    try:
        return lst.index(val)
    except ValueError:
        return -1

hashmap = defaultdict(lambda: ([], []))
for instruction in inps:
    if '=' in instruction:
        label, focal = instruction.split('=')
        box_num = do_hash(label)
        focal = int(focal)
        labels, focals = hashmap[box_num]
        ind = safe_index(labels, label)
        if ind >= 0:
            focals[ind] = focal
        else:
            labels.append(label)
            focals.append(focal)
    else:
        label = instruction[:-1]
        box_num = do_hash(label)
        labels, focals = hashmap[box_num]
        ind = safe_index(labels, label)
        if ind >= 0:
            labels.pop(ind)
            focals.pop(ind)
        

out = 0
for box_num, (labels, focals) in hashmap.items():
    for i, (label, focal) in enumerate(zip(labels, focals)):
        out += (1 + box_num) * (1 + i) * focal
print(out)
