## Usage

To use this solver it's required to install the required Python modules with

# Nonogram Solver

## Description

This is a Nonogram solver that can solve only single solution puzzles. It can theoreitcally solve any of them, but it's recommended to solve only puzzles with a size less than 27 or even more.

_Don't take this project too seriously, it was done only to have fun._

## Installation

1. Clone the repository
2. Install the required Python modules (```$ python -m pip install -r requirements.txt```)
3. _(optional)_ If you want to use the _PHONE_ mode you must have installed _ADB_ in your system, and you have to connect your device with debugging mode enabled. You can find a lot of good guides online on how to do it.

## Usage

**DISCLAIMER**: The _PHONE_ mode only works on this app: [Nonogram from Easybrain](https://play.google.com/store/apps/details?id=com.easybrain.nonogram).

Usage syntax:

```$ python src\nonogram.py [file|PHONE]```

If we don't have any arguments the solver will ask the user for the size of the Nongoram and its rules. If we have as an argument a file the solver will read the input from there that must formatted using this rules:
1. The first line will contain _N_ the size of the Nonogram
2. The next _N_ lines will contain the rules of the rows
3. The next_N_ lines will contains the rules of the columns
If the second argument is ```PHONE``` then the solver will ask the user the size and the rules of the Nonogram, and it will also ask to touch the top left quarter of the grid and when it solves the Nonogram than the solution will be sent to the phone.

To test the solver there are some test files in the _tests_ folder.
