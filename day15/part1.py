import sys

with open(sys.argv[1], 'r') as f:
    inps = f.read().strip().split(',')

def do_hash(st):
    output = 0
    for c in st:
        output = ((output + ord(c)) * 17) % 256
    return output

print(sum(do_hash(st) for st in inps))
