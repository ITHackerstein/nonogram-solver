import os, re, sys
from constants import *
from phone import ADB

# Input function

def get_input():
	# Gets the size of the Nonogram

	while True:
		try:
			nono_size = int(input("Type the size of the Nonogram: "))
			if nono_size < 1:
				print("Not valid!")
			else:
				break
		except:
			print("Not valid!")

	row_rules, col_rules = [], []

	# Gets the rules of the rows

	for i in range(nono_size):
		while True:
			err = False
			rule = input(f"Type the rule of row {i + 1}: ").strip()
			if not re.match(r"(\d+ ?)+", rule):
				print("Not valid!")
				err = True
			if not err:
				row_rules.append(re.sub(' {2,}', ' ', rule)) # Removes consecutive spaces
				break

	# Gets the rules of the columns

	for i in range(nono_size):
		while True:
			err = False
			rule = input(f"Type the rule of column {i + 1}: ").strip()
			if not re.match(r"(\d+ ?)+", rule):
				print("Not valid!")
				err = True
			if not err:
				col_rules.append(re.sub(' {2,}', ' ', rule)) # Removes consecutive spaces
				break

	return nono_size, row_rules, col_rules

# Function to parse file as input

def parse_file(filename):
	with open(filename) as f:
		lines = f.read().strip().split("\n")

	nono_size = int(lines[0])
	row_rules = [l.strip() for l in lines[1:nono_size + 1]]
	col_rules = [l.strip() for l in lines[nono_size + 1:]]
	return nono_size, row_rules, col_rules

# Function to get input from a phone

def phone_input():
	nono_size, row_rules, col_rules = get_input()

	print("Now you have to touch a cell in the top left quarter of the grid.")
	print("You will have 5 seconds to do it. As soon as you hit Enter the countdown starts.")
	input("Hit Enter when you're ready ... ")
	try:
		tl_cell = adb.get_touch_inputs()[0] # The top left cell position
	except:
		print("Error while trying to read touch inputs from device! Make sure the device is connected!")
		sys.exit(1)

	actual_tl_cell = tl_cell.copy() # The actual top left cell position

	try:
		phone_screen = adb.get_screen()
	except:
		print("Error while trying to take screenshot from device! Make sure the device is connected!")
		sys.exit(1)

	width, height = phone_screen.size

	big_border_color = (0, 0, 0, 255)
	small_border_color = (190, 197, 212, 255)
	WHITE = (255, 255, 255, 255)

	print("Gaining top left cell X coordinate...")

	while phone_screen.getpixel((actual_tl_cell[0], tl_cell[1])) != big_border_color:
		actual_tl_cell[0] -= 1
	actual_tl_cell[0] += 2

	print("Gaining top left cell Y coordinate...")

	while phone_screen.getpixel((actual_tl_cell[0], actual_tl_cell[1])) != big_border_color:
		actual_tl_cell[1] -= 1
	actual_tl_cell[1] += 2

	print("Getting grid data...")

	x, y = actual_tl_cell
	cell_size = 0
	while phone_screen.getpixel((x, y)) != small_border_color:
		cell_size += 1
		x += 1

	small_border_size = 0
	while phone_screen.getpixel((x, y)) != WHITE:
		small_border_size += 1
		x += 1

	while phone_screen.getpixel((x, y)) != big_border_color:
		x += 1

	big_border_size = 0
	while phone_screen.getpixel((x,y)) != WHITE:
		big_border_size += 1
		x += 1

	pgrid_data = {"tl_cell": actual_tl_cell, "cell_size": cell_size, "big_border_size": big_border_size, "small_border_size": small_border_size}

	phone_screen.close()
	os.remove('screen.png')

	return nono_size, pgrid_data, row_rules, col_rules

