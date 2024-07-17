# src/hc_div/hc_div.py

import sys

def div():
	a = int(sys.argv[1])
	b = int(sys.argv[2])
	print(a//b, " remainder ", a%b)
