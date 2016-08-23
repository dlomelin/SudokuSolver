'''.'''

from sudoku_solver.utilities import instantiate_matrix, double_iter, number_set


class SudokuBlock(object):
    ''' Class that represents a NxN sudoku block with N^2 cells '''

    def __init__(self, num_list):
        # Set the values to what the user passed in, which should be a list of lists
        # Ex: [['9', '7', ' '], [' ', ' ', ' '], ['5', '6', '3']]
        self.__store_values(num_list)

        # Store data related to the data that was passed in
        self.__store_square_data()

        # Make sure the values passed in are in a valid format
        self.__validate_num_list()

        # Creates new candidates for each of the N^2 cells
        self.__create_candidate_numbers()

        # Remove all candidates for cells that have been assigned a number
        self.__eliminate_known_numbers()

    def __eq__(self, other):
        return self.__values == other.__values  # pylint: disable=protected-access

    ##################
    # Public Methods #
    ##################

    def valid(self):
        '''
        Checks if every cell in the block contains a unique number.

        :param:  None

        :return:  Boolean
        '''
        valid_solution = True
        valid_nums = set()

        # Iterate through each of the N^2 cells
        for row, col in double_iter(self.__square_size):
            # Check if there is a valid digit in the cell
            num = self.get_value(row, col)
            if num:
                valid_nums.add(num)
            else:
                valid_solution = False
                break

        # Checks if there are N^2 unique numbers
        if len(valid_nums) != self.__cell_count:
            valid_solution = False

        return valid_solution

    def complete(self):
        '''
        Checks if every cell in the block contains a number.

        :param:  None

        :return:  Boolean
        '''
        all_complete = True

        # Iterate through each of the N^2 cells
        for row, col in double_iter(self.__square_size):
            # Check if the cell contains a digit
            if not self.get_value(row, col):
                all_complete = False
                break

        return all_complete

    def get_value(self, row, col):
        '''
        Returns the assigned value for the cell if one exists; otherwise returns None

        :param row:  Integer
        :param col:  Integer

        :return:  String (integer)
        '''
        value = None
        if self.__values[row][col].isdigit():
            value = self.__values[row][col]
        return value

    def set_value(self, num, row, col):
        '''
        Sets the number at position (row, col)

        :param num:  Integer
        :param row:  Integer
        :param col:  Integer

        :return:  None
        '''
        self.__values[row][col] = str(num)

    ##
    # CANDIDATE METHODS BELOW
    # Candidates keep track of all the possible numbers that are valid options
    # for a given cell.  As cells across the puzzle are resolved, candidates
    # are modified to remove numbers that are no longer possible at the
    # current cell.
    # Candidates are represented by a set() of numbers from 1-N^2
    ##

    def get_candidates(self, row, col):
        '''
        Returns the notes for the specified (row, col)

        :param row:  Integer
        :param col:  Integer

        :return:  Set of integers cast as strings
        '''
        return self.__candidates[row][col]

    def delete_candidate_number(self, num, row, col):
        '''
        Deletes a number from a given set of notes at position (row, col)

        :param num:  Integer
        :param row:  Integer
        :param col:  Integer

        :return:  None
        '''
        self.__candidates[row][col].discard(str(num))

    def clear_candidates(self, row, col):
        '''
        Deletes all numbers for a set of notes

        :param row:  Integer
        :param col:  Integer

        :return:  None
        '''
        self.__candidates[row][col] = set()

    ###################
    # Private Methods #
    ###################

    ###### START
    # __init__ methods
    #
    def __store_values(self, num_list):
        self.__values = num_list
        for i in xrange(len(self.__values)):
            for j in xrange(len(self.__values[i])):
                self.__values[i][j] = str(self.__values[i][j])

    # Stores information related to the size of the input data
    def __store_square_data(self):
        self.__square_size = len(self.__values)
        self.__cell_count = self.__square_size ** 2

    # Make sure the values passed in are in a valid format
    def __validate_num_list(self):
        # Make sure the correct number of lists are passed in
        list_len = len(self.__values)
        if list_len != self.__square_size:
            raise Exception(
                'Invalid number of lists passed to SudokuBlock object.  '
                'Must contain %s lists.' % (self.__square_size)
            )

        num_count = 0
        num_set = set()
        for item_list in self.__values:
            item_len = len(item_list)
            if item_len != self.__square_size:
                raise Exception(
                    'Invalid number of items passed to SudokuBlock object.  '
                    'Must contain %s items.' % (self.__square_size)
                )
            for num in item_list:
                if num.isdigit():
                    num_count += 1
                    num_set.add(num)
        num_len = len(num_set)
        if num_len != num_count:
            raise Exception('Duplicate numbers pre-assigned to SudokuBlock object.')

    def __create_candidate_numbers(self):
        ''' Creates new notes for each of the N^2 cells '''
        # Creates a NxN matrix.  Each cell will have its own set of notes
        self.__candidates = instantiate_matrix(self.__square_size)

        # Iterate through each of the N^2 cells and assign a new set of notes
        for row, col in double_iter(self.__square_size):
            self.__candidates[row][col] = number_set(self.__square_size)

    # Remove all notes for cells that have been assigned a number
    def __eliminate_known_numbers(self):
        # Iterate through each of the N^2 cells
        for row, col in double_iter(self.__square_size):
            # Remove all notes for the cell if it has been assigned a number
            if self.get_value(row, col):
                self.clear_candidates(row, col)
    #
    # __init__ methods
    ###### END
