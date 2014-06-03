import os, sys

from SudokuSolver.modules.utilities import instantiateMatrix, doubleIter, numberSet, numDictList
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

			# Reduce numbers based on hint pairs in the same row or column
			self.__reduceCandidateLines()

			# Reduce numbers based on using the xwing method
			self.__reduceXwing()

			# Reduce numbers based on naked pairs/trios
			self.__reduceNakedSets()

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

	def __setCellValue(self, num, blockRow, blockCol, row, col):
		self.__matrix[blockRow][blockCol].setValue(num, row, col)

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

		# Clear the current number from the notes in every cell of the specified block
		self.__clearBlockNoteNumber(num, blockRow, blockCol)

		# Clear the current number from the notes in every row and column that contain the
		# specified cell
		self.__clearRowColNoteNumber(blockRow, blockCol, row, col)

		# Let the solver know changes were made
		self.__setChangeTrue()

	# Clear the current number from the notes in every cell of the specified block
	def __clearBlockNoteNumber(self, num, blockRow, blockCol):
		for row, col in doubleIter(3):
			self.__clearCellNoteNumberAndSet(num, blockRow, blockCol, row, col)

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

		# Iterate through each cell and extract the coordinates
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

		self.__clearInitialValueNotes()

	def __clearInitialValueNotes(self):
		# Iterate through each of the 9 blocks
		for blockRow, blockCol in doubleIter(3):

			# Reduce numbers within the SudokuBlock based on initial values
			for num in self.__validBlockNums(blockRow, blockCol):
				self.__clearBlockNoteNumber(num, blockRow, blockCol)

			# Reduce numbers across all rows/columns based on initial SudokuBlock values
			self.__reduceRowColNotes(blockRow, blockCol)

	def __validBlockNums(self, blockRow, blockCol):
		validNums = set()
		# Iterate through each of the 9 cells in blockRow, blockCol
		for row, col in doubleIter(3):
			num = self.getCellValue(blockRow, blockCol, row, col)
			if num:
				validNums.add(num)
		return validNums

	def __reduceRowColNotes(self, blockRow, blockCol):
		# Iterate through each of the 9 cells in blockRow, blockCol
		for row, col in doubleIter(3):
			self.__clearRowColNoteNumber(blockRow, blockCol, row, col)
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
		self.__setSingletonNotes(self.__rowCellCoordsIter)

		# Assign singletons within columns
		self.__setSingletonNotes(self.__colCellCoordsIter)

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

				# Iterate through each of the cells
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
	def __reduceCandidateLines(self):

		for cellCoordinatesList in self.__blockCellCoordsIter():
			hintCoords = self.__generateHintCoords(cellCoordinatesList)
			blockRow = cellCoordinatesList[0].blockRow
			blockCol = cellCoordinatesList[0].blockCol

			for num in hintCoords:
				if len(hintCoords[num]) == 2:
					# Candidate line lies along a row, therefore remove from every blockColum on the same row
					if hintCoords[num][0][0] == hintCoords[num][1][0]:
						for testBlockCol in range(3):
							if testBlockCol == blockCol:
								continue
							for unitCol in range(3):
								self.__clearCellNoteNumberAndSet(num, blockRow, testBlockCol, hintCoords[num][0][0], unitCol)
					# Candidate line lies along a column, therefore remove from every blockRow on the same column
					elif hintCoords[num][0][1] == hintCoords[num][1][1]:
						for testBlockRow in range(3):
							if testBlockRow == blockRow:
								continue
							for unitRow in range(3):
								self.__clearCellNoteNumberAndSet(num, testBlockRow, blockCol, unitRow, hintCoords[num][0][1])

	def __generateHintCoords(self, cellCoordinatesList):
		hintCoords = numDictList(3)

		for cellCoords in cellCoordinatesList:
			noteNums = self.getCellNotes(cellCoords.blockRow, cellCoords.blockCol, cellCoords.row, cellCoords.col)
			for num in noteNums:
				hintCoords[num].append((cellCoords.row, cellCoords.col))

		return hintCoords
	#
	# __reduceCandidateLines methods
	###### END

	###### START
	# __reduceXwing methods
	#
	def __reduceXwing(self):
		self.__reduceXwingRow()
		self.__reduceXwingCol()

	def __reduceXwingRow(self):

		potentialXwings = self.__possibleRowXwings()
		for num in potentialXwings:
			itemLen = len(potentialXwings[num])
			if itemLen > 1:
				# Performs all pairwise combinations looking for valid xwings
				for i in range(itemLen-1):
					for j in range(i+1,itemLen):
						row1 = potentialXwings[num][i]
						row2 = potentialXwings[num][j]

						blockRow1 = row1[0].blockRow
						blockRow2 = row2[0].blockRow
						blockCol1_1 = row1[0].blockCol
						blockCol2_1 = row2[0].blockCol
						blockCol1_2 = row1[1].blockCol
						blockCol2_2 = row2[1].blockCol
						row1_1 = row1[0].row
						row2_1 = row2[0].row
						col1_1 = row1[0].col
						col2_1 = row2[0].col
						col1_2 = row1[1].col
						col2_2 = row2[1].col

						# Ensures the rows are in different blockRows
						# Ensures the columns are in the same blockColumns
						# Ensures the columns are in the same columns
						if blockRow1 != blockRow2 and \
							blockCol1_1 == blockCol2_1 and blockCol1_2 == blockCol2_2 and \
							col1_1 == col2_1 and col1_2 == col2_2:
							self.__removeXwingCol(num, blockCol1_1, col1_1, blockRow1, row1_1, blockRow2, row2_1)
							self.__removeXwingCol(num, blockCol1_2, col1_2, blockRow1, row1_1, blockRow2, row2_1)

	def __reduceXwingCol(self):

		potentialXwings = self.__possibleColXwings()
		for num in potentialXwings:
			itemLen = len(potentialXwings[num])
			if itemLen > 1:
				# Performs all pairwise combinations looking for valid xwings
				for i in range(itemLen-1):
					for j in range(i+1,itemLen):
						row1 = potentialXwings[num][i]
						row2 = potentialXwings[num][j]

						blockRow1_1 = row1[0].blockRow
						blockRow2_1 = row2[0].blockRow
						blockRow1_2 = row1[1].blockRow
						blockRow2_2 = row2[1].blockRow

						blockCol1_1 = row1[0].blockCol
						blockCol2_1 = row2[0].blockCol
						blockCol1_2 = row1[1].blockCol
						blockCol2_2 = row2[1].blockCol

						row1_1 = row1[0].row
						row2_1 = row2[0].row
						row1_2 = row1[1].row
						row2_2 = row2[1].row

						col1_1 = row1[0].col
						col2_1 = row2[0].col
						col1_2 = row1[1].col
						col2_2 = row2[1].col

						# Ensures the columns are in different blockColumns
						# Ensures the rows are in the same blockRows
						# Ensures the rows are in the same rows
						if blockCol1_1 != blockCol2_1 and \
							blockRow1_1 == blockRow2_1 and blockRow1_2 == blockRow2_2 and \
							row1_1 == row2_1 and row1_2 == row2_2:
							self.__removeXwingRow(num, blockRow1_1, row1_1, blockCol1_1, col1_1, blockCol2_1, col2_1)
							self.__removeXwingRow(num, blockRow1_2, row1_2, blockCol1_1, col1_1, blockCol2_1, col2_1)

	def __possibleRowXwings(self):
		potentialXwings = self.__potentialXwings(self.__rowCellCoordsIter)
		return potentialXwings

	def __possibleColXwings(self):
		potentialXwings = self.__potentialXwings(self.__colCellCoordsIter)
		return potentialXwings

	def __potentialXwings(self, coordIter):
		potentialXwings = numDictList(3)
		for cellCoordinatesList in coordIter():
			hintCoords = numDictList(3)
			for cellCoords in cellCoordinatesList:

				noteNums = self.getCellNotes(
					cellCoords.blockRow,
					cellCoords.blockCol,
					cellCoords.row,
					cellCoords.col,
				)
				for num in noteNums:
					hintCoords[num].append(
						SudokuCoordinates(
							cellCoords.blockRow,
							cellCoords.blockCol,
							cellCoords.row,
							cellCoords.col,
						)
					)

			for num in hintCoords:
				if len(hintCoords[num]) == 2:
					potentialXwings[num].append(hintCoords[num])

		return potentialXwings

	def __removeXwingRow(self, num, blockRow, row, blockCol1Skip, col1Skip, blockCol2Skip, col2Skip):
		for blockCol, col in doubleIter(3):
			if self.__skip(blockCol, col, blockCol1Skip, col1Skip) or self.__skip(blockCol, col, blockCol2Skip, col2Skip):
				continue
			self.__clearCellNoteNumberAndSet(num, blockRow, blockCol, row, col)

	def __removeXwingCol(self, num, blockCol, col, blockRow1Skip, row1Skip, blockRow2Skip, row2Skip):
		for blockRow, row in doubleIter(3):
			if self.__skip(blockRow, row, blockRow1Skip, row1Skip) or self.__skip(blockRow, row, blockRow2Skip, row2Skip):
				continue
			self.__clearCellNoteNumberAndSet(num, blockRow, blockCol, row, col)

	def __skip(self, blockRow, row, blockRowSkip, rowSkip):
		if blockRow == blockRowSkip and row == rowSkip:
			return True
		else:
			return False
	#
	# __reduceXwing methods
	###### END

	###### START
	# __reduceNakedSets methods
	#
	def __reduceNakedSets(self):
		# Reduce naked sets by row
		self.__findNakedSets(self.__rowCellCoordsIter)

		# Reduce naked sets by column
		self.__findNakedSets(self.__colCellCoordsIter)

		# Reduce naked sets by block
		self.__findNakedSets(self.__blockCellCoordsIter)

	def __findNakedSets(self, coordIter):

		for cellCoordinatesList in coordIter():
			noteCoords = []
			noteList = []
			for cellCoords in cellCoordinatesList:

				noteNums = self.getCellNotes(cellCoords.blockRow, cellCoords.blockCol, cellCoords.row, cellCoords.col)
				if noteNums:
					noteCoords.append(SudokuCoordinates(cellCoords.blockRow, cellCoords.blockCol, cellCoords.row, cellCoords.col))
					noteList.append(noteNums)

			noteLen = len(noteList)
			if noteLen >= 5:
				self.__findNakedPairs(noteList, noteCoords, noteLen, cellCoordinatesList)
				self.__findNakedTrios(noteList, noteCoords, noteLen, cellCoordinatesList)
				self.__findNakedQuads(noteList, noteCoords, noteLen, cellCoordinatesList)
			elif noteLen <= 4:
				self.__findNakedPairs(noteList, noteCoords, noteLen, cellCoordinatesList)
				self.__findNakedTrios(noteList, noteCoords, noteLen, cellCoordinatesList)
			elif noteLen <= 3:
				self.__findNakedPairs(noteList, noteCoords, noteLen, cellCoordinatesList)

	def __findNakedPairs(self, noteList, noteCoords, noteLen, cellCoordinatesList):
		for i in range(noteLen - 1):
			for j in range(i + 1, noteLen):
				uniqueNums = self.__combineNotes(noteList, [i, j])
				if len(uniqueNums) == 2:
					self.__removeNakedSetNotes(uniqueNums, cellCoordinatesList, noteCoords, [i, j])

	def __findNakedTrios(self, noteList, noteCoords, noteLen, cellCoordinatesList):
		for i in range(noteLen - 2):
			for j in range(i + 1, noteLen - 1):
				for k in range(j + 1, noteLen):
					uniqueNums = self.__combineNotes(noteList, [i, j, k])
					if len(uniqueNums) == 3:
						self.__removeNakedSetNotes(uniqueNums, cellCoordinatesList, noteCoords, [i, j, k])

	def __findNakedQuads(self, noteList, noteCoords, noteLen, cellCoordinatesList):
		for i in range(noteLen - 3):
			for j in range(i + 1, noteLen - 2):
				for k in range(j + 1, noteLen - 1):
					for l in range(k + 1, noteLen):
						uniqueNums = self.__combineNotes(noteList, [i, j, k, l])
						if len(uniqueNums) == 4:
							self.__removeNakedSetNotes(uniqueNums, cellCoordinatesList, noteCoords, [i, j, k, l])

	def __combineNotes(self, setList, coords):
		uniqueNums = set()
		for indexNum in coords:
			for num in list(setList[indexNum]):
				uniqueNums.add(num)
		return uniqueNums

	def __removeNakedSetNotes(self, removeNums, cellCoordinatesList, skipCoords, skipCoordsIndex):
		for cellCoords in cellCoordinatesList:

			if not self.__skipCoords(skipCoords, skipCoordsIndex, cellCoords.blockRow, cellCoords.blockCol, cellCoords.row, cellCoords.col):
				for num in removeNums:
					self.__clearCellNoteNumberAndSet(num, cellCoords.blockRow, cellCoords.blockCol, cellCoords.row, cellCoords.col)

	def __skipCoords(self, skipCoords, skipIndex, blockRow, blockCol, row, col):
		skip = False
		for i in skipIndex:
			testBlockRow = skipCoords[i].blockRow
			testBlockCol = skipCoords[i].blockCol
			testRow = skipCoords[i].row
			testCol = skipCoords[i].col
			if testBlockRow == blockRow and testBlockCol == blockCol and testRow == row and testCol == col:
				skip = True
		return skip
	#
	# __reduceNakedSets methods
	###### END

	###### START
	# __reduceMultipleLines methods
	#
	def __reduceMultipleLines(self):

		# Iterate through each block
		for cellCoordinatesList in self.__blockCellCoordsIter():

			# Extract the current block coordinates
			blockRow = cellCoordinatesList[0].blockRow
			blockCol = cellCoordinatesList[0].blockCol

			# Generate list of numbers that can still be assigned to the
			# remaining cells in the row or column
			unassignedNums = self.__findUnassignedNums(cellCoordinatesList)

			# Look for rows/columns that share the unassigned number in pairs of rows
			for num in unassignedNums:

				# Identify the rows in the current block that can have the number eliminted from the notes
				sharedRows = self.__findSharedLinesByRow(num, blockRow, blockCol)
				if sharedRows:

					# Remove the number from the cell's notes
					for row in sharedRows:
						for col in range(3):
							self.__clearCellNoteNumberAndSet(num, blockRow, blockCol, row, col)

				# Identify the columns in the current block that can have the number eliminted from the notes
				sharedCols = self.__findSharedLinesByCol(num, blockRow, blockCol)
				if sharedCols:

					# Remove the number from the cell's notes
					for col in sharedCols:
						for row in range(3):
							self.__clearCellNoteNumberAndSet(num, blockRow, blockCol, row, col)

	# Identify the rows in the current block that can have the number eliminted from the notes
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

	# Identify the columns in the current block that can have the number eliminted from the notes
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
	# __clearRowColNoteNumber methods
	#
	# If the cell has an assigned value, then delete the cell's value from the notes
	# across all rows/columns
	def __clearRowColNoteNumber(self, blockRow, blockCol, row, col):
		num = self.getCellValue(blockRow, blockCol, row, col)
		if num:
			# If num is defined, then remove all note values in the columns/rows
			self.__clearCellNoteNumberFromRow(num, blockRow, blockCol, row)
			self.__clearCellNoteNumberFromColumn(num, blockRow, blockCol, col)

	# Delete the specified number from all cell notes in the column
	def __clearCellNoteNumberFromColumn(self, num, blockRow, blockCol, col):
		for blockRowLoop in range(3):
			if blockRowLoop == blockRow:
				continue
			for row in range(3):
				self.__clearCellNoteNumberAndSet(num, blockRowLoop, blockCol, row, col)

	# Delete the specified number from all cell notes in the row
	def __clearCellNoteNumberFromRow(self, num, blockRow, blockCol, row):
		for blockColLoop in range(3):
			if blockColLoop == blockCol:
				continue
			for col in range(3):
				self.__clearCellNoteNumberAndSet(num, blockRow, blockColLoop, row, col)
	#
	# __clearRowColNoteNumber methods
	###### END

	###### START
	# __checkValid methods
	#
	def __checkValid(self):
		self.__checkValidBlocks()
		self.__checkValidRows()
		self.__checkValidCols()
		self.__setSolvedTrue()

	def __checkValidBlocks(self):
		# Iterate through each of the 9 blocks to make sure each one has 9 unique numbers
		for blockRow, blockCol in doubleIter(3):
			if not self.__validBlock(blockRow, blockCol):
				print self
				raise Exception('Completed puzzle is not a valid solution.  Block (%s,%s) contains duplicate entries.  Check the code to remove bugs.' % (blockRow, blockCol))

	def __checkValidRows(self):
		# Checks that rows have 9 unique numbers
		for blockRow, row in doubleIter(3):
			if not self.__validRow(blockRow, row):
				print self
				raise Exception('Completed puzzle is not a valid solution.  Row (%s,%s) contains duplicate entries.  Check the code to remove bugs.' % (blockRow, row))

	def __checkValidCols(self):
		# Checks that columns have 9 unique numbers
		for blockCol, col in doubleIter(3):
			if not self.__validCol(blockCol, col):
				print self
				raise Exception('Completed puzzle is not a valid solution.  Column (%s,%s) contains duplicate entries.  Check the code.' % (blockCol, col))

	def __validRow(self, blockRow, row):
		validSolution = True
		validNums = set()
		for blockCol, col in doubleIter(3):
			num = self.getCellValue(blockRow, blockCol, row, col)
			validNums.add(num)
		if len(validNums) != 9:
			validSolution = False
		return validSolution

	def __validCol(self, blockCol, col):
		validSolution = True
		validNums = set()
		for blockRow, row in doubleIter(3):
			num = self.getCellValue(blockRow, blockCol, row, col)
			validNums.add(num)
		if len(validNums) != 9:
			validSolution = False
		return validSolution

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
	def __rowCellCoordsIter(self):
		for blockRow, row in doubleIter(3):
			rowCoords = []
			for blockCol, col in doubleIter(3):
				rowCoords.append(SudokuCoordinates(blockRow, blockCol, row, col))
			yield rowCoords

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
	def __colCellCoordsIter(self):
		for blockCol, col in doubleIter(3):
			colCoords = []
			for blockRow, row in doubleIter(3):
				colCoords.append(SudokuCoordinates(blockRow, blockCol, row, col))
			yield colCoords

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
	def __blockCellCoordsIter(self):
		for blockRow, blockCol in doubleIter(3):
			blockCoords = []
			for row, col in doubleIter(3):
				blockCoords.append(SudokuCoordinates(blockRow, blockCol, row, col))
			yield blockCoords
	#
	# Private Iterator Methods
	######### END
