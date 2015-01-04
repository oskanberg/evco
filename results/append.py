import csv

one = []
with open('plaincoevolution2.csv','r') as f:
	r = csv.reader(f)
	for row in r:
		one.append(row)

two = []
with open('plaincoevolution.csv','r') as f:
	r = csv.reader(f)
	for row in r:
		two.append(row)

assert len(one) == len(two)

for i, row in enumerate(one):
	new_row = row + two[i]
	print ','.join(new_row)
