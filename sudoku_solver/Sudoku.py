'''.'''  # pylint: disable=too-many-lines

import os
import sys
from itertools import combinations, chain

from sudoku_solver.utilities import instantiate_matrix, double_iter, number_set, num_dict_list
from sudoku_solver.SudokuBlock import SudokuBlock
from sudoku_solver.SudokuCoordinates import SudokuCoordinates


class Sudoku(object):
    ''' Class that provides interface to solving and visualizing Sudoku puzzles '''

    def __init__(self, **args):

        # Make sure one of the required arguments was passed in
        fields_to_check = set(['file', 'data'])
        self.__check_input_arguments(fields_to_check, args)

        # Loads the user specified data
        self.__load_input_data(args)

        # Mark this puzzle as unsolved
        self.__set_solved_false()

        self.__techniques_used = {}

    ########################
    # Overloaded Operators #
    ########################

    def __eq__(self, other):
        return self.grid_values() == other.grid_values()

    def __str__(self):
        row_delimeter = self.__row_delimeter()

        # Gets the currently assigned values to the sudoku grid
        values = self.grid_values()

        # Create a header and center it
        if self.__puzzle_solved():
            status = 'Solution'
        else:
            status = 'Incomplete'
        status = status.center(len(row_delimeter))

        string = '%s\n' % (status)
        for row in xrange(len(values)):
            # Every 3rd block gets a delimeter
            if row % 3 == 0:
                string += '%s\n' % (row_delimeter)

            # Iterate through each number
            for col in xrange(len(values[row])):
                # Every 3rd number gets a column delimeter
                if col % 3 == 0:
                    string += '| '

                string += '%s ' % (values[row][col])

            string += '|\n'
        string += '%s\n' % (row_delimeter)

        return string

    ##################
    # Public Methods #
    ##################

    def grid_values(self):
        '''
        Returns a list of lists with the current grid values.
        Unknown positions are represented by a period.

        :param:  None

        :return:  List of Lists
        '''
        values = []

        for mat_row, row in double_iter(3):
            values.append([])
            for mat_col, col in double_iter(3):
                num = self.get_cell_value(mat_row, mat_col, row, col)
                if not num:
                    num = '.'

                values[-1].append(num)

        return values

    def solve(self):
        '''
        Attempts to figure out the values for all cells in the sudoku grid.

        :param:  None

        :return:  None
        '''

        # Mark this puzzle as unsolved
        self.__set_solved_false()

        while True:
            # Mark this iteration as having no changes
            # Any modifications to the puzzle will mark the puzzle as changed
            # otherwise the loop will quit
            self.__set_change_false()

            # Assign values to a row or column where only a single value is possible
            self.__set_singletons()

            # Reduce numbers based on lone hint pairs lying along the same row or column
            # within 1 block.  Removes the number along the same row or column but in
            # neighboring blocks.
            self.__reduce_candidate_lines()

            # Reduce numbers based on using the xwing, swordfish, and jellyfish techniques
            self.__reduce_xwing_sword_jelly_fish()

            # Reduce numbers based on naked pairs/trios
            self.__reduce_naked_sets()

            # Reduce numbers based on using the Ywing method
            self.__reduce_ywing()

            # Reduce numbers based on using the XYZwing method
            self.__reduce_xyz_wing()

            # Reduce numbers based on using the WXYZwing method
            self.__reduce_wxyz_wing()

            # Reduce numbers based on multiple lines
            self.__reduce_multiple_lines()

            if not self.__puzzle_changed():
                break

        # If puzzle was complete, make sure the blocks, rows, and columns
        # all adhere to a valid sudoku solution.
        if self.complete():
            self.__check_valid()

    def complete(self):
        '''
        Checks if every cell has been filled in with a number.
        Does not check if the numbers are valid though.

        :param:  None

        :return:  Boolean
        '''

        all_complete = True

        # Iterate through each of the 9 blocks
        for block_row, block_col in double_iter(3):
            # Check if the block is complete
            if not self.__complete_block(block_row, block_col):
                all_complete = False
                break

        return all_complete

    def print_candidates(self, fh_out=sys.stdout):
        '''
        Prints the current candidates used to solve the puzzle in a human readable format

        :param fh_out:  Filehandle - Optional

        :return:  None
        '''
        candidate_nums = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']]

        header = 'Current Candidates'.center(len(self.__block_row_split()))

        fh_out.write('%s\n' % (header))
        for block_row in xrange(3):  # pylint: disable=too-many-nested-blocks
            if block_row == 0:
                fh_out.write('%s\n' % (self.__block_row_split()))
            for row in xrange(3):
                for i in xrange(len(candidate_nums)):
                    fh_out.write('||')
                    for block_col, col in double_iter(3):
                        num_string = ''
                        candidates = self.get_cell_candidates(block_row, block_col, row, col)
                        for num in candidate_nums[i]:
                            if num in candidates:
                                num_string += '%s' % (num)
                            else:
                                num_string += ' '
                        if col == 2:
                            col_split = '||'
                        else:
                            col_split = '|'
                        fh_out.write(' %s %s' % (num_string, col_split))
                    fh_out.write('\n')
                if row == 2:
                    fh_out.write('%s\n' % (self.__block_row_split()))
                else:
                    fh_out.write('%s\n' % (self.__row_split()))

    def print_techniques_used(self, fh_out=sys.stdout):
        '''
        Prints out a list of techniques used and how frequently they were used

        :param fh_out:  Filehandle - Optional

        :return:  None
        '''

        fh_out.write('Candidates Removed By:\n')
        for technique in sorted(self.__techniques_used):
            fh_out.write('  %s: %s\n' % (technique, self.__techniques_used[technique]))
        fh_out.write('\n')

    def get_cell_value(self, block_row, block_col, row, col):
        '''
        Returns the value of a cell at the specified coordinates

        :param block_row:  Integer
        :param block_col:  Integer
        :param row:  Integer
        :param col:  Integer

        :return:  String (integer)
        '''
        return self.__matrix[block_row][block_col].get_value(row, col)

    def get_cell_candidates(self, block_row, block_col, row, col):
        '''
        Returns the set() of candidates at the specified coordinates

        :param block_row:  Integer
        :param block_col:  Integer
        :param row:  Integer
        :param col:  Integer

        :return:  Set of integers cast as strings
        '''
        return self.__matrix[block_row][block_col].get_candidates(row, col)

    ###################
    # Private Methods #
    ###################

    ###### START
    # Instance variable setters and getters
    #
    def __puzzle_changed(self):
        return self.__change_status

    # Lets the solver know changes were made
    def __set_change_true(self, technique_used):
        self.__change_status = True  # pylint: disable=attribute-defined-outside-init
        self.__track_techniques_used(technique_used)

    def __set_change_false(self):
        self.__change_status = False  # pylint: disable=attribute-defined-outside-init

    def __puzzle_solved(self):
        return self.__solved_status

    def __set_solved_false(self):
        self.__solved_status = False

    def __track_techniques_used(self, technique):
        if technique:
            try:
                self.__techniques_used[technique] += 1
            except KeyError:
                self.__techniques_used[technique] = 1
    #
    # instance variable setters and getters
    ###### END

    ###### START
    # Wrappers around SudokuBlock methods
    #
    def __delete_candidate_number(  # pylint: disable=too-many-arguments
            self,
            num,
            block_row,
            block_col,
            row,
            col):
        self.__matrix[block_row][block_col].delete_candidate_number(num, row, col)

    def __set_cell_value(  # pylint: disable=too-many-arguments
            self,
            num,
            block_row,
            block_col,
            row,
            col):
        ''' Sets the value of the specified cell '''
        self.__matrix[block_row][block_col].set_value(num, row, col)

    # Clears out available candidates from the specified cell
    def __clear_cell_candidates(self, block_row, block_col, row, col):
        self.__matrix[block_row][block_col].clear_candidates(row, col)

    def __valid_block(self, block_row, block_col):
        return self.__matrix[block_row][block_col].valid()

    def __complete_block(self, block_row, block_col):
        return self.__matrix[block_row][block_col].complete()
    #
    # Wrappers around SudokuBlock methods
    ###### END

    ###### START
    # Shared methods
    #
    # Sets the value of the specified cell and adjusts the candidates in the
    # necessary row, column, and block.
    def __set_value(  # pylint: disable=too-many-arguments
            self,
            num,
            block_row,
            block_col,
            row,
            col,
            technique_used=None):

        # Sets the value of the specified cell
        self.__set_cell_value(num, block_row, block_col, row, col)

        # Clears out available candidates from the specified cell
        self.__clear_cell_candidates(block_row, block_col, row, col)

        # Clears out available candidates from the affected block, row, and column
        self.__remove_candidate_seen_by(num, block_row, block_col, row, col)

        # Let the solver know changes were made
        self.__set_change_true(technique_used)

    def __clear_cell_candidate_and_set(  # pylint: disable=too-many-arguments
            self,
            num,
            block_row,
            block_col,
            row,
            col,
            technique_used):
        '''
        Deletes the specified number from the cell's candidates.  If there is only
        one number left in the candidates, then it sets the value
        '''

        candidates = self.get_cell_candidates(block_row, block_col, row, col)
        if num in candidates:
            self.__delete_candidate_number(num, block_row, block_col, row, col)

            nums = list(candidates)
            if len(nums) == 1:
                self.__set_value(
                    nums[0],
                    block_row,
                    block_col,
                    row,
                    col,
                    technique_used,
                )
            else:
                # Let the solver know changes were made
                self.__set_change_true(technique_used)

    # Iterate through each cell, determine which numbers have already been
    # assigned, and remove them from the list of unassigned numbers
    def __find_unassigned_nums(self, cell_coordinates_list):
        # Create a list of all possible numbers that can be assigned to the current set of cells
        unassigned_nums = number_set(3)

        # Iterate through each cell's coordinates
        for cell_coords in cell_coordinates_list:

            # Remove the already assigned number in the current cell
            # from the list of possible numbers
            num = self.get_cell_value(
                cell_coords.block_row,
                cell_coords.block_col,
                cell_coords.row,
                cell_coords.col,
            )
            if num:
                unassigned_nums.discard(num)

        return unassigned_nums

    def __remove_candidate_seen_by(  # pylint: disable=too-many-arguments
            self,
            num,
            block_row,
            block_col,
            row,
            col):
        ''' Clears out available candidates from the affected block, row, and column '''

        # Remove the number from the candidates along the block
        self.__remove_candidate_by_iter(
            num,
            self.__block_cell_coords_iter,
            block_row,
            block_col,
            [],
        )

        # Remove the number from the candidates along the row
        self.__remove_candidate_by_iter(
            num,
            self.__row_cell_coords_iter,
            block_row,
            row,
            [],
        )

        # Remove the number from the candidates along the column
        self.__remove_candidate_by_iter(
            num,
            self.__col_cell_coords_iter,
            block_col,
            col,
            [],
        )

    def __remove_candidate_by_iter(  # pylint: disable=too-many-arguments
            self,
            num,
            coord_iter,
            coord_pos1,
            coord_pos2,
            skip_coords_list,
            technique=None):
        '''
        Goes through each cell passed from the iterator and removes
        the number from the cell's candidates
        '''
        # Iterate through each cell
        for coords in coord_iter(coord_pos1, coord_pos2):

            # Skip the cells that are the skip list
            if not self.__coords_in_list(coords, skip_coords_list):
                # Remove the numbers from the cell candidates
                self.__clear_cell_candidate_and_set(
                    num,
                    coords.block_row,
                    coords.block_col,
                    coords.row,
                    coords.col,
                    technique,
                )

    @staticmethod
    def __coords_in_list(coords, skip_list):
        item_in_list = False
        for item in skip_list:
            if item == coords:
                item_in_list = True
                break
        return item_in_list

    def __coords_intersection(self, *coords_list):
        seen_coords_list = []
        for coords in coords_list:
            shared_coords = self.__coords_seen_by(coords)
            seen_coords_list.append(shared_coords)

        intersecting_coords = seen_coords_list[0]
        for i in xrange(1, len(seen_coords_list)):
            intersecting_coords = intersecting_coords.intersection(seen_coords_list[i])

        return intersecting_coords

    def __coords_seen_by(self, center_coord):
        '''
        Returns a set of all coordinates that are in the same
        block, row, and column as the input coordinates
        '''
        unique_coords = set()

        # Store all coordinates in the same block as center_coord
        for coord in self.__block_cell_coords_iter(center_coord.block_row, center_coord.block_col):
            unique_coords.add(coord)

        # Store all coordinates in the same row as center_coord
        for coord in self.__row_cell_coords_iter(center_coord.block_row, center_coord.row):
            unique_coords.add(coord)

        # Store all coordinates in the same column as center_coord
        for coord in self.__col_cell_coords_iter(center_coord.block_col, center_coord.col):
            unique_coords.add(coord)

        # Remove center_coord
        unique_coords.discard(center_coord)

        return unique_coords

    def __valid_cells_seen_by(self, coords, pivot_cell_candidates, valid_cell_function):
        coords_list = []
        candidates_list = []

        # Iterate across all cells that are seen by the current cell
        for cell_coords in self.__coords_seen_by(coords):

            # Look for cells that pass the criteria set forth by valid_cell_function
            cell_candidates = self.get_cell_candidates(
                cell_coords.block_row,
                cell_coords.block_col,
                cell_coords.row,
                cell_coords.col,
            )
            if valid_cell_function(pivot_cell_candidates, cell_candidates):
                coords_list.append(cell_coords)
                candidates_list.append(cell_candidates)

        return coords_list, candidates_list

    @staticmethod
    def __candidates_intersection(*candidates_list):
        candidates_intersection = candidates_list[0]
        for i in xrange(1, len(candidates_list)):
            candidates_intersection = candidates_intersection.intersection(candidates_list[i])

        return candidates_intersection

    @staticmethod
    def __candidates_union(*candidates_list):
        candidates_union = candidates_list[0]
        for i in xrange(1, len(candidates_list)):
            candidates_union = candidates_union.union(candidates_list[i])

        return candidates_union
    #
    # Shared methods
    ###### END

    ###### START
    # __init__ methods
    #
    @staticmethod
    def __check_input_arguments(fields_to_check, args):
        # Check if one of the required arguments was supplied
        missing_fields = True
        for field in args:
            if field in fields_to_check:
                missing_fields = False

        if missing_fields:
            raise Exception(
                'One of the following required fields was not provided: %s' % (
                    ','.join(fields_to_check),
                )
            )

    # Loads the user specified data
    def __load_input_data(self, args):
        if 'file' in args:
            # Parses file with starting Sudoku numbers and loads object
            self.__load_from_file(args['file'])
        elif 'data' in args:
            # Parses list of lists with starting Sudoku numbers and loads object
            self.__load_from_data(args['data'])

    def __load_from_file(self, file_name):
        ''' Loads data from a file '''
        if os.path.isfile(file_name):
            data = []

            # Converts file contents into a list of lists
            fh_in = open(file_name, 'rU')
            for line in fh_in:
                nums = self.__parse_file_line(line)
                data.append(nums)
            fh_in.close()

            # Loads data from a list of lists
            self.__load_from_data(data)

        else:
            raise Exception('%s is not a valid file or does not exist.' % (file_name))

    # Loads data from a list of lists
    def __load_from_data(self, data):
        temp_matrix = instantiate_matrix(3)
        current_block_row = 0

        for nums in data:
            # Every 3 lines get incremented
            if self.__current_block_row_full(temp_matrix, current_block_row):
                current_block_row += 1

            temp_matrix[current_block_row][0].append(nums[0:3])
            temp_matrix[current_block_row][1].append(nums[3:6])
            temp_matrix[current_block_row][2].append(nums[6:9])

        self.__instantiate_sudoku_matrix(temp_matrix)

    @staticmethod
    def __parse_file_line(line):
        ''' Parses the line of a file into a valid list '''
        # Strip newline character
        line = line.strip('\n')

        # Periods are allowed for unknown positions by converting them to spaces
        line = line.replace('.', ' ')

        # Make sure there are at least 9 positions in the line
        # Right padded spaces will be turned into unknowns
        line = line.ljust(9)

        # Convert to a list of numbers
        return list(line)

    @staticmethod
    def __current_block_row_full(matrix, block_row):
        ''' Returns True if the current row of blocks are all full '''
        return len(matrix[block_row][0]) == 3 and \
            len(matrix[block_row][1]) == 3 and \
            len(matrix[block_row][2]) == 3

    def __instantiate_sudoku_matrix(self, temp_matrix):
        ''' Converts the temporary matrix into one that has SudokuBlock objects '''

        self.__matrix = instantiate_matrix(3)  # pylint: disable=attribute-defined-outside-init
        # Iterate through each of the 9 blocks
        for block_row, block_col in double_iter(3):
            self.__matrix[block_row][block_col] = SudokuBlock(temp_matrix[block_row][block_col])

        # Adjusts the candidates based on the initial values of the sudoku grid.
        self.__clear_initial_candidates()

    # Adjusts the candidates based on the initial values of the sudoku grid.
    def __clear_initial_candidates(self):

        # Iterate through each block in the sudoku grid
        for cell_coordinates_list in self.__block_coords_iter():

            # Iterate through each cell's coordinates
            for cell_coords in cell_coordinates_list:

                # If the cell has a number assigned then clear the block, row, and column candidates
                num = self.get_cell_value(
                    cell_coords.block_row,
                    cell_coords.block_col,
                    cell_coords.row,
                    cell_coords.col,
                )
                if num:
                    # Clears out available candidates from the affected block, row, and column
                    self.__remove_candidate_seen_by(
                        num,
                        cell_coords.block_row,
                        cell_coords.block_col,
                        cell_coords.row,
                        cell_coords.col,
                    )
    #
    # __init__ methods
    ###### END

    ###### START
    # __str__ methods
    #
    @staticmethod
    def __row_delimeter():
        return '-------------------------'
    #
    # __str__ methods
    ###### END

    ###### START
    # print_candidates methods
    #
    @staticmethod
    def __row_split():
        return '-----------------------------------------------------------'

    @staticmethod
    def __block_row_split():
        return '==========================================================='
    #
    # print_candidates methods
    ###### END

    ###### START
    # __set_singletons methods
    #
    def __set_singletons(self):
        # Assign singletons within rows
        self.__set_singleton_candidates(self.__row_coords_iter)

        # Assign singletons within columns
        self.__set_singleton_candidates(self.__column_coords_iter)

    def __set_singleton_candidates(self, coord_iter):

        # Iterate through each line in the sudoku grid
        # The lines will be all rows or all columns, depending on what was passed
        # to this method in coord_iter
        for cell_coordinates_list in coord_iter():  # pylint: disable=too-many-nested-blocks

            # Generate list of numbers that can still be assigned to the
            # remaining cells in the row or column
            unassigned_nums = self.__find_unassigned_nums(cell_coordinates_list)

            # Iterate through the set of unassigned numbers
            for current_value in unassigned_nums:

                available_cell_count = 0
                available_cell_coords = None

                # Iterate through each cell's coordinates
                for cell_coords in cell_coordinates_list:

                    # If that position was already assigned a number then skip it
                    if not self.get_cell_value(
                            cell_coords.block_row,
                            cell_coords.block_col,
                            cell_coords.row,
                            cell_coords.col):
                        # Grab the set() of available values for the current cell
                        candidates = self.get_cell_candidates(
                            cell_coords.block_row,
                            cell_coords.block_col,
                            cell_coords.row,
                            cell_coords.col,
                        )
                        # Keep track of how many positions will allow the current value
                        if current_value in candidates:
                            available_cell_count += 1
                            available_cell_coords = cell_coords

                            # Once the available cell count is greater than 1, there is no point
                            # in going forward because we need singletons
                            if available_cell_count > 1:
                                break

                # Assuming there is only 1 cell that can accept the current value
                # then set that cell's value
                if available_cell_count == 1:
                    self.__set_value(
                        current_value,
                        available_cell_coords.block_row,
                        available_cell_coords.block_col,
                        available_cell_coords.row,
                        available_cell_coords.col,
                    )
    #
    # __set_singletons methods
    ###### END

    ###### START
    # __reduce_candidate_lines methods
    #
    # Reduce numbers based on lone hint pairs lying along the same row or column within 1 block.
    # Removes the number along the same row or column but in neighboring blocks.
    def __reduce_candidate_lines(self):
        technique = 'Candidate Lines'

        # Iterate through all sudoku grid blocks
        for cell_coordinates_list in self.__block_coords_iter():
            # Create a list of all unassigned numbers and the coordinates where they are found
            hint_coords = self.__generate_hint_coords(cell_coordinates_list)

            # Iterate through each unassigned number
            for num in hint_coords:

                # Candidate lines method works by aligning
                if len(hint_coords[num]) == 2:

                    # Store variables just to make code more readable
                    coords1 = hint_coords[num][0]
                    coords2 = hint_coords[num][1]

                    # Candidate line lies along a row, therefore
                    # remove number from the rest of the row
                    if coords1.aligns_by_row(coords2):
                        # Remove the number from the candidates along the row
                        self.__remove_candidate_by_iter(
                            num,
                            self.__row_cell_coords_iter,
                            coords1.block_row,
                            coords1.row,
                            [coords1, coords2],
                            technique,
                        )

                    # Candidate line lies along a column, therefore
                    # remove number from the rest of the column
                    elif coords1.aligns_by_col(coords2):
                        # Remove the number from the candidates along the column
                        self.__remove_candidate_by_iter(
                            num,
                            self.__col_cell_coords_iter,
                            coords1.block_col,
                            coords1.col,
                            [coords1, coords2],
                            technique,
                        )

    # Stores the coordinates for all hint positions
    def __generate_hint_coords(self, cell_coordinates_list):
        hint_coords = num_dict_list(3)

        # Iterate through each cell's coordinates
        for cell_coords in cell_coordinates_list:
            # Store the coordinates where all numbers are found
            candidates = self.get_cell_candidates(
                cell_coords.block_row,
                cell_coords.block_col,
                cell_coords.row,
                cell_coords.col,
            )
            for num in candidates:
                hint_coords[num].append(cell_coords)

        return hint_coords
    #
    # __reduce_candidate_lines methods
    ###### END

    ###### START
    # __reduce_xwing_sword_jelly_fish methods
    #
    def __reduce_xwing_sword_jelly_fish(self):

        # 2 = Xwing  3 = Swordfish  4 = Jellyfish
        for cell_count in xrange(2, 5):
            # Search for valid xwing cells along rows to reduce candidates along the columns
            self.__reduce_xwing_sword_jelly_row(cell_count)

            # Search for valid xwing cells along columns to reduce candidates along the rows
            self.__reduce_xwing_sword_jelly_col(cell_count)

    def __reduce_xwing_sword_jelly_row(self, cell_count):
        technique = self.__x_sword_jelly_technique(cell_count)
        potential_cells = self.__potential_rectangle_cells(cell_count, self.__row_coords_iter)

        # Iterate through each number
        for num in potential_cells:

            # Iterate through all possible row triplets
            for dataset in combinations(potential_cells[num], cell_count):

                # Checks if the current triplet of rows forms a valid Swordfish across 3 columns
                if self.__valid_rectangle_col_cells(cell_count, *dataset):

                    # Iterate through the 3 affected columns
                    for block_coords in self.__columns_in_common(*dataset):

                        # Remove the number from the candidates along the column,
                        # excluding the cells that make up the Swordfish
                        self.__remove_candidate_by_iter(
                            num,
                            self.__col_cell_coords_iter,
                            block_coords.block_col,
                            block_coords.col,
                            list(chain(*dataset)),
                            technique,
                        )

    def __reduce_xwing_sword_jelly_col(self, cell_count):
        technique = self.__x_sword_jelly_technique(cell_count)

        potential_cells = self.__potential_rectangle_cells(cell_count, self.__column_coords_iter)

        # Iterate through each number
        for num in potential_cells:

            # Iterate through all possible cell_count cells
            for dataset in combinations(potential_cells[num], cell_count):

                # Checks if the current triplet of rows forms a valid Swordfish across 3 rows
                if self.__valid_rectangle_row_cells(cell_count, *dataset):

                    # Iterate through the 3 affected rows
                    for block_coords in self.__rows_in_common(*dataset):

                        # Remove the number from the candidates along the row, excluding the cells
                        # that make up the Swordfish
                        self.__remove_candidate_by_iter(
                            num,
                            self.__row_cell_coords_iter,
                            block_coords.block_row,
                            block_coords.row,
                            list(chain(*dataset)),
                            technique,
                        )

    @staticmethod
    def __valid_rectangle_row_cells(cell_count, *data_list):

        row_data = DictCounter()
        complete_data_lists = True

        for data in data_list:
            if not data:
                complete_data_lists = False
            for coords in data:
                row = '%s,%s' % (coords.block_row, coords.row)
                row_data.add(row)

        return row_data.key_count() == cell_count and row_data.counts_ge(2) and complete_data_lists

    @staticmethod
    def __valid_rectangle_col_cells(cell_count, *data_list):

        col_data = DictCounter()
        complete_data_lists = True

        for data in data_list:
            if not data:
                complete_data_lists = False
            for coords in data:
                col = '%s,%s' % (coords.block_col, coords.col)
                col_data.add(col)

        return col_data.key_count() == cell_count and col_data.counts_ge(2) and complete_data_lists

    @staticmethod
    def __rows_in_common(*data_list):
        row_set = set()

        for data in data_list:
            for coords in data:
                row_set.add(SudokuCoordinates(coords.block_row, 0, coords.row, 0))

        return row_set

    @staticmethod
    def __columns_in_common(*data_list):
        col_set = set()

        for data in data_list:
            for coords in data:
                col_set.add(SudokuCoordinates(0, coords.block_col, 0, coords.col))

        return col_set

    # Search all rows/columns for cells that have between 2 and cell_count candidates
    # cell_count is dependent on the technique.  This method is used in the xwing,
    # swordfish, jellyfish type puzzles
    def __potential_rectangle_cells(self, cell_count, coord_iter):

        potential_cells = num_dict_list(3)

        # Iterate through each row/cell in the sudoku grid
        for cell_coordinates_list in coord_iter():
            hint_coords = num_dict_list(3)

            # Iterate through each cell's coordinates
            for cell_coords in cell_coordinates_list:

                # Loop through all candidates in the current cell
                candidates = self.get_cell_candidates(
                    cell_coords.block_row,
                    cell_coords.block_col,
                    cell_coords.row,
                    cell_coords.col,
                )
                for num in candidates:
                    # Store the current coordinates
                    hint_coords[num].append(cell_coords)

            # Keep only the cells that have between 2 and cell_count candidates left in the row/col
            for num in hint_coords:
                if 2 <= len(hint_coords[num]) <= cell_count:
                    potential_cells[num].append(hint_coords[num])

        return potential_cells

    @staticmethod
    def __x_sword_jelly_technique(cell_count):
        techniques = {
            2: 'X-Wing',
            3: 'Sword-Fish',
            4: 'Jelly-Fish',
        }
        try:
            return techniques[cell_count]
        except:
            raise Exception('Invalid  size used: %s.  Please modify code' % (cell_count))
    #
    # __reduce_xwing_sword_jelly_fish methods
    ###### END

    ###### START
    # __reduce_naked_sets methods
    #
    def __reduce_naked_sets(self):
        # Reduce naked sets by row
        self.__find_naked_sets(self.__row_coords_iter)

        # Reduce naked sets by column
        self.__find_naked_sets(self.__column_coords_iter)

        # Reduce naked sets by block
        self.__find_naked_sets(self.__block_coords_iter)

    def __find_naked_sets(self, coord_iter):

        # Iterate through each row/column/block in the sudoku grid
        for cell_coordinates_list in coord_iter():
            candidate_coords = []
            candidate_list = []

            # Iterate through each cell's coordinates
            for cell_coords in cell_coordinates_list:

                # Store the cell's coordinates and candidates
                candidates = self.get_cell_candidates(
                    cell_coords.block_row,
                    cell_coords.block_col,
                    cell_coords.row,
                    cell_coords.col,
                )
                if candidates:
                    candidate_coords.append(cell_coords)
                    candidate_list.append(candidates)

            # set_size determines the naked set size, 2=naked pairs, 3=naked trios, 4=naked quads
            for set_size in xrange(2, 5):

                # Looks for naked sets in the current set of cells
                self.__find_naked_set_combinations(
                    set_size,
                    candidate_list,
                    candidate_coords,
                    cell_coordinates_list,
                )

    # Finds all valid naked sets.  If any are found, remove the numbers that are found in the naked
    # sets from all remaining neighboring cells.
    def __find_naked_set_combinations(
            self,
            set_size,
            candidate_list,
            candidate_coords,
            cell_coordinates_list):
        technique = self.__naked_set_technique(set_size)

        # Generates a list with all combinations of size set_size.
        # If candidate_list = [0, 1, 2] and set_size = 2, then 3 index_lists would be created
        # [0, 1], [0, 2], [1, 2]
        for index_list in combinations(xrange(len(candidate_list)), set_size):

            # Generate a set of the unique candidates in candidate_list
            unique_candidates = self.__combine_candidates(candidate_list, index_list)

            # Valid naked sets have been found when the number of unique numbers == the set size.
            # If 2 unique numbers are found in 2 cells, then you can remove those 2 numbers from
            # the remaining cells.  Same criteria applies if you find 3 unique numbers in 3 cells,
            # 4 unique numbers in 4 cells.
            if len(unique_candidates) == set_size:

                # Store the coordinates of the cells that made up the naked sets.
                skip_coords_list = []
                for i in index_list:
                    skip_coords_list.append(candidate_coords[i])

                # Iterate through each number in the naked set
                for num in unique_candidates:

                    # Iterate through each cell in the current row/column/block
                    for coords in cell_coordinates_list:

                        # Skip the cells that are in the skip list
                        # (cells that made up the naked set)
                        if not self.__coords_in_list(coords, skip_coords_list):

                            # Remove the numbers from the cell candidates
                            self.__clear_cell_candidate_and_set(
                                num,
                                coords.block_row,
                                coords.block_col,
                                coords.row,
                                coords.col,
                                technique,
                            )

    @staticmethod
    def __combine_candidates(set_list, coords):
        ''' Generate a set of the unique candidates in candidate_list '''
        unique_candidates = set()
        for index_num in coords:
            for num in list(set_list[index_num]):
                unique_candidates.add(num)
        return unique_candidates

    @staticmethod
    def __naked_set_technique(set_size):
        ''' Returns the technique name for a given set_size '''
        techniques = {
            2: 'Naked Pairs',
            3: 'Naked Trios',
            4: 'Naked Quads',
        }
        try:
            return techniques[set_size]
        except:
            raise Exception('Invalid naked set size used: %s.  Please modify code' % (set_size))
    #
    # __reduce_naked_sets methods
    ###### END

    ###### START
    # __reduce_ywing methods
    #
    def __reduce_ywing(self):

        # Iterate through each row in the sudoku grid
        for cell_coordinates_list in self.__row_coords_iter():

            # Iterate through each cell's coordinates
            for cell_coords in cell_coordinates_list:

                # Perform Y wing technique
                self.__find_potential_ywing(cell_coords)

    # Performs the Y wing technique
    def __find_potential_ywing(self, coords):
        technique = 'Y-Wing'

        # Look for a pivot cell that has 2 unknown candidates
        pivot_cell_candidates = self.get_cell_candidates(
            coords.block_row,
            coords.block_col,
            coords.row,
            coords.col,
        )

        # Y wing requires the pivot cell to contain exactly 2 candidates
        if len(pivot_cell_candidates) == 2:

            # Get a list of coordinates and candidates seen by the current cell
            coords_list, candidates_list = self.__valid_cells_seen_by(
                coords,
                pivot_cell_candidates,
                self.__valid_y_cell,
            )

            # Iterate through all pairs of cells
            for index_list in combinations(xrange(len(coords_list)), 2):

                # Create a set of common of candidate numbers from the pair of cells.
                # If there is only 1 candidate number and its not found in the pivot cell
                # then remove that number from the overlapping cells that can see one
                # another between the current pairs of cells.
                common_set = candidates_list[index_list[0]].intersection(
                    candidates_list[index_list[1]],
                )
                if len(common_set) == 1:
                    remove_num = common_set.pop()
                    if not remove_num in pivot_cell_candidates:
                        remove_coords = self.__coords_intersection(
                            coords_list[index_list[0]],
                            coords_list[index_list[1]],
                        )

                        for r_coords in remove_coords:
                            self.__clear_cell_candidate_and_set(
                                remove_num,
                                r_coords.block_row,
                                r_coords.block_col,
                                r_coords.row,
                                r_coords.col,
                                technique,
                            )

    @staticmethod
    def __valid_y_cell(pivot_cell_candidates, cell_candidates):
        '''
        Looks for a cell that has 2 candidate numbers and shares
        exactly 1 candidate between itself and the pivot cell
        '''
        return len(cell_candidates) == 2 and \
            len(cell_candidates.intersection(pivot_cell_candidates)) == 1
    #
    # __reduce_ywing methods
    ###### END

    ###### START
    # __reduce_xyz_wing methods
    #
    def __reduce_xyz_wing(self):

        # Iterate through each row in the sudoku grid
        for cell_coordinates_list in self.__row_coords_iter():

            # Iterate through each cell's coordinates
            for cell_coords in cell_coordinates_list:

                # Perform XYZ wing technique
                self.__find_potential_xyz_wing(cell_coords)

    def __find_potential_xyz_wing(self, coords):
        technique = 'XYZ-Wing'

        # Look for a pivot point that has 3 unknown candidates
        pivot_cell_candidates = self.get_cell_candidates(
            coords.block_row,
            coords.block_col,
            coords.row,
            coords.col,
        )

        # XYZ wing requires the pivot cell to contain exactly 3 candidates
        if len(pivot_cell_candidates) == 3:

            # Get a list of coordinates and candidates seen by the current cell
            coords_list, candidates_list = self.__valid_cells_seen_by(
                coords,
                pivot_cell_candidates,
                self.__valid_xyz_cell,
            )

            # Iterate through all pairs of cells
            for index_list in combinations(xrange(len(coords_list)), 2):

                # Union between each pair
                candidates_union = self.__candidates_union(
                    candidates_list[index_list[0]],
                    candidates_list[index_list[1]],
                )

                if len(candidates_union) == 3:
                    common_set = self.__candidates_intersection(
                        candidates_list[index_list[0]],
                        candidates_list[index_list[1]],
                    )
                    remove_num = common_set.pop()

                    remove_coords = self.__coords_intersection(
                        coords,
                        coords_list[index_list[0]],
                        coords_list[index_list[1]],
                    )

                    for r_coords in remove_coords:
                        self.__clear_cell_candidate_and_set(
                            remove_num,
                            r_coords.block_row,
                            r_coords.block_col,
                            r_coords.row,
                            r_coords.col,
                            technique,
                        )

    @staticmethod
    def __valid_xyz_cell(pivot_cell_candidates, cell_candidates):
        '''
        Look for cells that have 2 unknown candidates that are all found
        within the pivot cell
        '''
        return len(cell_candidates) == 2 and cell_candidates.issubset(pivot_cell_candidates)
    #
    # __reduce_xyz_wing methods
    ###### END

    ###### START
    # __reduce_wxyz_wing methods
    #
    def __reduce_wxyz_wing(self):

        # Iterate through each row in the sudoku grid
        for cell_coordinates_list in self.__row_coords_iter():

            # Iterate through each cell's coordinates
            for cell_coords in cell_coordinates_list:

                # Perform WXYZ wing technique
                self.__find_potential_wxyz_wing(cell_coords)

    def __find_potential_wxyz_wing(self, coords):
        technique = 'WXYZ-Wing'

        pivot_cell_candidates = self.get_cell_candidates(
            coords.block_row,
            coords.block_col,
            coords.row,
            coords.col,
        )

        # Get a list of coordinates and candidates seen by the current cell
        coords_list, candidates_list = self.__valid_cells_seen_by(
            coords,
            pivot_cell_candidates,
            self.__valid_wxyz_cell,
        )

        # Iterate through all pairs of cells
        for index_list in combinations(xrange(len(coords_list)), 3):

            candidates_union = self.__candidates_union(
                pivot_cell_candidates,
                candidates_list[index_list[0]],
                candidates_list[index_list[1]],
                candidates_list[index_list[2]],
            )

            if len(candidates_union) == 4:
                remove_num = self.__find_non_restricted_candidate(
                    [
                        candidates_list[index_list[0]],
                        candidates_list[index_list[1]],
                        candidates_list[index_list[2]],
                    ],
                    [
                        coords_list[index_list[0]],
                        coords_list[index_list[1]],
                        coords_list[index_list[2]],
                    ],
                )

                if not remove_num is None:

                    coords_for_intersection = []
                    if remove_num in pivot_cell_candidates:
                        coords_for_intersection.append(coords)
                    for i in xrange(3):
                        if remove_num in candidates_list[index_list[i]]:
                            coords_for_intersection.append(coords_list[index_list[i]])

                    remove_coords = self.__coords_intersection(*coords_for_intersection)

                    for r_coords in remove_coords:
                        self.__clear_cell_candidate_and_set(
                            remove_num,
                            r_coords.block_row,
                            r_coords.block_col,
                            r_coords.row,
                            r_coords.col,
                            technique,
                        )

    @staticmethod
    def __find_non_restricted_candidate(candidates_list, coords_list):
        candidate_set = set()

        # Iterate through each pair of cells
        for index_list in combinations(xrange(len(coords_list)), 2):

            # Look for cells that can't see each other
            if not coords_list[index_list[0]].aligns_by_row(coords_list[index_list[1]]) and \
                not coords_list[index_list[0]].aligns_by_col(coords_list[index_list[1]]) and \
                not coords_list[index_list[0]].aligns_by_block(coords_list[index_list[1]]):

                # Look for the numbers shared in common between both cells
                intersection_set = candidates_list[index_list[0]].intersection(
                    candidates_list[index_list[1]]
                )
                candidate_set = candidate_set.union(intersection_set)

        if len(candidate_set) == 1:
            return candidate_set.pop()
        else:
            return None

    @staticmethod
    def __valid_wxyz_cell(pivot_cell_candidates, cell_candidates):
        ''' Look for cells that have candidates and at least 1 number in common '''
        return len(cell_candidates) >= 2 and \
            len(cell_candidates.intersection(pivot_cell_candidates)) >= 1
    #
    # __reduce_wxyz_wing methods
    ###### END

    ###### START
    # __reduce_multiple_lines methods
    #
    def __reduce_multiple_lines(self):
        technique = 'Multiple Lines'
        # Iterate through each block
        for cell_coordinates_list in self.__block_coords_iter():

            # Extract the current block coordinates
            block_row = cell_coordinates_list[0].block_row
            block_col = cell_coordinates_list[0].block_col

            # Generate list of numbers that can still be assigned to the
            # remaining cells in the row or column
            unassigned_nums = self.__find_unassigned_nums(cell_coordinates_list)

            # Look for rows/columns that share the unassigned number in pairs of rows
            for num in unassigned_nums:

                # Identify the rows in the current block that can
                # have the number eliminated from the candidates
                shared_rows = self.__find_shared_lines_by_row(num, block_row, block_col)
                if shared_rows:

                    # Remove the number from the cell's candidates
                    for row in shared_rows:
                        for col in xrange(3):
                            self.__clear_cell_candidate_and_set(
                                num,
                                block_row,
                                block_col,
                                row,
                                col,
                                technique,
                            )

                # Identify the columns in the current block that can
                # have the number eliminated from the candidates
                shared_cols = self.__find_shared_lines_by_col(num, block_row, block_col)
                if shared_cols:

                    # Remove the number from the cell's candidates
                    for col in shared_cols:
                        for row in xrange(3):
                            self.__clear_cell_candidate_and_set(
                                num,
                                block_row,
                                block_col,
                                row,
                                col,
                                technique,
                            )

    def __find_shared_lines_by_row(self, num, block_row, block_col):
        '''
        Identify the rows in the current block that can
        have the number eliminated from the candidates
        '''
        shared_rows = set()
        affected_blocks = set()

        # Iterate through the remaining columns except for the starting one
        for block_col_loop in [x for x in xrange(3) if x != block_col]:

            # Iterate through each cell in the block
            for row, col in double_iter(3):

                # Check the cell's candidates if num can be placed here.
                # If it can, track the row and block
                candidates = self.get_cell_candidates(block_row, block_col_loop, row, col)
                if num in candidates:
                    shared_rows.add(row)
                    affected_blocks.add(block_col_loop)

        # Criteria for the multiple lines technique is that there are 2 shared rows
        # across 2 blocks with the same number.
        if len(shared_rows) == 2 and len(affected_blocks) == 2:
            return shared_rows
        else:
            return set()

    def __find_shared_lines_by_col(self, num, block_row, block_col):
        '''
        Identify the columns in the current block that can
        have the number eliminated from the candidates
        '''
        shared_cols = set()
        affected_blocks = set()

        # Iterate through the remaining rows except for the starting one
        for block_row_loop in [x for x in xrange(3) if x != block_row]:

            # Iterate through each cell in the block
            for row, col in double_iter(3):

                # Check the cell's candidates if num can be placed here.
                # If it can, track the column and block
                candidates = self.get_cell_candidates(block_row_loop, block_col, row, col)
                if num in candidates:
                    shared_cols.add(col)
                    affected_blocks.add(block_row_loop)

        # Criteria for the multiple lines technique is that there are 2 shared columns
        # across 2 blocks with the same number.
        if len(shared_cols) == 2 and len(affected_blocks) == 2:
            return shared_cols
        else:
            return set()
    #
    # __reduce_multiple_lines methods
    ###### END

    ###### START
    # __check_valid methods
    #
    def __check_valid(self):
        # Check valid cells by row
        self.__check_valid_cells(self.__row_coords_iter, 'Rows')

        # Check valid cells by column
        self.__check_valid_cells(self.__column_coords_iter, 'Columns')

        # Check valid cells by block
        self.__check_valid_cells(self.__block_coords_iter, 'Blocks')

        # The previous method calls will raise Exceptions if the completed grid is invalid
        # so if it gets here, then the puzzle is valid and solved
        self.__set_solved_true()

    # Makes sure there are 9 unique elements in the iterator
    def __check_valid_cells(self, coord_iter, iter_type):

        # Iterate through each row/column/block in the sudoku grid
        for cell_coordinates_list in coord_iter():
            valid_nums = set()

            # Iterate through each cell's coordinates
            for cell_coords in cell_coordinates_list:
                num = self.get_cell_value(
                    cell_coords.block_row,
                    cell_coords.block_col,
                    cell_coords.row,
                    cell_coords.col,
                )
                valid_nums.add(num)

            if len(valid_nums) != 9:
                print self
                raise Exception(
                    'Completed puzzle is not a valid solution.  %s contain duplicate entries.  '
                    'Check the starting puzzle or code to remove bugs.' % (iter_type)
                )

    def __set_solved_true(self):
        self.__solved_status = True  # pylint: disable=attribute-defined-outside-init
    #
    # __check_valid methods
    ###### END

    ######### START
    # Private Iterator Methods
    # The following iterators are helpful for traversing the sudoku
    # grid's cells.  They yield the coordinates for the cells that
    # make up each of the grid's rows, columns, or blocks.

    # Iterator that yields lists, which contain the coordinates for every cell
    # that corresponds to a row in the sudoku grid.
    # For instance, for the following example grid:
    #
    # 123
    # 456
    # 789
    #
    # The iterator would yield the following 3 lists, where the contents of each
    # list are coordinate objects for each cell.
    # [1, 2, 3], [4, 5, 6], [7, 8, 9]
    def __row_coords_iter(self):
        for block_row, row in double_iter(3):
            row_coords = []
            for coords in self.__row_cell_coords_iter(block_row, row):
                row_coords.append(coords)
            yield row_coords

    @staticmethod
    def __row_cell_coords_iter(block_row, row):
        '''
        Iterator that yields coordinate objects found in the row specified with block_row, row
        '''
        for block_col, col in double_iter(3):
            yield SudokuCoordinates(block_row, block_col, row, col)

    # Iterator that yields lists, which contain the coordinates for every cell
    # that corresponds to a column in the sudoku grid.
    # For instance, for the following example grid:
    #
    # 123
    # 456
    # 789
    #
    # The iterator would yield the following 3 lists, where the contents of each
    # list are coordinate objects for each cell.
    # [1, 4, 7], [2, 5, 8], [3, 6, 9]
    def __column_coords_iter(self):
        for block_col, col in double_iter(3):
            col_coords = []
            for coords in self.__col_cell_coords_iter(block_col, col):
                col_coords.append(coords)
            yield col_coords

    @staticmethod
    def __col_cell_coords_iter(block_col, col):
        '''
        Iterator that yields coordinate objects found
        in the column specified with block_col, col
        '''
        for block_row, row in double_iter(3):
            yield SudokuCoordinates(block_row, block_col, row, col)

    # Iterator that yields lists, which contain the coordinates for every cell
    # that corresponds to a block in the sudoku grid.
    # For instance, for the following example grid:
    #
    # 12 34
    # 56 78
    #
    # 90 *@
    # $% ^&
    #
    # The iterator would yield the following 4 lists, where the contents of each
    # list are coordinate objects for each cell.
    # [1, 2, 5, 6], [3, 4, 7, 8], [9, 0, $, %], [*, @, ^, &]
    def __block_coords_iter(self):
        for block_row, block_col in double_iter(3):
            block_coords = []
            for coords in self.__block_cell_coords_iter(block_row, block_col):
                block_coords.append(coords)
            yield block_coords

    @staticmethod
    def __block_cell_coords_iter(block_row, block_col):
        '''
        Iterator that yields coordinate objects found in
        the block specified with block_row, block_col
        '''
        for row, col in double_iter(3):
            yield SudokuCoordinates(block_row, block_col, row, col)
    #
    # Private Iterator Methods
    ######### END


class DictCounter(object):
    ''' Special counter for dictionary elements '''

    def __init__(self):
        self.__counts = {}

    def counts_ge(self, size):
        '''
        Determines if all keys in the dictionary are greater than or equal to size

        :param size:  Integer

        :return:  Boolean
        '''
        status = True
        for key in self.__counts:
            if self.__counts[key] < size:
                status = False
                break
        return status

    def add(self, key):
        '''
        Increases the counter for key by 1

        :param key:  String - A dictionary key

        :return:  None
        '''
        try:
            self.__counts[key] += 1
        except KeyError:
            self.__counts[key] = 1

    def key_count(self):
        '''
        Returns the total number of keys in the dictionary

        :param:  None

        :return:  Integer - The number of elements in the dictionary
        '''
        return len(self.__counts)
