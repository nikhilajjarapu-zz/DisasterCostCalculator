q = []
times1 = []
times2 = []
with open('result.csv','r') as f:
	for line in f:
		if "[" in line:
			q.extend(line[1:-1])
		elif "T1" in line:
			#print(line)
			times1.append(float(line.split("-")[-1]))
		elif "T2" in line:
			times2.append(float(line.split("-")[-1]))			

l =[round(float(y),2) for y in q]
with open('tests/avgerror.csv','w') as fp:
	for i in set(l):
		fp.write(str(i) + ", " + str(l.count(i)) + "\n")		

with open('tests/times1.csv','w') as p:
	for j in times1:
		p.write(str(j) + "\n")

with open('tests/times2.csv','w') as p:
	for j in times2:
		p.write(str(j) + "\n")