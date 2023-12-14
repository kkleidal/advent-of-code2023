import sys

board = []
with open(sys.argv[1], 'r') as f:
    for line in f:
        line = line.strip()
        if line:
            board.append(list(line))

def tilt_north():
    for j in range(len(board[0])):
        i = 0
        while i < len(board):
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

def view_as_north(direction, undo=False):
    global board
    assert len(board) == len(board[1])
    N = len(board)
    if direction == 'W':
        coord_mapping = lambda i, j: (j, i)
    elif direction == 'E':
        coord_mapping = lambda i, j: (j, N - 1 - i)
    elif direction == 'S':
        coord_mapping = lambda i, j: (N - 1 - i, j)
    elif direction == 'N':
        coord_mapping = lambda i, j: (i, j)
    new_board = [[None] * N for _ in range(N)]
    for i in range(N):
        for j in range(N):
            oi, oj = coord_mapping(i, j)
            if undo:
                new_board[oi][oj] = board[i][j]
            else:
                new_board[i][j] = board[oi][oj]
    board = new_board

def print_board():
    for row in board:
        print(''.join(row))
    print()

def cycle():
    # print_board()
    for direction in ['N', 'W', 'S', 'E']:
        view_as_north(direction)
        tilt_north()
        view_as_north(direction, undo=True)
        # print_board()

state_to_seen = {}
target = 1000000000
at_end = False
i = 0
while i < target:
    cycle()
    i += 1
    state = tuple(tuple(row) for row in board)
    if not at_end and state in state_to_seen:
        cycle_length = i - state_to_seen[state]
        i += ((target - i) // cycle_length) * cycle_length
        at_end = True
    if not at_end:
        state_to_seen[state] = i
total = 0
for i, row in enumerate(board):
    points_per = len(board) - i
    total += points_per * sum(1 for c in row if c == 'O')
print(total) 
