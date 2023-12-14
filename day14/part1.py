import sys

board = []
with open(sys.argv[1], 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            board.append(list(line))

for j in range(len(board[1])):
    i = 0
    while i < len(board[0]):
        if board[i][j] == '.':
            # Find next O or #
            start = i
            while i < len(board[0]) and board[i][j] not in ('O', '#'):
                i += 1
            if i == len(board[0]):
                break
            elif board[i][j] == 'O':
                board[start][j] = 'O'
                board[i][j] = '.'
                i = start
            else:
                assert board[i][j] == '#'
        i += 1

total = 0
for i, row in enumerate(board):
    points_per = len(board) - i
    total += points_per * sum(1 for c in row if c == 'O')
print(total) 
