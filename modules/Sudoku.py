import os, sys
from itertools import combinations

from SudokuSolver.modules.utilities import instantiateMatrix, doubleIter, numberSet, numDictList, pairwiseIter
from SudokuSolver.modules.SudokuBlock import SudokuBlock
from SudokuSolver.modules.SudokuCoordinates import SudokuCoordinates

class Sudoku(object):
	def __init__(self, **args):

		# Make sure one of the required arguments was passed in
		fieldsToCheck = set(['file', 'data'])
		self.__checkInputParameters(fieldsToCheck, args)

		# Loads the user specified data
		self.__loadInputData(args)

		# Mark this puzzle as unsolved
		self.__setSolvedFalse()

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
		for row in range(len(values)):
			# Every 3rd block gets a delimeter
			if row % 3 == 0:
				string += '%s\n' % (rowDelimeter)

			# Iterate through each number
			for col in range(len(values[row])):
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

	# Returns a list of lists with the current grid values.
	# Unknown positions are represented by a period.
	def gridValues(self):
		values = []

		for matRow, row in doubleIter(3):
			values.append([])
			for matCol, col in doubleIter(3):
				num = self.getCellValue(matRow, matCol, row, col)
				if not num:
					num = '.'

				values[-1].append(num)

		return values

	# Attempts to figure out the values for all cells in the sudoku grid.
	def solve(self):
		# Mark this puzzle as unsolved
		self.__setSolvedFalse()

		while True:
			# Mark this iteration as having no changes
			# Any modifications to the puzzle will mark the puzzle as changed
			# otherwise the loop will quit
			self.__setChangeFalse()

			# Assign values to a row or column where only a single value is possible
			self.__setSingletons()

			# Reduce numbers based on lone hint pairs lying along the same row or column within 1 block.
			# Removes the number along the same row or column but in neighboring blocks.
			self.__reduceCandidateLines()

			# Reduce numbers based on using the xwing method
			self.__reduceXwing()

			# Reduce numbers based on naked pairs/trios
			self.__reduceNakedSets()

			# Reduce numbers based on using the XYwing method
			self.__reduceXYwing()

			# Reduce numbers based on multiple lines
			self.__reduceMultipleLines()

			if not self.__puzzleChanged():
				break

		# If puzzle was complete, make sure the blocks, rows, and columns
		# all adhere to a valid sudoku solution.
		if self.complete():
			self.__checkValid()

	# Checks if every cell has been filled in with a number.
	# Does not check if the numbers are valid though.
	def complete(self):
		allComplete = True

		# Iterate through each of the 9 blocks
		for blockRow, blockCol in doubleIter(3):
			# Check if the block is complete
			if not self.__completeBlock(blockRow, blockCol):
				allComplete = False
				break

		return allComplete

	# Prints the current notes used to solve the puzzle in a human readable format
	def printNotes(self, fhOut = sys.stdout):
		noteSets = [['1','2','3'], ['4','5','6'], ['7','8','9']]

		header = 'Current Notes'.center(len(self.__blockRowSplit()))

		fhOut.write('%s\n' % (header))
		for blockRow in range(3):
			if blockRow == 0:
				fhOut.write('%s\n' % (self.__blockRowSplit()))
			for row in range(3):
				for i in range(len(noteSets)):
					fhOut.write('||')
					for blockCol in range(3):
						for col in range(3):
							numString = ''
							noteNums = self.getCellNotes(blockRow, blockCol, row, col)
							for num in noteSets[i]:
								if num in noteNums:
									numString += '%s' % (num)
								else:
									numString += ' '
							if col == 2:
								colSplit = '||'
							else:
								colSplit = '|'
							fhOut.write(' %s %s' % (numString, colSplit))
					fhOut.write('\n')
				if row == 2:
					fhOut.write('%s\n' % (self.__blockRowSplit()))
				else:
					fhOut.write('%s\n' % (self.__rowSplit()))

	# Returns the value of a cell at the specified coordinates
	def getCellValue(self, blockRow, blockCol, row, col):
		return self.__matrix[blockRow][blockCol].getValue(row, col)

	# Returns the set() of notes at the specified coordinates
	def getCellNotes(self, blockRow, blockCol, row, col):
		return self.__matrix[blockRow][blockCol].getNoteNumbers(row, col)

	###################
	# Private Methods #
	###################

	###### START
	# Instance variable setters and getters
	#
	def __puzzleChanged(self):
		return self.__changeStatus

	# Lets the solver know changes were made
	def __setChangeTrue(self):
		self.__changeStatus = True

	def __setChangeFalse(self):
		self.__changeStatus = False

	def __puzzleSolved(self):
		return self.__solvedStatus

	def __setSolvedFalse(self):
		self.__solvedStatus = False
	#
	# instance variable setters and getters
	###### END

	###### START
	# Wrappers around SudokuBlock methods
	#
	def __deleteCellNoteNumber(self, num, blockRow, blockCol, row, col):
		self.__matrix[blockRow][blockCol].deleteNoteNumber(num, row, col)

	# Sets the value of the specified cell
	def __setCellValue(self, num, blockRow, blockCol, row, col):
		self.__matrix[blockRow][blockCol].setValue(num, row, col)

	# Clears out available notes from the specified cell
	def __clearCellNoteNumbers(self, blockRow, blockCol, row, col):
		self.__matrix[blockRow][blockCol].clearNoteNumbers(row, col)

	def __validBlock(self, blockRow, blockCol):
		return self.__matrix[blockRow][blockCol].valid()

	def __completeBlock(self, blockRow, blockCol):
		return self.__matrix[blockRow][blockCol].complete()
	#
	# Wrappers around SudokuBlock methods
	###### END

	###### START
	# Shared methods
	#
	# Sets the value of the specified cell and adjusts the notes in the
	# necessary row, column, and block.
	def __setValue(self, num, blockRow, blockCol, row, col):
		# Sets the value of the specified cell
		self.__setCellValue(num, blockRow, blockCol, row, col)

		# Clears out available notes from the specified cell
		self.__clearCellNoteNumbers(blockRow, blockCol, row, col)

		# Clears out available notes from the affected block, row, and column
		self.__removeAffectedNotes(num, blockRow, blockCol, row, col)

		# Let the solver know changes were made
		self.__setChangeTrue()

	# Deletes the specified number from the cell's notes.  If there is only
	# one number left in the notes, then it sets the value
	def __clearCellNoteNumberAndSet(self, num, blockRow, blockCol, row, col):

		noteNums = self.getCellNotes(blockRow, blockCol, row, col)
		if num in noteNums:
			self.__deleteCellNoteNumber(num, blockRow, blockCol, row, col)

			nums = list(noteNums)
			if len(nums) == 1:
				self.__setValue(nums[0], blockRow, blockCol, row, col)

			# Let the solver know changes were made
			self.__setChangeTrue()

	# Iterate through each cell, determine which numbers have already been
	# assigned, and remove them from the list of unassigned numbers
	def __findUnassignedNums(self, cellCoordinatesList):
		# Create a list of all possible numbers that can be assigned to the current set of cells
		unassignedNums = numberSet(3)

		# Iterate through each cell's coordinates
		for cellCoords in cellCoordinatesList:

			# Remove the already assigned number in the current cell from the list of possible numbers
			num = self.getCellValue(
				cellCoords.blockRow,
				cellCoords.blockCol,
				cellCoords.row,
				cellCoords.col,
			)
			if num:
				unassignedNums.discard(num)

		return unassignedNums

	# Clears out available notes from the affected block, row, and column
	def __removeAffectedNotes(self, num, blockRow, blockCol, row, col):

		# Remove the number from the notes along the block
		self.__removeNotesByIter(
			num,
			self.__blockCellCoordsIter,
			blockRow,
			blockCol,
			[],
		)

		# Remove the number from the notes along the row
		self.__removeNotesByIter(
			num,
			self.__rowCellCoordsIter,
			blockRow,
			row,
			[],
		)

		# Remove the number from the notes along the column
		self.__removeNotesByIter(
			num,
			self.__colCellCoordsIter,
			blockCol,
			col,
			[],
		)

	# Goes through each cell passed from the iterator and removes the number from the cell's notes
	def __removeNotesByIter(self, num, coordIter, coordPos1, coordPos2, skipCoordsList):

		# Iterate through each cell
		for coords in coordIter(coordPos1, coordPos2):

			# Skip the cells that are the skip list
			if not(self.__coordsInList(coords, skipCoordsList)):
				# Remove the numbers from the cell notes
				self.__clearCellNoteNumberAndSet(num, coords.blockRow, coords.blockCol, coords.row, coords.col)

	def __coordsInList(self, coords, skipList):
		itemInList = False
		for item in skipList:
			if item == coords:
				itemInList = True
				break
		return itemInList
	#
	# Shared methods
	###### END

	###### START
	# __init__ methods
	#
	def __checkInputParameters(self, fieldsToCheck, args):
		# Check if one of the required parameters was supplied
		missingFields = True
		for field in args:
			if field in fieldsToCheck:
				missingFields = False

		if missingFields:
			raise Exception('One of the following required fields was not provided: %s' % (','.join(fieldsToCheck)))

	# Loads the user specified data
	def __loadInputData(self, args):
		if 'file' in args:
			# Parses file with starting Sudoku numbers and loads object
			self.__loadFromFile(args['file'])
		elif 'data' in args:
			# Parses list of lists with starting Sudoku numbers and loads object
			self.__loadFromData(args['data'])

	# Loads data from a file
	def __loadFromFile(self, file):
		if os.path.isfile(file):
			data = []

			# Converts file contents into a list of lists
			fhIn = open(file, 'rU')
			for line in fhIn:
				nums = self.__parseFileLine(line)
				data.append(nums)
			fhIn.close()

			# Loads data from a list of lists
			self.__loadFromData(data)

		else:
			raise Exception('%s is not a valid file or does not exist.' % (file))

	# Loads data from a list of lists
	def __loadFromData(self, data):
		tempMatrix = instantiateMatrix(3)
		currentBlockRow = 0

		for nums in data:
			# Every 3 lines get incremented
			if self.__currentBlockRowFull(tempMatrix, currentBlockRow):
				currentBlockRow += 1

			tempMatrix[currentBlockRow][0].append(nums[0:3])
			tempMatrix[currentBlockRow][1].append(nums[3:6])
			tempMatrix[currentBlockRow][2].append(nums[6:9])

		self.__instantiateSudokuMatrix(tempMatrix)

	# Parses the line of a file into a valid list
	def __parseFileLine(self, line):
		# Strip newline character
		line = line.strip('\n')

		# Periods are allowed for unknown positions by converting them to spaces
		line = line.replace('.', ' ')

		# Make sure there are at least 9 positions in the line
		# Right padded spaces will be turned into unknowns
		line = line.ljust(9)

		# Convert to a list of numbers
		return list(line)

	# Returns True if the current row of blocks are all full
	def __currentBlockRowFull(self, matrix, blockRow):
		if len(matrix[blockRow][0]) == 3 and \
			len(matrix[blockRow][1]) == 3 and \
			len(matrix[blockRow][2]) == 3:
			return True
		else:
			return False

	# Converts the temporary matrix into one that has SudokuBlock objects
	def __instantiateSudokuMatrix(self, tempMatrix):
		self.__matrix = instantiateMatrix(3)
		# Iterate through each of the 9 blocks
		for blockRow, blockCol in doubleIter(3):
			self.__matrix[blockRow][blockCol] = SudokuBlock(tempMatrix[blockRow][blockCol])

		# Adjusts the notes based on the initial values of the sudoku grid.
		self.__clearInitialNotes()

	# Adjusts the notes based on the initial values of the sudoku grid.
	def __clearInitialNotes(self):

		# Iterate through each block in the sudoku grid
		for cellCoordinatesList in self.__blockCoordsIter():

			# Iterate through each cell's coordinates
			for cellCoords in cellCoordinatesList:

				# If the cell has a number assigned, then clear the block, row, and column notes
				num = self.getCellValue(
					cellCoords.blockRow,
					cellCoords.blockCol,
					cellCoords.row,
					cellCoords.col,
				)
				if num:
					# Clears out available notes from the affected block, row, and column
					self.__removeAffectedNotes(
						num,
						cellCoords.blockRow,
						cellCoords.blockCol,
						cellCoords.row,
						cellCoords.col,
					)

	#
	# __init__ methods
	###### END

	###### START
	# __str__ methods
	#
	def __rowDelimeter(self):
		return '-------------------------'
	#
	# __str__ methods
	###### END

	###### START
	# printNotes methods
	#
	def __rowSplit(self):
		return '-----------------------------------------------------------'

	def __blockRowSplit(self):
		return '==========================================================='
	#
	# printNotes methods
	###### END

	###### START
	# __setSingletons methods
	#
	def __setSingletons(self):
		# Assign singletons within rows
		self.__setSingletonNotes(self.__rowCoordsIter)

		# Assign singletons within columns
		self.__setSingletonNotes(self.__columnCoordsIter)

	def __setSingletonNotes(self, coordIter):

		# Iterate through each line in the sudoku grid
		# The lines will be all rows or all columns, depending on what was passed
		# to this method in coordIter
		for cellCoordinatesList in coordIter():

			# Generate list of numbers that can still be assigned to the
			# remaining cells in the row or column
			unassignedNums = self.__findUnassignedNums(cellCoordinatesList)

			# Iterate through the set of unassigned numbers
			for currentValue in unassignedNums:

				availableCellCount = 0
				availableCellCoords = None

				# Iterate through each cell's coordinates
				for cellCoords in cellCoordinatesList:

					# If that position was already assigned a number then skip it
					if not self.getCellValue(cellCoords.blockRow, cellCoords.blockCol, cellCoords.row, cellCoords.col):
						# Grab the set() of available values for the current cell
						noteNums = self.getCellNotes(cellCoords.blockRow, cellCoords.blockCol, cellCoords.row, cellCoords.col)
						# Keep track of how many positions will allow the current value
						if currentValue in noteNums:
							availableCellCount += 1
							availableCellCoords = cellCoords

							# Once the available cell count is greater than 1, there is no point
							# in going forward because we need singletons
							if availableCellCount > 1:
								break

				# Assuming there is only 1 cell that can accept the current value, then set that cell's value
				if availableCellCount == 1:
					self.__setValue(
						currentValue,
						availableCellCoords.blockRow,
						availableCellCoords.blockCol,
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

		# Iterate through all sudoku grid blocks
		for cellCoordinatesList in self.__blockCoordsIter():
			# Create a list of all unassigned numbers and the coordinates where they are found
			hintCoords = self.__generateHintCoords(cellCoordinatesList)

			# Iterate through each unassigned number
			for num in hintCoords:

				# Candidate lines method works by aligning
				if len(hintCoords[num]) == 2:

					# Store variables just to make code more readable
					coords1 = hintCoords[num][0]
					coords2 = hintCoords[num][1]

					# Candidate line lies along a row, therefore remove note from the rest of the row
					if coords1.alignsByRow(coords2):
						# Remove the number from the notes along the row
						self.__removeNotesByIter(
							num,
							self.__rowCellCoordsIter,
							coords1.blockRow,
							coords1.row,
							[coords1, coords2],
						)

					# Candidate line lies along a column, therefore remove note from the rest of the column
					elif coords1.alignsByCol(coords2):
						# Remove the number from the notes along the column
						self.__removeNotesByIter(
							num,
							self.__colCellCoordsIter,
							coords1.blockCol,
							coords1.col,
							[coords1, coords2],
						)

	# Stores the coordinates for all hint positions
	def __generateHintCoords(self, cellCoordinatesList):
		hintCoords = numDictList(3)

		# Iterate through each cell's coordinates
		for cellCoords in cellCoordinatesList:
			# Store the coordinates where all numbers are found
			noteNums = self.getCellNotes(
				cellCoords.blockRow,
				cellCoords.blockCol,
				cellCoords.row,
				cellCoords.col,
			)
			for num in noteNums:
				hintCoords[num].append(cellCoords)

		return hintCoords
	#
	# __reduceCandidateLines methods
	###### END

	###### START
	# __reduceXwing methods
	#
	def __reduceXwing(self):
		# Search for valid xwing cells along rows to reduce notes along the columns
		self.__reduceXwingRow()

		# Search for valid xwing cells along columns to reduce notes along the rows
		self.__reduceXwingCol()

	# Search for valid xwing cells along rows to reduce notes along the columns
	def __reduceXwingRow(self):

		# Search all rows for pairs of cells that are the 2 remaining
		# cells that can contain 1 specific number
		potentialXwings = self.__potentialXwings(self.__rowCoordsIter)

		# Iterate through each number
		for num in potentialXwings:

			# Iterate through all possible pairs of cells
			for data1, data2 in pairwiseIter(potentialXwings[num]):

				# data1[0] = ulCoords, data1[1] = urCoords
				# data2[0] = llCoords, data2[1] = lrCoords

				# Ensures the 4 cells properly align to form xwing cells, which are
				# required for the xwing method to work
				if self.__validXwingRowCells(data1[0], data1[1], data2[0], data2[1]):

					# Remove the number from the notes along the column
					self.__removeNotesByIter(
						num,
						self.__colCellCoordsIter,
						data1[0].blockCol,
						data1[0].col,
						[data1[0], data2[0]],
					)

					# Remove the number from the notes along the column
					self.__removeNotesByIter(
						num,
						self.__colCellCoordsIter,
						data1[1].blockCol,
						data1[1].col,
						[data1[1], data2[1]],
					)

	# Search for valid xwing cells along columns to reduce notes along the rows
	def __reduceXwingCol(self):

		# Search all columns for pairs of cells that are the 2 remaining
		# cells that can contain 1 specific number
		potentialXwings = self.__potentialXwings(self.__columnCoordsIter)

		# Iterate through each number
		for num in potentialXwings:

			# Iterate through all possible pairs of cells
			for data1, data2 in pairwiseIter(potentialXwings[num]):

				# data1[0] = ulCoords, data1[1] = llCoords
				# data2[0] = urCoords, data2[1] = lrCoords

				# Ensures the 4 cells properly align to form xwing cells, which are
				# required for the xwing method to work
				if self.__validXwingColCells(data1[0], data1[1], data2[0], data2[1]):

					# Remove the number from the notes along the row
					self.__removeNotesByIter(
						num,
						self.__rowCellCoordsIter,
						data1[0].blockRow,
						data1[0].row,
						[data1[0], data2[0]],
					)

					# Remove the number from the notes along the row
					self.__removeNotesByIter(
						num,
						self.__rowCellCoordsIter,
						data1[1].blockRow,
						data1[1].row,
						[data1[1], data2[1]],
					)

	# Ensures the 4 cells properly align to form xwing cells, which are
	# required for the xwing method to work
	def __validXwingRowCells(self, ulCoords, urCoords, llCoords, lrCoords):
		# Ensures the rows are in different blockRows
		# Ensures the upperleft and lowerleft coords are in the same grid column
		# Ensures the upperright and lowerright coords are in the same grid column
		if ulCoords.blockRow != llCoords.blockRow and \
			ulCoords.alignsByCol(llCoords) and urCoords.alignsByCol(lrCoords):
			return True
		else:
			return False

	# Ensures the 4 cells properly align to form xwing cells, which are
	# required for the xwing method to work
	def __validXwingColCells(self, ulCoords, llCoords, urCoords, lrCoords):
		# Ensures the columns are in different blockColumns
		# Ensures the upperleft and upperright coords are in the same grid row
		# Ensures the lowerleft and lowerright coords are in the same grid row
		if ulCoords.blockCol != urCoords.blockCol and \
			ulCoords.alignsByRow(urCoords) and llCoords.alignsByRow(lrCoords):
			return True
		else:
			return False

	# Search all rows/columns for pairs of cells that are the 2 remaining
	# cells that can contain 1 specific number
	def __potentialXwings(self, coordIter):
		potentialXwings = numDictList(3)
		# Iterate through each row/cell in the sudoku grid
		for cellCoordinatesList in coordIter():
			hintCoords = numDictList(3)

			# Iterate through each cell's coordinates
			for cellCoords in cellCoordinatesList:

				# Loop through all notes in the current cell
				noteNums = self.getCellNotes(
					cellCoords.blockRow,
					cellCoords.blockCol,
					cellCoords.row,
					cellCoords.col,
				)
				for num in noteNums:
					# Store the current coordinates
					hintCoords[num].append(cellCoords)

			# Keep only the cells that have exactly 2 numbers left in the row/column
			for num in hintCoords:
				if len(hintCoords[num]) == 2:
					potentialXwings[num].append(hintCoords[num])

		return potentialXwings
	#
	# __reduceXwing methods
	###### END

	###### START
	# __reduceNakedSets methods
	#
	def __reduceNakedSets(self):
		# Reduce naked sets by row
		self.__findNakedSets(self.__rowCoordsIter)

		# Reduce naked sets by column
		self.__findNakedSets(self.__columnCoordsIter)

		# Reduce naked sets by block
		self.__findNakedSets(self.__blockCoordsIter)

	def __findNakedSets(self, coordIter):

		# Iterate through each row/column/block in the sudoku grid
		for cellCoordinatesList in coordIter():
			noteCoords = []
			noteList = []

			# Iterate through each cell's coordinates
			for cellCoords in cellCoordinatesList:

				# Store the cell's coordinates and notes
				noteNums = self.getCellNotes(
					cellCoords.blockRow,
					cellCoords.blockCol,
					cellCoords.row,
					cellCoords.col,
				)
				if noteNums:
					noteCoords.append(cellCoords)
					noteList.append(noteNums)

			# setSize determines the naked set size, 2 = naked pairs, 3 = naked trios, 4 = naked quads
			for setSize in range(2, 5):

				# Looks for naked sets in the current set of cells
				self.__findNakedSetCombinations(setSize, noteList, noteCoords, cellCoordinatesList)

	# Finds all valid naked sets.  If any are found, remove the numbers that are found in the naked
	# sets from all remaining neighboring cells.
	def __findNakedSetCombinations(self, setSize, noteList, noteCoords, cellCoordinatesList):

		# Generates a list with all combinations of size setSize.
		# If noteList = [0, 1, 2] and setSize = 2, then 3 indexLists would be created
		# [0, 1], [0, 2], [1, 2]
		for indexList in combinations(range(len(noteList)), setSize):

			# Generate a set of the unique notes in noteList
			uniqueNums = self.__combineNotes(noteList, indexList)

			# Valid naked sets have been found when the number of unique numbers == the set size.
			# If 2 unique numbers are found in 2 cells, then you can remove those 2 numbers from
			# the remaining cells.  Same criteria applies if you find 3 unique numbers in 3 cells,
			# 4 unique numbers in 4 cells.
			if len(uniqueNums) == setSize:

				# Store the coordinates of the cells that made up the naked sets.
				skipCoordsList = []
				for i in indexList:
					skipCoordsList.append(noteCoords[i])

				# Iterate through each number in the naked set
				for num in uniqueNums:

					# Iterate through each cell in the current row/column/block
					for coords in cellCoordinatesList:

						# Skip the cells that are in the skip list (cells that made up the naked set)
						if not(self.__coordsInList(coords, skipCoordsList)):

							# Remove the numbers from the cell notes
							self.__clearCellNoteNumberAndSet(
								num,
								coords.blockRow,
								coords.blockCol,
								coords.row,
								coords.col,
							)

	# Generate a set of the unique notes in noteList
	def __combineNotes(self, setList, coords):
		uniqueNums = set()
		for indexNum in coords:
			for num in list(setList[indexNum]):
				uniqueNums.add(num)
		return uniqueNums
	#
	# __reduceNakedSets methods
	###### END

	###### START
	# __reduceXYwing methods
	#
	def __reduceXYwing(self):
		# Reduce XY wing sets by row
		self.__findXYwingSets(self.__rowCoordsIter)

		# Reduce XY wing sets by column
		self.__findXYwingSets(self.__columnCoordsIter)

	def __findXYwingSets(self, coordIter):

		# Iterate through each row/column in the sudoku grid
		for cellCoordinatesList in coordIter():

			# Iterate through each cell's coordinates and create all pairwise combinations
			# Keep only the pairs of coordinates in different blocks and each contain
			# exactly 2 notes.
			for cellCoordsList in filter(self.__validXYwingPair, combinations(cellCoordinatesList, 2)):

				# These 2 cells make up a valid potential XY wing pair
				cell1 = cellCoordsList[0]
				cell2 = cellCoordsList[1]

				# Get the notes for each cell
				cell1Notes = self.getCellNotes(cell1.blockRow, cell1.blockCol, cell1.row, cell1.col)
				cell2Notes = self.getCellNotes(cell2.blockRow, cell2.blockCol, cell2.row, cell2.col)

				# Create a new set that contains the numbers different between both cells
				# Only cell pairs that have 1 element in common are valid xy wing pairs
				# eg, set([1,2]) + set([2,3]) = valid pair since symmetric difference = set([1,3])
				newNotes = cell1Notes.symmetric_difference(cell2Notes)
				if len(newNotes) == 2:

					# Check each block that is a parent to each cell for any cells that have notes
					# equal to newNotes
					self.__findBentCell(newNotes, cell1, cell2)
					self.__findBentCell(newNotes, cell2, cell1)

	def __findBentCell(self, searchNotes, cell1, cell2):
		if cell1.alignsByRow(cell2):
			alignType = 'row'
		elif cell1.alignsByCol(cell2):
			alignType = 'col'

		# Iterate through each cell in cell1's block
		for coords in self.__blockCellCoordsIter(cell1.blockRow, cell1.blockCol):

			# Start looking for a valid bent cell that has the same cell notes as searchNotes
			noteNums = self.getCellNotes(
				coords.blockRow,
				coords.blockCol,
				coords.row,
				coords.col,
			)
			if noteNums == searchNotes:
				validXYWing = False

				# If cell1 and cell2 are aligned by row or column, make
				# sure the new cell does not also align by row or column respectively
				if alignType == 'row' and not cell1.alignsByRow(coords):
					validXYWing = True
				elif alignType == 'col' and not cell1.alignsByCol(coords):
					validXYWing = True

				# All criteria is perfect to do xy wing technique.
				if validXYWing:
					# Find the number to remove and the cell to remove the number from
					removeNum, removeCoords = self.__intersectXYWingCells(
						coords,
						cell2,
						alignType,
					)

					self.__clearCellNoteNumberAndSet(
						removeNum,
						removeCoords.blockRow,
						removeCoords.blockCol,
						removeCoords.row,
						removeCoords.col,
					)

	def __intersectXYWingCells(self, bentCell, cell2, alignType):
		# Get the number shared between both sets of notes
		# This number will be removed from the intersection between the 2 cells
		sharedNotes = self.__notesInCommon(bentCell, cell2)
		removeNum = sharedNotes.pop()

		if alignType == 'row':
			removeCoords = SudokuCoordinates(
				bentCell.blockRow,
				cell2.blockCol,
				bentCell.row,
				cell2.col,
			)
		elif alignType == 'col':
			removeCoords = SudokuCoordinates(
				cell2.blockRow,
				bentCell.blockCol,
				cell2.row,
				bentCell.col,
			)

		return removeNum, removeCoords

	def __notesInCommon(self, coords1, coords2):
		noteNums1 = self.getCellNotes(
			coords1.blockRow,
			coords1.blockCol,
			coords1.row,
			coords1.col,
		)

		noteNums2 = self.getCellNotes(
			coords2.blockRow,
			coords2.blockCol,
			coords2.row,
			coords2.col,
		)

		return noteNums1.intersection(noteNums2)

	def __validXYwingPair(self, x):
		if x[0].alignsByBlock(x[1]):
			return False
		else:
			# Store the cell pair's notes
			noteNums1 = self.getCellNotes(
				x[0].blockRow,
				x[0].blockCol,
				x[0].row,
				x[0].col,
			)
			noteNums2 = self.getCellNotes(
				x[1].blockRow,
				x[1].blockCol,
				x[1].row,
				x[1].col,
			)
			if len(noteNums1) == 2 and len(noteNums2) == 2:
				return True
			else:
				return False
	#
	# __reduceXYwing methods
	###### END

	###### START
	# __reduceMultipleLines methods
	#
	def __reduceMultipleLines(self):

		# Iterate through each block
		for cellCoordinatesList in self.__blockCoordsIter():

			# Extract the current block coordinates
			blockRow = cellCoordinatesList[0].blockRow
			blockCol = cellCoordinatesList[0].blockCol

			# Generate list of numbers that can still be assigned to the
			# remaining cells in the row or column
			unassignedNums = self.__findUnassignedNums(cellCoordinatesList)

			# Look for rows/columns that share the unassigned number in pairs of rows
			for num in unassignedNums:

				# Identify the rows in the current block that can have the number eliminated from the notes
				sharedRows = self.__findSharedLinesByRow(num, blockRow, blockCol)
				if sharedRows:

					# Remove the number from the cell's notes
					for row in sharedRows:
						for col in range(3):
							self.__clearCellNoteNumberAndSet(num, blockRow, blockCol, row, col)

				# Identify the columns in the current block that can have the number eliminated from the notes
				sharedCols = self.__findSharedLinesByCol(num, blockRow, blockCol)
				if sharedCols:

					# Remove the number from the cell's notes
					for col in sharedCols:
						for row in range(3):
							self.__clearCellNoteNumberAndSet(num, blockRow, blockCol, row, col)

	# Identify the rows in the current block that can have the number eliminated from the notes
	def __findSharedLinesByRow(self, num, blockRow, blockCol):
		sharedRows = set()
		affectedBlocks = set()

		# Iterate through the remaining columns except for the starting one
		for blockColLoop in filter(lambda x: x != blockCol, range(3)):

			# Iterate through each cell in the block
			for row, col in doubleIter(3):

				# Check the cell's notes if num can be placed here.  If it can, track the row and block
				noteNums = self.getCellNotes(blockRow, blockColLoop, row, col)
				if num in noteNums:
					sharedRows.add(row)
					affectedBlocks.add(blockColLoop)

		# Criteria for the multiple lines technique is that there are 2 shared rows
		# across 2 blocks with the same number.
		if len(sharedRows) == 2 and len(affectedBlocks) == 2:
			return sharedRows
		else:
			return set()

	# Identify the columns in the current block that can have the number eliminated from the notes
	def __findSharedLinesByCol(self, num, blockRow, blockCol):
		sharedCols = set()
		affectedBlocks = set()

		# Iterate through the remaining rows except for the starting one
		for blockRowLoop in filter(lambda x: x != blockRow, range(3)):

			# Iterate through each cell in the block
			for row, col in doubleIter(3):

				# Check the cell's notes if num can be placed here.  If it can, track the column and block
				noteNums = self.getCellNotes(blockRowLoop, blockCol, row, col)
				if num in noteNums:
					sharedCols.add(col)
					affectedBlocks.add(blockRowLoop)

		# Criteria for the multiple lines technique is that there are 2 shared columns
		# across 2 blocks with the same number.
		if len(sharedCols) == 2 and len(affectedBlocks) == 2:
			return sharedCols
		else:
			return set()
	#
	# __reduceMultipleLines methods
	###### END

	###### START
	# __checkValid methods
	#
	def __checkValid(self):
		# Check valid cells by row
		self.__checkValidCells(self.__rowCoordsIter, 'Rows')

		# Check valid cells by column
		self.__checkValidCells(self.__columnCoordsIter, 'Columns')

		# Check valid cells by block
		self.__checkValidCells(self.__blockCoordsIter, 'Blocks')

		# The previous method calls will raise Exceptions if the completed grid is invalid
		# so if it gets here, then the puzzle is valid and solved
		self.__setSolvedTrue()

	# Makes sure there are 9 unique elements in the iterator
	def __checkValidCells(self, coordIter, iterType):

		# Iterate through each row/column/block in the sudoku grid
		for cellCoordinatesList in coordIter():
			validNums = set()

			# Iterate through each cell's coordinates
			for cellCoords in cellCoordinatesList:
				num = self.getCellValue(
					cellCoords.blockRow,
					cellCoords.blockCol,
					cellCoords.row,
					cellCoords.col,
				)
				validNums.add(num)

			if len(validNums) != 9:
				print self
				raise Exception('Completed puzzle is not a valid solution.  %s contain duplicate entries.  Check the starting puzzle or code to remove bugs.' % (iterType))

	def __setSolvedTrue(self):
		self.__solvedStatus = True
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
	def __rowCoordsIter(self):
		for blockRow, row in doubleIter(3):
			rowCoords = []
			for coords in self.__rowCellCoordsIter(blockRow, row):
				rowCoords.append(coords)
			yield rowCoords

	# Iterator that yields coordinate objects found in the row specified with blockRow, row
	def __rowCellCoordsIter(self, blockRow, row):
		for blockCol, col in doubleIter(3):
			yield SudokuCoordinates(blockRow, blockCol, row, col)

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
	def __columnCoordsIter(self):
		for blockCol, col in doubleIter(3):
			colCoords = []
			for coords in self.__colCellCoordsIter(blockCol, col):
				colCoords.append(coords)
			yield colCoords

	# Iterator that yields coordinate objects found in the column specified with blockCol, col
	def __colCellCoordsIter(self, blockCol, col):
		for blockRow, row in doubleIter(3):
			yield SudokuCoordinates(blockRow, blockCol, row, col)

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
	def __blockCoordsIter(self):
		for blockRow, blockCol in doubleIter(3):
			blockCoords = []
			for coords in self.__blockCellCoordsIter(blockRow, blockCol):
				blockCoords.append(coords)
			yield blockCoords

	# Iterator that yields coordinate objects found in the block specified with blockRow, blockCol
	def __blockCellCoordsIter(self, blockRow, blockCol):
		for row, col in doubleIter(3):
			yield SudokuCoordinates(blockRow, blockCol, row, col)

	#
	# Private Iterator Methods
	######### END
