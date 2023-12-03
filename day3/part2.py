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

pos_to_digit_index = {
    pos: digit_index
    for digit_index, (digit, positions) in enumerate(digits)
    for pos in positions
}

total = 0
for (i, j), symbol in symbols.items():
    if symbol != '*':
        continue
    adj_digits = set()
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            if dy == 0 and dx == 0:
                continue
            digit_index = pos_to_digit_index.get((i + dy, j + dx))
            if digit_index is not None:
                adj_digits.add(digit_index)
    if len(adj_digits) == 2:
        x, y = sorted(adj_digits)
        total += digits[x][0] * digits[y][0]
print(total)
