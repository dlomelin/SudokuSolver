from SudokuSolver.modules.utilities import instantiateMatrix, doubleIter

# Class that represents a NxN sudoku block with N^2 cells
class SudokuBlock(object):
	SQUARE_SIZE = 3
	CELL_COUNT = SQUARE_SIZE ** 2

	def __init__(self, numList):
		# Make sure the values passed in are in a valid format
		self.__validateNumList(numList)

		# Set the values to what the user passed in
		self.__values = numList

		# Creates new notes for each of the N^2 cells
		self.__createNoteNumbers()

		# Remove all notes for cells that have been assigned a number
		self.__eliminateKnownNumbers()

	##################
	# Public Methods #
	##################

	# Checks if the block contains N^2 unique numbers.
	# Returns True if so, False otherwise.
	def valid(self):
		validSolution = True
		validNums = set()

		# Iterate through each of the N^2 cells
		for row, col in doubleIter(self.SQUARE_SIZE):
			# Check if there is a valid digit in the cell
			num = self.getValue(row, col)
			if num:
				validNums.add(num)
			else:
				validSolution = False
				break

		# Checks if there are N^2 unique numbers
		if len(validNums) != self.CELL_COUNT:
			validSolution = False

		return validSolution

	# Checks all N^2 cells in the block and returns
	# True if each one has a digit, False otherwise.
	def complete(self):
		allComplete = True

		# Iterate through each of the N^2 cells
		for row, col in doubleIter(self.SQUARE_SIZE):
			# Check if the cell contains a digit
			if not self.getValue(row, col):
				allComplete = False
				break

		return allComplete

	# Returns the assigned value for the cell if one
	# exists; otherwise returns None
	def getValue(self, row, col):
		value = None
		if self.__values[row][col].isdigit():
			value = self.__values[row][col]
		return value

	# Sets the number at position (row, col)
	def setValue(self, num, row, col):
		self.__values[row][col] = num

	##
	# NOTE METHODS BELOW
	# Notes keep track of all the possible numbers that are valid options
	# for a given cell.  As cells across the puzzle are resolved, notes
	# are modified to remove numbers that are no longer possible at the
	# current cell.
	# Notes are represented by a set() of numbers from 1-N^2
	##

	# Returns the notes for the specified (row, col)
	def getNoteNumbers(self, row, col):
		return self.__noteNums[row][col]

	# Deletes a number from a given set of notes at position (row, col)
	def deleteNoteNumber(self, num, row, col):
		self.__noteNums[row][col].discard(num)

	# Deletes all numbers for a set of notes
	def clearNoteNumbers(self, row, col):
		self.__noteNums[row][col] = set()

	##################
	# Static Methods #
	##################

	# Returns a set of numbers from 1-N^2
	@staticmethod
	def numberSet():
		numList = []
		for x in SudokuBlock.cellIdIter():
			numList.append(x)
		return set(numList)

	# Returns a dictionary with keys being numbers 1-N^2 and values as empty lists
	@staticmethod
	def numDictList():
		dictList = {}
		for x in SudokuBlock.cellIdIter():
			dictList[x] = []
		return dictList

	# Iterator that yields numbers 1-squareSize^2
	@staticmethod
	def cellIdIter():
		for x in map(str, range(1, SudokuBlock.CELL_COUNT+1)):
			yield x

	###################
	# Private Methods #
	###################

	# Remove all notes for cells that have been assigned a number
	def __eliminateKnownNumbers(self):
		# Iterate through each of the N^2 cells
		for row, col in doubleIter(self.SQUARE_SIZE):
			# Remove all notes for the cell if it has been assigned a number
			if self.getValue(row, col):
				self.clearNoteNumbers(row, col)

	# Creates new notes for each of the N^2 cells
	def __createNoteNumbers(self):
		# Creates a NxN matrix.  Each cell will have its own set of notes
		self.__noteNums = instantiateMatrix(self.SQUARE_SIZE)

		# Iterate through each of the N^2 cells and assign a new set of notes
		for row, col in doubleIter(self.SQUARE_SIZE):
			self.__noteNums[row][col] = self.numberSet()

	# Make sure the values passed in are in a valid format
	def __validateNumList(self, numList):
		# Make sure the correct number of lists are passed in
		listLen = len(numList)
		if listLen != self.SQUARE_SIZE:
			raise Exception('Invalid number of lists passed to SudokuBlock object.  Must contain %s lists.' % (self.SQUARE_SIZE))

		numCount = 0
		numSet = set()
		for itemList in numList:
			itemLen = len(itemList)
			if itemLen != self.SQUARE_SIZE:
				raise Exception('Invalid number of items passed to SudokuBlock object.  Must contain %s items.' % (self.SQUARE_SIZE))
			for num in itemList:
				if num.isdigit():
					numCount += 1
					numSet.add(num)
		numLen = len(numSet)
		if numLen != numCount:
			raise Exception('Duplicate numbers pre-assigned to SudokuBlock object.')
