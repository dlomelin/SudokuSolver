def instantiateMatrix(size):
	matrix = []
	for i in range(size):
		matrix.append([])
		for j in range(size):
			matrix[i].append([])
	return matrix

def doubleIter(num):
	for x in range(num):
		for y in range(num):
			yield x, y
