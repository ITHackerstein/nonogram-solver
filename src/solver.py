from constants import *
from itertools import product as cart_prod
import os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pygame

# Wrapper function to get the font

font_hash = {}

def get_font(font_name, font_size):
	if (font_name, font_size) not in font_hash:
		font_hash[(font_name, font_size)] = pygame.font.SysFont(font_name, font_size)
	return font_hash[(font_name, font_size)]

# Helper function to check if a combination is valid given a rule

def is_valid(comb, exc_counts, constraints = {}):
	comb_ = comb[:]
	for i, ch in constraints.items():
		if comb_[i] == 2 and ch == 0:
			comb_[i] = 0

		if comb_[i] != ch:
			return False

	count = 0
	got_counts = []
	for ch in comb_:
		if ch == 1:
			count += 1
		else:
			if count > 0:
				got_counts.append(count)
			count = 0

	if count > 0:
		got_counts.append(count)

	return got_counts == exc_counts

# Solver classes

class Rule:
	def __init__(self, pos, type, rule, N, total_combinations, screen):
		self.pos = pos
		self.type = type
		self.rule = [int(rule) for rule in rule.split(" ")]
		self.N = N
		self.screen = screen
		self.total_combinations = total_combinations

	def show(self, size, color):
		if self.type == "ROW":
			rule_txt = " ".join(map(str, self.rule))

			fs = min(int((3 * rules_off / len(rule_txt) + 3) / 2), size - 4) # That's the font size. I calculated it with a mathematical formula
			f = get_font('Monospace', fs)

			text_surface = f.render(rule_txt, True, color) # Draw a text with anti-aliasing and the color specified

			tw, th = text_surface.get_width(), text_surface.get_height() # Width and height of the text drawn

			h_off = (size - th) // 2 # Amount to add to the y-coordinate to center vertically the text.

			self.screen.blit(text_surface, (rules_off - tw, self.pos * size + rules_off + h_off)) # Draws the text onto the screen
		elif self.type == "COL":
			# Calculates the minimum font size. I used a mathematical formula again
			fs = rules_off // len(self.rule)
			for n in self.rule:
				fs = min(fs, int(3 / 2 * (size / len(str(n)) + 1)))

			f = get_font('Monospace', fs)
			for i, n in enumerate(self.rule):

				text_surface = f.render(str(n), True, color) # Draw a text with anti-aliasing and the color specified

				tw = text_surface.get_width() # That's the width of the text

				w_off = (size - tw) // 2 # Amount to add to the x-coordinate to center horizontally

				self.screen.blit(text_surface, (rules_off + self.pos * size + w_off, fs * i)) # Draws the text onto the screen

	def solve(self, constraints = {}):
		valid_combinations = [comb for comb in self.total_combinations if is_valid(comb, self.rule, constraints)]

		prod = [[] for _ in range(self.N)]
		for i in range(self.N):
			for j in range(len(valid_combinations)):
				if valid_combinations[j][i] not in prod[i]:
					prod[i].append(valid_combinations[j][i])

		res = []
		for intersection in prod:
			if len(intersection) == 1:
				if intersection[0] == 2:
					res.append(0)
				else:
					res.append(intersection[0])
			else:
				res.append(2)

		return res

class Grid:
	def __init__(self, N, screen):
		self.N = N
		self.mat = [[2 for i in range(N)] for j in range(N)]
		self.rules = []
		self.scl = size // N
		self.solve_idx = 0
		self.screen = screen
		self.total_combinations = [list(comb) for comb in cart_prod([2, 1], repeat=self.N)]

	def show(self):
		for j in range(self.N):
			for i in range(self.N):
				pygame.draw.rect(self.screen, (127, 127, 127), pygame.Rect(i * self.scl + rules_off, j * self.scl + rules_off, self.scl, self.scl), 1)
				if self.mat[j][i] == 0:
					pygame.draw.line(self.screen, (255, 255, 255), (i * self.scl + 10 + rules_off, j * self.scl + 10 + rules_off), ((i + 1) * self.scl - 10 + rules_off, (j + 1) * self.scl - 10 + rules_off), 3)
					pygame.draw.line(self.screen, (255, 255, 255), ((i + 1) * self.scl - 10 + rules_off, j * self.scl + 10 + rules_off), (i * self.scl + 10 + rules_off, (j + 1) * self.scl - 10 + rules_off), 3)
				elif self.mat[j][i] == 1:
					pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(i * self.scl + 1 + rules_off, j * self.scl + 1 + rules_off, self.scl - 2, self.scl - 2))
				elif self.mat[j][i] == 2:
					pygame.draw.rect(self.screen, (0, 0, 0), pygame.Rect(i * self.scl + 1 + rules_off, j * self.scl + 1 + rules_off, self.scl - 2, self.scl - 2))

		for rule in self.rules:
			rule.show(self.scl, (36, 209, 96) if self.is_rule_solved(rule.type, rule.pos) else (255, 255, 255))

	def get_rule(self, type, pos):
		for i, rule in enumerate(self.rules):
			if rule.type == type and rule.pos == pos:
				return self.rules[i]
		return -1

	def get(self, x, y):
		assert x >= 0 and x < self.N, f"X out of range! (0 <= X < {self.N})"
		assert y >= 0 and y < self.N, f"Y out of range! (0 <= Y < {self.N})"
		return self.mat[y][x]

	def set(self, x, y, val):
		assert x >= 0 and x < self.N, f"X out of range! (0 <= X < {self.N})"
		assert y >= 0 and y < self.N, f"Y out of range! (0 <= Y < {self.N})"
		self.mat[y][x] = val

	def solve_rule(self, type, pos):
		if self.is_rule_solved(type, pos):
			if type == "ROW":
				for i in range(self.N):
					if self.mat[pos][i] == 2:
						self.mat[pos][i] = 0
			elif type == "COL":
				for j in range(self.N):
					if self.mat[j][pos] == 2:
						self.mat[j][pos] = 0
			return

		rule = self.get_rule(type, pos)
		assert rule != -1, f"No such rule ({type}, {pos})"

		constraints = {}
		if type == "ROW":
			for i in range(self.N):
				if self.mat[pos][i] < 2:
					constraints[i] = self.mat[pos][i]
		elif type == "COL":
			for j in range(self.N):
				if self.mat[j][pos] < 2:
					constraints[j] = self.mat[j][pos]

		res = rule.solve(constraints)

		if type == "ROW":
			for i in range(self.N):
				if self.mat[pos][i] == 2:
					self.mat[pos][i] = res[i]
		elif type == "COL":
			for j in range(self.N):
				if self.mat[j][pos] == 2:
					self.mat[j][pos] = res[j]

	def is_rule_solved(self, type, pos):
		rule = self.get_rule(type, pos)
		assert rule != -1, f"There is no such rule ({type}, {pos})"
		if type == "ROW":
			return is_valid(self.mat[pos], rule.rule)
		elif type == "COL":
			return is_valid([self.mat[j][pos] for j in range(self.N)], rule.rule)

	def is_grid_solved(self):
		for j in range(self.N):
			if not self.is_rule_solved("ROW", j):
				return False
		for i in range(self.N):
			if not self.is_rule_solved("COL", i):
				return False
		return True

	def solve(self):
		type = "ROW"
		if self.solve_idx >= self.N:
			type = "COL"
		self.solve_rule(type, self.solve_idx % self.N)
		self.solve_idx += 1
		self.solve_idx = self.solve_idx % (self.N * 2)

	def add_rule(self, pos, type, rule):
		self.rules.append(Rule(pos, type, rule, self.N, self.total_combinations, self.screen))
