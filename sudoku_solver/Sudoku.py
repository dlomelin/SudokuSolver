'''.'''

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
        return self.gridValues() == other.gridValues()

    def __str__(self):
        rowDelimeter = self.__rowDelimeter()

        # Gets the currently assigned values to the sudoku grid
        values = self.gridValues()

        # Create a header and center it
        if self.__puzzleSolved():
            status = 'Solution'
        else:
            status = 'Incomplete'
        status = status.center(len(rowDelimeter))

        string = '%s\n' % (status)
        for row in xrange(len(values)):
            # Every 3rd block gets a delimeter
            if row % 3 == 0:
                string += '%s\n' % (rowDelimeter)

            # Iterate through each number
            for col in xrange(len(values[row])):
                # Every 3rd number gets a column delimeter
                if col % 3 == 0:
                    string += '| '

                string += '%s ' % (values[row][col])

            string += '|\n'
        string += '%s\n' % (rowDelimeter)

        return string

    ##################
    # Public Methods #
    ##################

    def gridValues(self):
        '''
        Returns a list of lists with the current grid values.
        Unknown positions are represented by a period.

        :param:  None

        :return:  List of Lists
        '''
        values = []

        for matRow, row in double_iter(3):
            values.append([])
            for matCol, col in double_iter(3):
                num = self.getCellValue(matRow, matCol, row, col)
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
            self.__setChangeFalse()

            # Assign values to a row or column where only a single value is possible
            self.__setSingletons()

            # Reduce numbers based on lone hint pairs lying along the same row or column
            # within 1 block.  Removes the number along the same row or column but in
            # neighboring blocks.
            self.__reduceCandidateLines()

            # Reduce numbers based on using the xwing, swordfish, and jellyfish techniques
            self.__reduceXwingSwordfishJellyfish()

            # Reduce numbers based on naked pairs/trios
            self.__reduceNakedSets()

            # Reduce numbers based on using the Ywing method
            self.__reduceYwing()

            # Reduce numbers based on using the XYZwing method
            self.__reduceXYZwing()

            # Reduce numbers based on using the WXYZwing method
            self.__reduceWXYZwing()

            # Reduce numbers based on multiple lines
            self.__reduce_multiple_lines()

            if not self.__puzzleChanged():
                break

        # If puzzle was complete, make sure the blocks, rows, and columns
        # all adhere to a valid sudoku solution.
        if self.complete():
            self.__checkValid()

    def complete(self):
        '''
        Checks if every cell has been filled in with a number.
        Does not check if the numbers are valid though.

        :param:  None

        :return:  Boolean
        '''

        allComplete = True

        # Iterate through each of the 9 blocks
        for block_row, block_col in double_iter(3):
            # Check if the block is complete
            if not self.__completeBlock(block_row, block_col):
                allComplete = False
                break

        return allComplete

    def printCandidates(self, fhOut=sys.stdout):
        '''
        Prints the current candidates used to solve the puzzle in a human readable format

        :param fhOut:  Filehandle - Optional

        :return:  None
        '''
        candidateNums = [['1', '2', '3'], ['4', '5', '6'], ['7', '8', '9']]

        header = 'Current Candidates'.center(len(self.__blockRowSplit()))

        fhOut.write('%s\n' % (header))
        for block_row in xrange(3):
            if block_row == 0:
                fhOut.write('%s\n' % (self.__blockRowSplit()))
            for row in xrange(3):
                for i in xrange(len(candidateNums)):
                    fhOut.write('||')
                    for block_col in xrange(3):
                        for col in xrange(3):
                            num_string = ''
                            candidates = self.get_cell_candidates(block_row, block_col, row, col)
                            for num in candidateNums[i]:
                                if num in candidates:
                                    num_string += '%s' % (num)
                                else:
                                    num_string += ' '
                            if col == 2:
                                col_split = '||'
                            else:
                                col_split = '|'
                            fhOut.write(' %s %s' % (num_string, col_split))
                    fhOut.write('\n')
                if row == 2:
                    fhOut.write('%s\n' % (self.__blockRowSplit()))
                else:
                    fhOut.write('%s\n' % (self.__rowSplit()))

    def printTechniquesUsed(self, fhOut=sys.stdout):
        '''
        Prints out a list of techniques used and how frequently they were used

        :param fhOut:  Filehandle - Optional

        :return:  None
        '''

        fhOut.write('Candidates Removed By:\n')
        for technique in sorted(self.__techniques_used):
            fhOut.write('  %s: %s\n' % (technique, self.__techniques_used[technique]))
        fhOut.write('\n')

    def getCellValue(self, block_row, block_col, row, col):
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
    def __puzzleChanged(self):
        return self.__change_status

    # Lets the solver know changes were made
    def __setChangeTrue(self, techniqueUsed):
        self.__change_status = True
        self.__track_techniques_used(techniqueUsed)

    def __setChangeFalse(self):
        self.__change_status = False

    def __puzzleSolved(self):
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
    def __deleteCandidateNumber(self, num, block_row, block_col, row, col):
        self.__matrix[block_row][block_col].delete_candidate_number(num, row, col)

    # Sets the value of the specified cell
    def __setCellValue(self, num, block_row, block_col, row, col):
        self.__matrix[block_row][block_col].set_value(num, row, col)

    # Clears out available candidates from the specified cell
    def __clearCellCandidates(self, block_row, block_col, row, col):
        self.__matrix[block_row][block_col].clear_candidates(row, col)

    def __validBlock(self, block_row, block_col):
        return self.__matrix[block_row][block_col].valid()

    def __completeBlock(self, block_row, block_col):
        return self.__matrix[block_row][block_col].complete()
    #
    # Wrappers around SudokuBlock methods
    ###### END

    ###### START
    # Shared methods
    #
    # Sets the value of the specified cell and adjusts the candidates in the
    # necessary row, column, and block.
    def __setValue(self, num, block_row, block_col, row, col, techniqueUsed=None):
        # Sets the value of the specified cell
        self.__setCellValue(num, block_row, block_col, row, col)

        # Clears out available candidates from the specified cell
        self.__clearCellCandidates(block_row, block_col, row, col)

        # Clears out available candidates from the affected block, row, and column
        self.__removeCandidateSeenBy(num, block_row, block_col, row, col)

        # Let the solver know changes were made
        self.__setChangeTrue(techniqueUsed)

    # Deletes the specified number from the cell's candidates.  If there is only
    # one number left in the candidates, then it sets the value
    def __clearCellCandidateAndSet(self, num, block_row, block_col, row, col, techniqueUsed):

        candidates = self.get_cell_candidates(block_row, block_col, row, col)
        if num in candidates:
            self.__deleteCandidateNumber(num, block_row, block_col, row, col)

            nums = list(candidates)
            if len(nums) == 1:
                self.__setValue(
                    nums[0],
                    block_row,
                    block_col,
                    row,
                    col,
                    techniqueUsed,
                )
            else:
                # Let the solver know changes were made
                self.__setChangeTrue(techniqueUsed)

    # Iterate through each cell, determine which numbers have already been
    # assigned, and remove them from the list of unassigned numbers
    def __findUnassignedNums(self, cell_coordinates_list):
        # Create a list of all possible numbers that can be assigned to the current set of cells
        unassignedNums = number_set(3)

        # Iterate through each cell's coordinates
        for cellCoords in cell_coordinates_list:

            # Remove the already assigned number in the current cell
            # from the list of possible numbers
            num = self.getCellValue(
                cellCoords.block_row,
                cellCoords.block_col,
                cellCoords.row,
                cellCoords.col,
            )
            if num:
                unassignedNums.discard(num)

        return unassignedNums

    # Clears out available candidates from the affected block, row, and column
    def __removeCandidateSeenBy(self, num, block_row, block_col, row, col):

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
            self.__rowCellCoordsIter,
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

    def __remove_candidate_by_iter(
            self,
            num,
            coord_iter,
            coordPos1,
            coordPos2,
            skipCoordsList,
            technique=None):
        '''
        Goes through each cell passed from the iterator and removes
        the number from the cell's candidates
        '''
        # Iterate through each cell
        for coords in coord_iter(coordPos1, coordPos2):

            # Skip the cells that are the skip list
            if not self.__coordsInList(coords, skipCoordsList):
                # Remove the numbers from the cell candidates
                self.__clearCellCandidateAndSet(
                    num,
                    coords.block_row,
                    coords.block_col,
                    coords.row,
                    coords.col,
                    technique,
                )

    @staticmethod
    def __coordsInList(coords, skip_list):
        item_in_list = False
        for item in skip_list:
            if item == coords:
                item_in_list = True
                break
        return item_in_list

    def __coordsIntersection(self, *coordsList):
        seenCoordsList = []
        for coords in coordsList:
            sharedCoords = self.__coordsSeenBy(coords)
            seenCoordsList.append(sharedCoords)

        intersectingCoords = seenCoordsList[0]
        for i in xrange(1, len(seenCoordsList)):
            intersectingCoords = intersectingCoords.intersection(seenCoordsList[i])

        return intersectingCoords

    def __coordsSeenBy(self, centerCoord):
        '''
        Returns a set of all coordinates that are in the same
        block, row, and column as the input coordinates
        '''
        uniqueCoords = set()

        # Store all coordinates in the same block as centerCoord
        for coord in self.__block_cell_coords_iter(centerCoord.block_row, centerCoord.block_col):
            uniqueCoords.add(coord)

        # Store all coordinates in the same row as centerCoord
        for coord in self.__rowCellCoordsIter(centerCoord.block_row, centerCoord.row):
            uniqueCoords.add(coord)

        # Store all coordinates in the same column as centerCoord
        for coord in self.__col_cell_coords_iter(centerCoord.block_col, centerCoord.col):
            uniqueCoords.add(coord)

        # Remove centerCoord
        uniqueCoords.discard(centerCoord)

        return uniqueCoords

    def __validCellsSeenBy(self, coords, pivotCellCandidates, validCellFunction):
        coordsList = []
        candidatesList = []

        # Iterate across all cells that are seen by the current cell
        for cellCoords in self.__coordsSeenBy(coords):

            # Look for cells that pass the criteria set forth by validCellFunction
            cellCandidates = self.get_cell_candidates(
                cellCoords.block_row,
                cellCoords.block_col,
                cellCoords.row,
                cellCoords.col,
            )
            if validCellFunction(pivotCellCandidates, cellCandidates):
                coordsList.append(cellCoords)
                candidatesList.append(cellCandidates)

        return coordsList, candidatesList

    @staticmethod
    def __candidatesIntersection(*candidatesList):
        candidatesIntersection = candidatesList[0]
        for i in xrange(1, len(candidatesList)):
            candidatesIntersection = candidatesIntersection.intersection(candidatesList[i])

        return candidatesIntersection

    @staticmethod
    def __candidatesUnion(*candidatesList):
        candidatesUnion = candidatesList[0]
        for i in xrange(1, len(candidatesList)):
            candidatesUnion = candidatesUnion.union(candidatesList[i])

        return candidatesUnion
    #
    # Shared methods
    ###### END

    ###### START
    # __init__ methods
    #
    @staticmethod
    def __check_input_arguments(fields_to_check, args):
        # Check if one of the required arguments was supplied
        missingFields = True
        for field in args:
            if field in fields_to_check:
                missingFields = False

        if missingFields:
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

    def __load_from_file(self, fileName):
        ''' Loads data from a file '''
        if os.path.isfile(fileName):
            data = []

            # Converts file contents into a list of lists
            fhIn = open(fileName, 'rU')
            for line in fhIn:
                nums = self.__parseFileLine(line)
                data.append(nums)
            fhIn.close()

            # Loads data from a list of lists
            self.__load_from_data(data)

        else:
            raise Exception('%s is not a valid file or does not exist.' % (fileName))

    # Loads data from a list of lists
    def __load_from_data(self, data):
        temp_matrix = instantiate_matrix(3)
        currentBlockRow = 0

        for nums in data:
            # Every 3 lines get incremented
            if self.__currentBlockRowFull(temp_matrix, currentBlockRow):
                currentBlockRow += 1

            temp_matrix[currentBlockRow][0].append(nums[0:3])
            temp_matrix[currentBlockRow][1].append(nums[3:6])
            temp_matrix[currentBlockRow][2].append(nums[6:9])

        self.__instantiateSudokuMatrix(temp_matrix)

    @staticmethod
    def __parseFileLine(line):
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
    def __currentBlockRowFull(matrix, block_row):
        ''' Returns True if the current row of blocks are all full '''
        return len(matrix[block_row][0]) == 3 and \
            len(matrix[block_row][1]) == 3 and \
            len(matrix[block_row][2]) == 3

    # Converts the temporary matrix into one that has SudokuBlock objects
    def __instantiateSudokuMatrix(self, temp_matrix):
        self.__matrix = instantiate_matrix(3)
        # Iterate through each of the 9 blocks
        for block_row, block_col in double_iter(3):
            self.__matrix[block_row][block_col] = SudokuBlock(temp_matrix[block_row][block_col])

        # Adjusts the candidates based on the initial values of the sudoku grid.
        self.__clearInitialCandidates()

    # Adjusts the candidates based on the initial values of the sudoku grid.
    def __clearInitialCandidates(self):

        # Iterate through each block in the sudoku grid
        for cell_coordinates_list in self.__block_coords_iter():

            # Iterate through each cell's coordinates
            for cellCoords in cell_coordinates_list:

                # If the cell has a number assigned then clear the block, row, and column candidates
                num = self.getCellValue(
                    cellCoords.block_row,
                    cellCoords.block_col,
                    cellCoords.row,
                    cellCoords.col,
                )
                if num:
                    # Clears out available candidates from the affected block, row, and column
                    self.__removeCandidateSeenBy(
                        num,
                        cellCoords.block_row,
                        cellCoords.block_col,
                        cellCoords.row,
                        cellCoords.col,
                    )
    #
    # __init__ methods
    ###### END

    ###### START
    # __str__ methods
    #
    @staticmethod
    def __rowDelimeter():
        return '-------------------------'
    #
    # __str__ methods
    ###### END

    ###### START
    # printCandidates methods
    #
    @staticmethod
    def __rowSplit():
        return '-----------------------------------------------------------'

    @staticmethod
    def __blockRowSplit():
        return '==========================================================='
    #
    # printCandidates methods
    ###### END

    ###### START
    # __setSingletons methods
    #
    def __setSingletons(self):
        # Assign singletons within rows
        self.__setSingletonCandidates(self.__row_coords_iter)

        # Assign singletons within columns
        self.__setSingletonCandidates(self.__column_coords_iter)

    def __setSingletonCandidates(self, coord_iter):

        # Iterate through each line in the sudoku grid
        # The lines will be all rows or all columns, depending on what was passed
        # to this method in coord_iter
        for cell_coordinates_list in coord_iter():

            # Generate list of numbers that can still be assigned to the
            # remaining cells in the row or column
            unassignedNums = self.__findUnassignedNums(cell_coordinates_list)

            # Iterate through the set of unassigned numbers
            for currentValue in unassignedNums:

                availableCellCount = 0
                availableCellCoords = None

                # Iterate through each cell's coordinates
                for cellCoords in cell_coordinates_list:

                    # If that position was already assigned a number then skip it
                    if not self.getCellValue(
                            cellCoords.block_row,
                            cellCoords.block_col,
                            cellCoords.row,
                            cellCoords.col):
                        # Grab the set() of available values for the current cell
                        candidates = self.get_cell_candidates(
                            cellCoords.block_row,
                            cellCoords.block_col,
                            cellCoords.row,
                            cellCoords.col,
                        )
                        # Keep track of how many positions will allow the current value
                        if currentValue in candidates:
                            availableCellCount += 1
                            availableCellCoords = cellCoords

                            # Once the available cell count is greater than 1, there is no point
                            # in going forward because we need singletons
                            if availableCellCount > 1:
                                break

                # Assuming there is only 1 cell that can accept the current value
                # then set that cell's value
                if availableCellCount == 1:
                    self.__setValue(
                        currentValue,
                        availableCellCoords.block_row,
                        availableCellCoords.block_col,
                        availableCellCoords.row,
                        availableCellCoords.col,
                    )
    #
    # __setSingletons methods
    ###### END

    ###### START
    # __reduceCandidateLines methods
    #
    # Reduce numbers based on lone hint pairs lying along the same row or column within 1 block.
    # Removes the number along the same row or column but in neighboring blocks.
    def __reduceCandidateLines(self):
        technique = 'Candidate Lines'

        # Iterate through all sudoku grid blocks
        for cell_coordinates_list in self.__block_coords_iter():
            # Create a list of all unassigned numbers and the coordinates where they are found
            hintCoords = self.__generate_hint_coords(cell_coordinates_list)

            # Iterate through each unassigned number
            for num in hintCoords:

                # Candidate lines method works by aligning
                if len(hintCoords[num]) == 2:

                    # Store variables just to make code more readable
                    coords1 = hintCoords[num][0]
                    coords2 = hintCoords[num][1]

                    # Candidate line lies along a row, therefore
                    # remove number from the rest of the row
                    if coords1.aligns_by_row(coords2):
                        # Remove the number from the candidates along the row
                        self.__remove_candidate_by_iter(
                            num,
                            self.__rowCellCoordsIter,
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
        hintCoords = num_dict_list(3)

        # Iterate through each cell's coordinates
        for cellCoords in cell_coordinates_list:
            # Store the coordinates where all numbers are found
            candidates = self.get_cell_candidates(
                cellCoords.block_row,
                cellCoords.block_col,
                cellCoords.row,
                cellCoords.col,
            )
            for num in candidates:
                hintCoords[num].append(cellCoords)

        return hintCoords
    #
    # __reduceCandidateLines methods
    ###### END

    ###### START
    # __reduceXwingSwordfishJellyfish methods
    #
    def __reduceXwingSwordfishJellyfish(self):

        # 2 = Xwing  3 = Swordfish  4 = Jellyfish
        for cell_count in xrange(2, 5):
            # Search for valid xwing cells along rows to reduce candidates along the columns
            self.__reduceXwingSwordJellyRow(cell_count)

            # Search for valid xwing cells along columns to reduce candidates along the rows
            self.__reduceXwingSwordJellyCol(cell_count)

    def __reduceXwingSwordJellyRow(self, cell_count):
        technique = self.__x_sword_jelly_technique(cell_count)
        potentialCells = self.__potential_rectangle_cells(cell_count, self.__row_coords_iter)

        # Iterate through each number
        for num in potentialCells:

            # Iterate through all possible row triplets
            for dataset in combinations(potentialCells[num], cell_count):

                # Checks if the current triplet of rows forms a valid Swordfish across 3 columns
                if self.__validRectangleColCells(cell_count, *dataset):

                    # Iterate through the 3 affected columns
                    for block_coords in self.__columnsInCommon(*dataset):

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

    def __reduceXwingSwordJellyCol(self, cell_count):
        technique = self.__x_sword_jelly_technique(cell_count)

        potentialCells = self.__potential_rectangle_cells(cell_count, self.__column_coords_iter)

        # Iterate through each number
        for num in potentialCells:

            # Iterate through all possible cell_count cells
            for dataset in combinations(potentialCells[num], cell_count):

                # Checks if the current triplet of rows forms a valid Swordfish across 3 rows
                if self.__validRectangleRowCells(cell_count, *dataset):

                    # Iterate through the 3 affected rows
                    for block_coords in self.__rowsInCommon(*dataset):

                        # Remove the number from the candidates along the row, excluding the cells
                        # that make up the Swordfish
                        self.__remove_candidate_by_iter(
                            num,
                            self.__rowCellCoordsIter,
                            block_coords.block_row,
                            block_coords.row,
                            list(chain(*dataset)),
                            technique,
                        )

    @staticmethod
    def __validRectangleRowCells(cell_count, *dataList):

        row_data = DictCounter()
        complete_data_lists = True

        for data in dataList:
            if not data:
                complete_data_lists = False
            for coords in data:
                row = '%s,%s' % (coords.block_row, coords.row)
                row_data.add(row)

        return row_data.key_count() == cell_count and row_data.counts_ge(2) and complete_data_lists

    @staticmethod
    def __validRectangleColCells(cell_count, *dataList):

        col_data = DictCounter()
        complete_data_lists = True

        for data in dataList:
            if not data:
                complete_data_lists = False
            for coords in data:
                col = '%s,%s' % (coords.block_col, coords.col)
                col_data.add(col)

        return col_data.key_count() == cell_count and col_data.counts_ge(2) and complete_data_lists

    @staticmethod
    def __rowsInCommon(*dataList):
        rowSet = set()

        for data in dataList:
            for coords in data:
                rowSet.add(SudokuCoordinates(coords.block_row, 0, coords.row, 0))

        return rowSet

    @staticmethod
    def __columnsInCommon(*dataList):
        colSet = set()

        for data in dataList:
            for coords in data:
                colSet.add(SudokuCoordinates(0, coords.block_col, 0, coords.col))

        return colSet

    # Search all rows/columns for cells that have between 2 and cell_count candidates
    # cell_count is dependent on the technique.  This method is used in the xwing,
    # swordfish, jellyfish type puzzles
    def __potential_rectangle_cells(self, cell_count, coord_iter):

        potentialCells = num_dict_list(3)

        # Iterate through each row/cell in the sudoku grid
        for cell_coordinates_list in coord_iter():
            hintCoords = num_dict_list(3)

            # Iterate through each cell's coordinates
            for cellCoords in cell_coordinates_list:

                # Loop through all candidates in the current cell
                candidates = self.get_cell_candidates(
                    cellCoords.block_row,
                    cellCoords.block_col,
                    cellCoords.row,
                    cellCoords.col,
                )
                for num in candidates:
                    # Store the current coordinates
                    hintCoords[num].append(cellCoords)

            # Keep only the cells that have between 2 and cell_count candidates left in the row/col
            for num in hintCoords:
                if 2 <= len(hintCoords[num]) <= cell_count:
                    potentialCells[num].append(hintCoords[num])

        return potentialCells

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
    # __reduceXwingSwordfishJellyfish methods
    ###### END

    ###### START
    # __reduceNakedSets methods
    #
    def __reduceNakedSets(self):
        # Reduce naked sets by row
        self.__findNakedSets(self.__row_coords_iter)

        # Reduce naked sets by column
        self.__findNakedSets(self.__column_coords_iter)

        # Reduce naked sets by block
        self.__findNakedSets(self.__block_coords_iter)

    def __findNakedSets(self, coord_iter):

        # Iterate through each row/column/block in the sudoku grid
        for cell_coordinates_list in coord_iter():
            candidateCoords = []
            candidateList = []

            # Iterate through each cell's coordinates
            for cellCoords in cell_coordinates_list:

                # Store the cell's coordinates and candidates
                candidates = self.get_cell_candidates(
                    cellCoords.block_row,
                    cellCoords.block_col,
                    cellCoords.row,
                    cellCoords.col,
                )
                if candidates:
                    candidateCoords.append(cellCoords)
                    candidateList.append(candidates)

            # setSize determines the naked set size, 2=naked pairs, 3=naked trios, 4=naked quads
            for setSize in xrange(2, 5):

                # Looks for naked sets in the current set of cells
                self.__findNakedSetCombinations(
                    setSize,
                    candidateList,
                    candidateCoords,
                    cell_coordinates_list,
                )

    # Finds all valid naked sets.  If any are found, remove the numbers that are found in the naked
    # sets from all remaining neighboring cells.
    def __findNakedSetCombinations(
            self,
            setSize,
            candidateList,
            candidateCoords,
            cell_coordinates_list):
        technique = self.__nakedSetTechnique(setSize)

        # Generates a list with all combinations of size setSize.
        # If candidateList = [0, 1, 2] and setSize = 2, then 3 indexLists would be created
        # [0, 1], [0, 2], [1, 2]
        for indexList in combinations(xrange(len(candidateList)), setSize):

            # Generate a set of the unique candidates in candidateList
            uniqueCandidates = self.__combineCandidates(candidateList, indexList)

            # Valid naked sets have been found when the number of unique numbers == the set size.
            # If 2 unique numbers are found in 2 cells, then you can remove those 2 numbers from
            # the remaining cells.  Same criteria applies if you find 3 unique numbers in 3 cells,
            # 4 unique numbers in 4 cells.
            if len(uniqueCandidates) == setSize:

                # Store the coordinates of the cells that made up the naked sets.
                skipCoordsList = []
                for i in indexList:
                    skipCoordsList.append(candidateCoords[i])

                # Iterate through each number in the naked set
                for num in uniqueCandidates:

                    # Iterate through each cell in the current row/column/block
                    for coords in cell_coordinates_list:

                        # Skip the cells that are in the skip list
                        # (cells that made up the naked set)
                        if not self.__coordsInList(coords, skipCoordsList):

                            # Remove the numbers from the cell candidates
                            self.__clearCellCandidateAndSet(
                                num,
                                coords.block_row,
                                coords.block_col,
                                coords.row,
                                coords.col,
                                technique,
                            )

    @staticmethod
    def __combineCandidates(setList, coords):
        ''' Generate a set of the unique candidates in candidateList '''
        uniqueCandidates = set()
        for indexNum in coords:
            for num in list(setList[indexNum]):
                uniqueCandidates.add(num)
        return uniqueCandidates

    @staticmethod
    def __nakedSetTechnique(setSize):
        ''' Returns the technique name for a given setSize '''
        techniques = {
            2: 'Naked Pairs',
            3: 'Naked Trios',
            4: 'Naked Quads',
        }
        try:
            return techniques[setSize]
        except:
            raise Exception('Invalid naked set size used: %s.  Please modify code' % (setSize))
    #
    # __reduceNakedSets methods
    ###### END

    ###### START
    # __reduceYwing methods
    #
    def __reduceYwing(self):

        # Iterate through each row in the sudoku grid
        for cell_coordinates_list in self.__row_coords_iter():

            # Iterate through each cell's coordinates
            for cellCoords in cell_coordinates_list:

                # Perform Y wing technique
                self.__findPotentialYwing(cellCoords)

    # Performs the Y wing technique
    def __findPotentialYwing(self, coords):
        technique = 'Y-Wing'

        # Look for a pivot cell that has 2 unknown candidates
        pivotCellCandidates = self.get_cell_candidates(
            coords.block_row,
            coords.block_col,
            coords.row,
            coords.col,
        )

        # Y wing requires the pivot cell to contain exactly 2 candidates
        if len(pivotCellCandidates) == 2:

            # Get a list of coordinates and candidates seen by the current cell
            coordsList, candidatesList = self.__validCellsSeenBy(
                coords,
                pivotCellCandidates,
                self.__validYCell,
            )

            # Iterate through all pairs of cells
            for indexList in combinations(xrange(len(coordsList)), 2):

                # Create a set of common of candidate numbers from the pair of cells.
                # If there is only 1 candidate number and its not found in the pivot cell
                # then remove that number from the overlapping cells that can see one
                # another between the current pairs of cells.
                commonSet = candidatesList[indexList[0]].intersection(candidatesList[indexList[1]])
                if len(commonSet) == 1:
                    removeNum = commonSet.pop()
                    if not removeNum in pivotCellCandidates:
                        removeCoords = self.__coordsIntersection(
                            coordsList[indexList[0]],
                            coordsList[indexList[1]],
                        )

                        for rCoords in removeCoords:
                            self.__clearCellCandidateAndSet(
                                removeNum,
                                rCoords.block_row,
                                rCoords.block_col,
                                rCoords.row,
                                rCoords.col,
                                technique,
                            )

    @staticmethod
    def __validYCell(pivotCellCandidates, cellCandidates):
        '''
        Looks for a cell that has 2 candidate numbers and shares
        exactly 1 candidate between itself and the pivot cell
        '''
        return len(cellCandidates) == 2 and \
            len(cellCandidates.intersection(pivotCellCandidates)) == 1
    #
    # __reduceYwing methods
    ###### END

    ###### START
    # __reduceXYZwing methods
    #
    def __reduceXYZwing(self):

        # Iterate through each row in the sudoku grid
        for cell_coordinates_list in self.__row_coords_iter():

            # Iterate through each cell's coordinates
            for cellCoords in cell_coordinates_list:

                # Perform XYZ wing technique
                self.__findPotentialXYZwing(cellCoords)

    def __findPotentialXYZwing(self, coords):
        technique = 'XYZ-Wing'

        # Look for a pivot point that has 3 unknown candidates
        pivotCellCandidates = self.get_cell_candidates(
            coords.block_row,
            coords.block_col,
            coords.row,
            coords.col,
        )

        # XYZ wing requires the pivot cell to contain exactly 3 candidates
        if len(pivotCellCandidates) == 3:

            # Get a list of coordinates and candidates seen by the current cell
            coordsList, candidatesList = self.__validCellsSeenBy(
                coords,
                pivotCellCandidates,
                self.__validXYZCell,
            )

            # Iterate through all pairs of cells
            for indexList in combinations(xrange(len(coordsList)), 2):

                # Union between each pair
                candidatesUnion = self.__candidatesUnion(
                    candidatesList[indexList[0]],
                    candidatesList[indexList[1]],
                )

                if len(candidatesUnion) == 3:
                    commonSet = self.__candidatesIntersection(
                        candidatesList[indexList[0]],
                        candidatesList[indexList[1]],
                    )
                    removeNum = commonSet.pop()

                    removeCoords = self.__coordsIntersection(
                        coords,
                        coordsList[indexList[0]],
                        coordsList[indexList[1]],
                    )

                    for rCoords in removeCoords:
                        self.__clearCellCandidateAndSet(
                            removeNum,
                            rCoords.block_row,
                            rCoords.block_col,
                            rCoords.row,
                            rCoords.col,
                            technique,
                        )

    @staticmethod
    def __validXYZCell(pivotCellCandidates, cellCandidates):
        '''
        Look for cells that have 2 unknown candidates that are all found
        within the pivot cell
        '''
        return len(cellCandidates) == 2 and cellCandidates.issubset(pivotCellCandidates)
    #
    # __reduceXYZwing methods
    ###### END

    ###### START
    # __reduceWXYZwing methods
    #
    def __reduceWXYZwing(self):

        # Iterate through each row in the sudoku grid
        for cell_coordinates_list in self.__row_coords_iter():

            # Iterate through each cell's coordinates
            for cellCoords in cell_coordinates_list:

                # Perform WXYZ wing technique
                self.__findPotentialWXYZwing(cellCoords)

    def __findPotentialWXYZwing(self, coords):
        technique = 'WXYZ-Wing'

        pivotCellCandidates = self.get_cell_candidates(
            coords.block_row,
            coords.block_col,
            coords.row,
            coords.col,
        )

        # Get a list of coordinates and candidates seen by the current cell
        coordsList, candidatesList = self.__validCellsSeenBy(
            coords,
            pivotCellCandidates,
            self.__validWXYZCell,
        )

        # Iterate through all pairs of cells
        for indexList in combinations(xrange(len(coordsList)), 3):

            candidatesUnion = self.__candidatesUnion(
                pivotCellCandidates,
                candidatesList[indexList[0]],
                candidatesList[indexList[1]],
                candidatesList[indexList[2]],
            )

            if len(candidatesUnion) == 4:
                removeNum = self.__findNonRestrictedCandidate(
                    [
                        candidatesList[indexList[0]],
                        candidatesList[indexList[1]],
                        candidatesList[indexList[2]],
                    ],
                    [
                        coordsList[indexList[0]],
                        coordsList[indexList[1]],
                        coordsList[indexList[2]],
                    ],
                )

                if not removeNum is None:

                    coordsForIntersection = []
                    if removeNum in pivotCellCandidates:
                        coordsForIntersection.append(coords)
                    for i in xrange(3):
                        if removeNum in candidatesList[indexList[i]]:
                            coordsForIntersection.append(coordsList[indexList[i]])

                    removeCoords = self.__coordsIntersection(*coordsForIntersection)

                    for rCoords in removeCoords:
                        self.__clearCellCandidateAndSet(
                            removeNum,
                            rCoords.block_row,
                            rCoords.block_col,
                            rCoords.row,
                            rCoords.col,
                            technique,
                        )

    @staticmethod
    def __findNonRestrictedCandidate(candidatesList, coordsList):
        candidateSet = set()

        # Iterate through each pair of cells
        for indexList in combinations(xrange(len(coordsList)), 2):

            # Look for cells that can't see each other
            if not coordsList[indexList[0]].aligns_by_row(coordsList[indexList[1]]) and \
                not coordsList[indexList[0]].aligns_by_col(coordsList[indexList[1]]) and \
                not coordsList[indexList[0]].aligns_by_block(coordsList[indexList[1]]):

                # Look for the numbers shared in common between both cells
                intersectionSet = candidatesList[indexList[0]].intersection(
                    candidatesList[indexList[1]]
                )
                candidateSet = candidateSet.union(intersectionSet)

        if len(candidateSet) == 1:
            return candidateSet.pop()
        else:
            return None

    @staticmethod
    def __validWXYZCell(pivotCellCandidates, cellCandidates):
        ''' Look for cells that have candidates and at least 1 number in common '''
        return len(cellCandidates) >= 2 and \
            len(cellCandidates.intersection(pivotCellCandidates)) >= 1
    #
    # __reduceWXYZwing methods
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
            unassignedNums = self.__findUnassignedNums(cell_coordinates_list)

            # Look for rows/columns that share the unassigned number in pairs of rows
            for num in unassignedNums:

                # Identify the rows in the current block that can
                # have the number eliminated from the candidates
                sharedRows = self.__find_shared_lines_by_row(num, block_row, block_col)
                if sharedRows:

                    # Remove the number from the cell's candidates
                    for row in sharedRows:
                        for col in xrange(3):
                            self.__clearCellCandidateAndSet(
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
                            self.__clearCellCandidateAndSet(
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
        sharedRows = set()
        affected_blocks = set()

        # Iterate through the remaining columns except for the starting one
        for blockColLoop in [x for x in xrange(3) if x != block_col]:

            # Iterate through each cell in the block
            for row, col in double_iter(3):

                # Check the cell's candidates if num can be placed here.
                # If it can, track the row and block
                candidates = self.get_cell_candidates(block_row, blockColLoop, row, col)
                if num in candidates:
                    sharedRows.add(row)
                    affected_blocks.add(blockColLoop)

        # Criteria for the multiple lines technique is that there are 2 shared rows
        # across 2 blocks with the same number.
        if len(sharedRows) == 2 and len(affected_blocks) == 2:
            return sharedRows
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
        for blockRowLoop in [x for x in xrange(3) if x != block_row]:

            # Iterate through each cell in the block
            for row, col in double_iter(3):

                # Check the cell's candidates if num can be placed here.
                # If it can, track the column and block
                candidates = self.get_cell_candidates(blockRowLoop, block_col, row, col)
                if num in candidates:
                    shared_cols.add(col)
                    affected_blocks.add(blockRowLoop)

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
    # __checkValid methods
    #
    def __checkValid(self):
        # Check valid cells by row
        self.__checkValidCells(self.__row_coords_iter, 'Rows')

        # Check valid cells by column
        self.__checkValidCells(self.__column_coords_iter, 'Columns')

        # Check valid cells by block
        self.__checkValidCells(self.__block_coords_iter, 'Blocks')

        # The previous method calls will raise Exceptions if the completed grid is invalid
        # so if it gets here, then the puzzle is valid and solved
        self.__setSolvedTrue()

    # Makes sure there are 9 unique elements in the iterator
    def __checkValidCells(self, coord_iter, iterType):

        # Iterate through each row/column/block in the sudoku grid
        for cell_coordinates_list in coord_iter():
            validNums = set()

            # Iterate through each cell's coordinates
            for cellCoords in cell_coordinates_list:
                num = self.getCellValue(
                    cellCoords.block_row,
                    cellCoords.block_col,
                    cellCoords.row,
                    cellCoords.col,
                )
                validNums.add(num)

            if len(validNums) != 9:
                print self
                raise Exception(
                    'Completed puzzle is not a valid solution.  %s contain duplicate entries.  '
                    'Check the starting puzzle or code to remove bugs.' % (iterType)
                )

    def __setSolvedTrue(self):
        self.__solved_status = True
    #
    # __checkValid methods
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
            rowCoords = []
            for coords in self.__rowCellCoordsIter(block_row, row):
                rowCoords.append(coords)
            yield rowCoords

    @staticmethod
    def __rowCellCoordsIter(block_row, row):
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
