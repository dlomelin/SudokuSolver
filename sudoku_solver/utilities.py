'''.'''


def instantiate_matrix(size):
    '''
    Creates a size x size matrix

    :param size:  Integer - Number of columns and rows

    :return:  List of Lists
    '''
    matrix = []
    for i in xrange(size):
        matrix.append([])
        for _ in xrange(size):
            matrix[i].append([])
    return matrix


def double_iter(num):
    '''
    Iterator returns pairs of numbers

    :param num:  Integer

    :yield:  Tuple of Integers
    '''
    for i in xrange(num):
        for j in xrange(num):
            yield i, j


def number_set(size):
    '''
    Returns a set of numbers from 1 to size^2

    :param size:  Integer - Number of columns and rows

    :return:  Set of Strings from 1 to size^2
    '''

    num_list = []
    for i in cell_id_iter(size):
        num_list.append(i)
    return set(num_list)


def num_dict_list(size):
    '''
    Returns a dictionary with keys being numbers 1-size^2 and values as empty lists
    '''
    dict_list = {}
    for i in cell_id_iter(size):
        dict_list[i] = []
    return dict_list


def cell_id_iter(size):
    '''
    Yields strings of numbers from 1 to size^2

    :param size:  Integer

    :yield:  Strings from 1 to size^2
    '''
    for i in map(str, xrange(1, (size**2)+1)):
        yield i
