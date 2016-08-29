'''.'''


class SudokuCoordinates(object):
    ''' Simple class wrapper to make coordinate retrieval easier '''

    def __init__(self, block_row, block_col, row, col):
        self.block_row = block_row
        self.block_col = block_col
        self.row = row
        self.col = col

    def __hash__(self):
        ''' Allows for storing object in a set([]) and using a sets' methods correctly '''
        return hash((self.block_row, self.block_col, self.row, self.col))

    def __str__(self):
        ''' Allows for using str(obj) '''
        return '(%s,%s,%s,%s)' % (self.block_row, self.block_col, self.row, self.col)

    def __eq__(self, other):
        ''' Allows for testing obj1 == obj2 '''
        return isinstance(other, self.__class__) and \
            self.aligns_by_row(other) and \
            self.aligns_by_col(other)

    def __ne__(self, other):
        ''' Allows for testing obj1 != obj2 '''
        return not self.__eq__(other)

    ##################
    # Public Methosd #
    ##################

    def aligns_by_block(self, other):
        '''
        Determine if the coordinates are both in the same exact block

        :param other:  SudokuCoordinates - Another instance of the same class

        :return:  Boolean
        '''
        return self.block_row == other.block_row and self.block_col == other.block_col

    def aligns_by_row(self, other):
        '''
        Determine if the coordinates are both in the same exact row

        :param other:  SudokuCoordinates - Another instance of the same class

        :return:  Boolean
        '''
        return self.block_row == other.block_row and self.row == other.row

    def aligns_by_col(self, other):
        '''
        Determine if the coordinates are both in the same exact column

        :param other:  SudokuCoordinates - Another instance of the same class

        :return:  Boolean
        '''
        return self.block_col == other.block_col and self.col == other.col
