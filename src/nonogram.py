# TODO:
# -- Try to use the 'tesseract' to get the rules from the puzzle (improbable if and only if it manages to recognize the numbers it doesn't recognize correctly the spaces between the numbers)

from itertools import product as cart_prod
from constants import *
from phone import ADB
from solver import Grid
from input_helpers import *
from PIL import Image
import math, io

import os, sys
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame

# Function to get the position where to touch on the phone

def get_phone_coord(i, j):
	cell_size = 840 // nono_size
	x = actual_tl_cell[0] + (cell_size + 2) * i + int((i + 1) % 5 == 0) * 5
	y = actual_tl_cell[1] + (cell_size + 2) * j + int((j + 1) % 5 == 0) * 5
	return x, y

# WELCOME Message

print("This is a Nonogram puzzle solver!")
print("This can theoretically solve any Nonogram puzzle, but I STRONGLY suggest to use a Nonogram size less than around 27, or even less. Trying bigger ones can potentially freeze your PC, so don't try that.")
print("This solver can only solve single solutions Nonograms.\n")

# Global variables

nono_size = 0
actual_tl_cell = None

if len(sys.argv) > 1:
	if sys.argv[1] != "PHONE":
		try:
			nono_size, row_rules, col_rules = parse_file(sys.argv[1])
		except:
			print("Error while parsing file!")
			sys.exit()
	else:
		nono_size, actual_tl_cell, row_rules, col_rules = phone_input()
else:
	nono_size, row_rules, col_rules = get_input()

# Initializing pygame

pygame.init()

# Creating the screen and the clock

screen = pygame.display.set_mode((size + rules_off, size + rules_off))
pygame.display.set_caption("Nonogram Solver")
clock = pygame.time.Clock()

# Creating the grid of the Nonogram

grid = Grid(nono_size, screen)

# Adding the rules of the rows to the grid

for i, rule in enumerate(row_rules):
	grid.add_rule(i, "ROW", rule)

# Adding the rules of the columns to the grid

for i, rule in enumerate(col_rules):
	grid.add_rule(i, "COL", rule)

# Main loop

while True:
	if grid.is_grid_solved() and sys.argv[1] == "PHONE":
		break

	for evt in pygame.event.get():
		if evt.type == pygame.QUIT:
			sys.exit()

	screen.fill((0, 0, 0))
	grid.solve()
	grid.show()

	pygame.display.flip()
	clock.tick(FPS)

if sys.argv[1] == "PHONE":
	print("Creating input script for phone...")
	input_file = io.open("input.sh", "a", newline='\n') # Assures the line-ending is Unix

	cell_size = 840 // nono_size

	for j in range(nono_size):
		start = None
		for i in range(nono_size):
			if i == nono_size - 1:
				if grid.get(i, j) == 1 and start is not None:
					swipe_dur = round((i - start + 1) / 5 * 300)
					if swipe_dur < 300:
						swipe_dur = 300
					x1, y1 = get_phone_coord(start, j)
					x2, y2 = get_phone_coord(i, j)
					input_file.write(f"input swipe {x1 + cell_size // 4} {y1 + cell_size // 2} {x2 + cell_size * 3 // 4} {y2 + cell_size // 2} {swipe_dur}\n")
				elif grid.get(i, j) == 1 and start is None:
					x, y = get_phone_coord(i, j)
					input_file.write(f"input tap {x + cell_size // 2} {y + cell_size // 2}\n")
				elif grid.get(i, j) != 1 and start is not None:
					swipe_dur = round((i - start) / 5 * 300)
					if swipe_dur < 300:
						swipe_dur = 300
					x1, y1 = get_phone_coord(start, j)
					x2, y2 = get_phone_coord(i - 1, j)
					input_file.write(f"input swipe {x1 + cell_size // 4} {y1 + cell_size // 2} {x2 + cell_size * 3 // 4} {y2 + cell_size // 2} {swipe_dur}\n")
				continue

			if grid.get(i, j) == 1 and start is None:
				start = i

			if grid.get(i, j) != 1 and start is not None:
					if i - start > 1:
						swipe_dur = round((i - start) / 5 * 300)
						if swipe_dur < 300:
							swipe_dur = 300
						x1, y1 = get_phone_coord(start, j)
						x2, y2 = get_phone_coord(i - 1, j)
						input_file.write(f"input swipe {x1 + cell_size // 4} {y1 + cell_size // 2} {x2 + cell_size * 3 // 4} {y2 + cell_size // 2} {swipe_dur}\n")
					else:
						x, y = get_phone_coord(start, j)
						input_file.write(f"input tap {x + cell_size // 2} {y + cell_size // 2}\n")
					start = None

	print("Sending input script to phone...")
	input_file.close()
	adb.send_file("input.sh", "/sdcard/input.sh")
	print("Running input script...")
	adb.run_command("sh /sdcard/input.sh")
	print("Removing input script...")
	os.remove("input.sh")
	adb.run_command("rm /sdcard/input.sh")

	while True:
		answer = input("Do you want to kill the ADB server? [y/n]").lower()
		if answer != 'y' and answer != 'n':
			print("Not valid!")
			continue

		if answer == 'y':
			kill_server()
			print("Server killed!")
		break
