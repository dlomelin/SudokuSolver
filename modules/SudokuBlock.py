from SudokuSolver.modules.utilities import instantiateMatrix, doubleIter, numberSet

# Class that represents a NxN sudoku block with N^2 cells
class SudokuBlock(object):
	def __init__(self, numList):
		# Set the values to what the user passed in, which should be a list of lists
		# Ex: [['9', '7', ' '], [' ', ' ', ' '], ['5', '6', '3']]
		self.__storeValues(numList)

		# Store data related to the data that was passed in
		self.__storeSquareData()

		# Make sure the values passed in are in a valid format
		self.__validateNumList()

		# Creates new candidates for each of the N^2 cells
		self.__createCandidateNumbers()

		# Remove all candidates for cells that have been assigned a number
		self.__eliminateKnownNumbers()

	# TODO pull out num list
	#def __repr__(self):
	#	return '%s(%s)' % (self.__class__.__name__)

	def __eq__(self, other):
		return self.__values == other.__values

	##################
	# Public Methods #
	##################

	# Checks if every cell in the block contains a unique number.
	# Returns True if so, False otherwise.
	def valid(self):
		validSolution = True
		validNums = set()

		# Iterate through each of the N^2 cells
		for row, col in doubleIter(self.__squareSize):
			# Check if there is a valid digit in the cell
			num = self.getValue(row, col)
			if num:
				validNums.add(num)
			else:
				validSolution = False
				break

		# Checks if there are N^2 unique numbers
		if len(validNums) != self.__cellCount:
			validSolution = False

		return validSolution

	# Checks if every cell in the block contains a number.
	# Returns True if so, False otherwise.
	def complete(self):
		allComplete = True

		# Iterate through each of the N^2 cells
		for row, col in doubleIter(self.__squareSize):
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
		self.__values[row][col] = str(num)

	##
	# CANDIDATE METHODS BELOW
	# Candidates keep track of all the possible numbers that are valid options
	# for a given cell.  As cells across the puzzle are resolved, candidates
	# are modified to remove numbers that are no longer possible at the
	# current cell.
	# Candidates are represented by a set() of numbers from 1-N^2
	##

	# Returns the notes for the specified (row, col)
	def getCandidates(self, row, col):
		return self.__candidates[row][col]

	# Deletes a number from a given set of notes at position (row, col)
	def deleteCandidateNumber(self, num, row, col):
		self.__candidates[row][col].discard(str(num))

	# Deletes all numbers for a set of notes
	def clearCandidates(self, row, col):
		self.__candidates[row][col] = set()

	###################
	# Private Methods #
	###################

	###### START
	# __init__ methods
	#
	def __storeValues(self, numList):
		self.__values = numList
		for i in range(len(self.__values)):
			for j in range(len(self.__values[i])):
				self.__values[i][j] = str(self.__values[i][j])

	# Stores information related to the size of the input data
	def __storeSquareData(self):
		self.__squareSize = len(self.__values)
		self.__cellCount = self.__squareSize ** 2

	# Make sure the values passed in are in a valid format
	def __validateNumList(self):
		# Make sure the correct number of lists are passed in
		listLen = len(self.__values)
		if listLen != self.__squareSize:
			raise Exception('Invalid number of lists passed to SudokuBlock object.  Must contain %s lists.' % (self.__squareSize))

		numCount = 0
		numSet = set()
		for itemList in self.__values:
			itemLen = len(itemList)
			if itemLen != self.__squareSize:
				raise Exception('Invalid number of items passed to SudokuBlock object.  Must contain %s items.' % (self.__squareSize))
			for num in itemList:
				if num.isdigit():
					numCount += 1
					numSet.add(num)
		numLen = len(numSet)
		if numLen != numCount:
			raise Exception('Duplicate numbers pre-assigned to SudokuBlock object.')

	# Creates new notes for each of the N^2 cells
	def __createCandidateNumbers(self):
		# Creates a NxN matrix.  Each cell will have its own set of notes
		self.__candidates = instantiateMatrix(self.__squareSize)

		# Iterate through each of the N^2 cells and assign a new set of notes
		for row, col in doubleIter(self.__squareSize):
			self.__candidates[row][col] = numberSet(self.__squareSize)

	# Remove all notes for cells that have been assigned a number
	def __eliminateKnownNumbers(self):
		# Iterate through each of the N^2 cells
		for row, col in doubleIter(self.__squareSize):
			# Remove all notes for the cell if it has been assigned a number
			if self.getValue(row, col):
				self.clearCandidates(row, col)
	#
	# __init__ methods
	###### END

