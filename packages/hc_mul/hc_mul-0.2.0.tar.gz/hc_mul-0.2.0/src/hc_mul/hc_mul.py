# src/hc_mul/hc_mul.py

import sys

def mul():
	try:
		args = sys.argv
		if len(args) != 3:
			print("Error: hc_mul.mul() requires two in-line arguments. Please try again.")
		else:
			try:
				a = int(args[1])
				b = int(args[2])
				print(a * b)
			except ValueError:
				print("Error: Both arguments must be integers. Please try again.")
	except AttributeError:
		print("Error: sys.argv does not exist. The script should be run from the command line. Please try again.")

