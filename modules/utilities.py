def instantiateMatrix():
	matrix = []
	for i in range(3):
		matrix.append([])
		matrix[i].append([])
		matrix[i].append([])
		matrix[i].append([])
	return matrix

def rowColIter(num):
	for row in range(num):
		for col in range(num):
			yield row, col
