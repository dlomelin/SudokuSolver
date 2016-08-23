'''.'''


class SudokuCoordinates(object):
    ''' Simple class wrapper to make coordinate retrieval easier '''

    def __init__(self, blockRow, blockCol, row, col):
        self.blockRow = blockRow
        self.blockCol = blockCol
        self.row = row
        self.col = col

    def __repr__(self):
        ''' Just for thoroughness '''
        return '%s(%s,%s,%s,%s)' % (self.__class__.__name__, self.blockRow, self.blockCol, self.row, self.col)

    def __hash__(self):
        ''' Allows for storing object in a set([]) and using a sets' methods correctly '''
        return hash((self.blockRow, self.blockCol, self.row, self.col))

    def __str__(self):
        ''' Allows for using str(obj) '''
        return '(%s,%s,%s,%s)' % (self.blockRow, self.blockCol, self.row, self.col)

    # Allows for testing obj1 == obj2
    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.alignsByRow(other) and self.alignsByCol(other)

    # Allows for testing obj1 != obj2
    def __ne__(self, other):
        return not self.__eq__(other)

    ##################
    # Public Methosd #
    ##################

    def alignsByBlock(self, other):
        return self.blockRow == other.blockRow and self.blockCol == other.blockCol

    def alignsByRow(self, other):
        return self.blockRow == other.blockRow and self.row == other.row

    def alignsByCol(self, other):
        return self.blockCol == other.blockCol and self.col == other.col
