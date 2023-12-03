import sys

i = 0
symbols = {}
digits = []
for line in sys.stdin:
    line = line.strip()
    if line:
        j = 0
        while j < len(line):
            c = line[j]
            if c.isdigit():
                je = j
                while je < len(line) and line[je].isdigit():
                    je += 1
                num = int(line[j:je])
                digits.append((num, [
                    (i, j_inner)
                    for j_inner in range(j, je)
                ]))
                j = je - 1
            elif c != '.':
                symbols[(i, j)] = c
            j += 1
        i += 1

total = 0
for digit, positions in digits:
    adj = False
    for (i, j) in positions:
        if adj:
            break
        for dy in range(-1, 2):
            if adj:
                break
            for dx in range(-1, 2):
                if dy == 0 and dx == 0:
                    continue
                if (i + dy, j + dx) in symbols:
                    adj = True
                    break
    if adj:
        total += digit
print(total)
