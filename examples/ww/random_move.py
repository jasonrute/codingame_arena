import sys
import math
import random

# Auto-generated code below aims at helping you parse
# the standard input according to the problem statement.

size = int(input())
units_per_player = int(input())

# game loop
while True:
    for i in range(size):
        row = input()
    for i in range(units_per_player):
        unit_x, unit_y = [int(j) for j in input().split()]
    for i in range(units_per_player):
        other_x, other_y = [int(j) for j in input().split()]
    legal_actions = int(input())
    moves = []
    for i in range(legal_actions):
        atype, index, dir_1, dir_2 = input().split()
        index = int(index)
        moves.append((atype, index, dir_1, dir_2))

    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr)

    if moves:
        print(*random.choice(moves))
    else:
        print("ACCEPT-DEFEAT")