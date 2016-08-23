'''.'''


def instantiate_matrix(size):
    matrix = []
    for i in xrange(size):
        matrix.append([])
        for j in xrange(size):
            matrix[i].append([])
    return matrix


def double_iter(num):
    for x in xrange(num):
        for y in xrange(num):
            yield x, y


def number_set(size):
    ''' Returns a set of numbers from 1-N^2 '''

    numList = []
    for x in cell_id_iter(size):
        numList.append(x)
    return set(numList)


def num_dict_list(size):
    ''' Returns a dictionary with keys being numbers 1-N^2 and values as empty lists '''
    dictList = {}
    for x in cell_id_iter(size):
        dictList[x] = []
    return dictList


def cell_id_iter(size):
    for x in map(str, xrange(1, (size**2)+1)):
        yield x
