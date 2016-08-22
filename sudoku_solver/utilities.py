def instantiateMatrix(size):
    matrix = []
    for i in xrange(size):
        matrix.append([])
        for j in xrange(size):
            matrix[i].append([])
    return matrix

def doubleIter(num):
    for x in xrange(num):
        for y in xrange(num):
            yield x, y

# Returns a set of numbers from 1-N^2
def numberSet(size):
    numList = []
    for x in cellIdIter(size):
        numList.append(x)
    return set(numList)

# Returns a dictionary with keys being numbers 1-N^2 and values as empty lists
def numDictList(size):
    dictList = {}
    for x in cellIdIter(size):
        dictList[x] = []
    return dictList

def cellIdIter(size):
    for x in map(str, xrange(1, (size**2)+1)):
        yield x
