# src/hc_div/hc_div.py

import sys

def div():
	try:
		args = sys.argv
		if len(args) != 3:
			print("Error: hc_add.add() requires two in-line arguments. Please try again.")
		else:
			try:
				a = int(sys.argv[1])
				b = int(sys.argv[2])
				print(a//b, " remainder ", a%b)
			except ValueError:
				print("Error: Both arguments must be integers. Please try again.")
	except AttributeError:
		print("Error: sys.argv does not exist. The script should be run from the command line. Please try again.")
