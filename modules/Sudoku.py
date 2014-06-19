import os, sys, time
from itertools import combinations, chain

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

		self.__techniquesUsed = {}

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

		#startTime = time.clock()

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
			self.__reduceMultipleLines()

			if not self.__puzzleChanged():
				break

		# If puzzle was complete, make sure the blocks, rows, and columns
		# all adhere to a valid sudoku solution.
		if self.complete():
			self.__checkValid()

		#totalTime = time.clock() - startTime
		#print 'Total Time: %s' % (totalTime)

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

	# Prints the current candidates used to solve the puzzle in a human readable format
	def printCandidates(self, fhOut = sys.stdout):
		candidateNums = [['1','2','3'], ['4','5','6'], ['7','8','9']]

		header = 'Current Candidates'.center(len(self.__blockRowSplit()))

		fhOut.write('%s\n' % (header))
		for blockRow in range(3):
			if blockRow == 0:
				fhOut.write('%s\n' % (self.__blockRowSplit()))
			for row in range(3):
				for i in range(len(candidateNums)):
					fhOut.write('||')
					for blockCol in range(3):
						for col in range(3):
							numString = ''
							candidates = self.getCellCandidates(blockRow, blockCol, row, col)
							for num in candidateNums[i]:
								if num in candidates:
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

	# Prints out a list of techniques used and how frequently they were used
	def printTechniquesUsed(self, fhOut = sys.stdout):
		fhOut.write('Candidates Removed By:\n')
		for technique in sorted(self.__techniquesUsed.keys()):
			fhOut.write('  %s: %s\n' % (technique, self.__techniquesUsed[technique]))
		fhOut.write('\n')

	# Returns the value of a cell at the specified coordinates
	def getCellValue(self, blockRow, blockCol, row, col):
		return self.__matrix[blockRow][blockCol].getValue(row, col)

	# Returns the set() of candidates at the specified coordinates
	def getCellCandidates(self, blockRow, blockCol, row, col):
		return self.__matrix[blockRow][blockCol].getCandidates(row, col)

	###################
	# Private Methods #
	###################

	###### START
	# Instance variable setters and getters
	#
	def __puzzleChanged(self):
		return self.__changeStatus

	# Lets the solver know changes were made
	def __setChangeTrue(self, techniqueUsed):
		self.__changeStatus = True
		self.__trackTechniquesUsed(techniqueUsed)

	def __setChangeFalse(self):
		self.__changeStatus = False

	def __puzzleSolved(self):
		return self.__solvedStatus

	def __setSolvedFalse(self):
		self.__solvedStatus = False

	def __trackTechniquesUsed(self, technique):
		if technique:
			try:
				self.__techniquesUsed[technique] += 1
			except:
				self.__techniquesUsed[technique] = 1
	#
	# instance variable setters and getters
	###### END

	###### START
	# Wrappers around SudokuBlock methods
	#
	def __deleteCandidateNumber(self, num, blockRow, blockCol, row, col):
		self.__matrix[blockRow][blockCol].deleteCandidateNumber(num, row, col)

	# Sets the value of the specified cell
	def __setCellValue(self, num, blockRow, blockCol, row, col):
		self.__matrix[blockRow][blockCol].setValue(num, row, col)

	# Clears out available candidates from the specified cell
	def __clearCellCandidates(self, blockRow, blockCol, row, col):
		self.__matrix[blockRow][blockCol].clearCandidates(row, col)

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
	# Sets the value of the specified cell and adjusts the candidates in the
	# necessary row, column, and block.
	def __setValue(self, num, blockRow, blockCol, row, col, techniqueUsed = None):
		# Sets the value of the specified cell
		self.__setCellValue(num, blockRow, blockCol, row, col)

		# Clears out available candidates from the specified cell
		self.__clearCellCandidates(blockRow, blockCol, row, col)

		# Clears out available candidates from the affected block, row, and column
		self.__removeCandidateSeenBy(num, blockRow, blockCol, row, col)

		# Let the solver know changes were made
		self.__setChangeTrue(techniqueUsed)

	# Deletes the specified number from the cell's candidates.  If there is only
	# one number left in the candidates, then it sets the value
	def __clearCellCandidateAndSet(self, num, blockRow, blockCol, row, col, techniqueUsed):

		candidates = self.getCellCandidates(blockRow, blockCol, row, col)
		if num in candidates:
			self.__deleteCandidateNumber(num, blockRow, blockCol, row, col)

			nums = list(candidates)
			if len(nums) == 1:
				self.__setValue(
					nums[0],
					blockRow,
					blockCol,
					row,
					col,
					techniqueUsed,
				)
			else:
				# Let the solver know changes were made
				self.__setChangeTrue(techniqueUsed)

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

	# Clears out available candidates from the affected block, row, and column
	def __removeCandidateSeenBy(self, num, blockRow, blockCol, row, col):

		# Remove the number from the candidates along the block
		self.__removeCandidateByIter(
			num,
			self.__blockCellCoordsIter,
			blockRow,
			blockCol,
			[],
		)

		# Remove the number from the candidates along the row
		self.__removeCandidateByIter(
			num,
			self.__rowCellCoordsIter,
			blockRow,
			row,
			[],
		)

		# Remove the number from the candidates along the column
		self.__removeCandidateByIter(
			num,
			self.__colCellCoordsIter,
			blockCol,
			col,
			[],
		)

	# Goes through each cell passed from the iterator and removes the number from the cell's candidates
	def __removeCandidateByIter(self, num, coordIter, coordPos1, coordPos2, skipCoordsList, technique = None):
		# Iterate through each cell
		for coords in coordIter(coordPos1, coordPos2):

			# Skip the cells that are the skip list
			if not(self.__coordsInList(coords, skipCoordsList)):
				# Remove the numbers from the cell candidates
				self.__clearCellCandidateAndSet(
					num,
					coords.blockRow,
					coords.blockCol,
					coords.row,
					coords.col,
					technique,
				)

	def __coordsInList(self, coords, skipList):
		itemInList = False
		for item in skipList:
			if item == coords:
				itemInList = True
				break
		return itemInList

	def __coordsIntersection(self, *coordsList):
		seenCoordsList = []
		for coords in coordsList:
			sharedCoords = self.__coordsSeenBy(coords)
			seenCoordsList.append(sharedCoords)

		intersectingCoords = seenCoordsList[0]
		for i in range(1, len(seenCoordsList)):
			intersectingCoords = intersectingCoords.intersection(seenCoordsList[i])

		return intersectingCoords

	# Returns a set of all coordinates that are in the same block, row, and column as the input coordinates
	def __coordsSeenBy(self, centerCoord):
		uniqueCoords = set()

		# Store all coordinates in the same block as centerCoord
		for coord in self.__blockCellCoordsIter(centerCoord.blockRow, centerCoord.blockCol):
			uniqueCoords.add(coord)

		# Store all coordinates in the same row as centerCoord
		for coord in self.__rowCellCoordsIter(centerCoord.blockRow, centerCoord.row):
			uniqueCoords.add(coord)

		# Store all coordinates in the same column as centerCoord
		for coord in self.__colCellCoordsIter(centerCoord.blockCol, centerCoord.col):
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
			cellCandidates = self.getCellCandidates(
				cellCoords.blockRow,
				cellCoords.blockCol,
				cellCoords.row,
				cellCoords.col,
			)
			if validCellFunction(pivotCellCandidates, cellCandidates):
				coordsList.append(cellCoords)
				candidatesList.append(cellCandidates)

		return coordsList, candidatesList

	def __candidatesIntersection(self, *candidatesList):
		candidatesIntersection = candidatesList[0]
		for i in range(1, len(candidatesList)):
			candidatesIntersection = candidatesIntersection.intersection(candidatesList[i])

		return candidatesIntersection

	def __candidatesUnion(self, *candidatesList):
		candidatesUnion = candidatesList[0]
		for i in range(1, len(candidatesList)):
			candidatesUnion = candidatesUnion.union(candidatesList[i])

		return candidatesUnion
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

		# Adjusts the candidates based on the initial values of the sudoku grid.
		self.__clearInitialCandidates()

	# Adjusts the candidates based on the initial values of the sudoku grid.
	def __clearInitialCandidates(self):

		# Iterate through each block in the sudoku grid
		for cellCoordinatesList in self.__blockCoordsIter():

			# Iterate through each cell's coordinates
			for cellCoords in cellCoordinatesList:

				# If the cell has a number assigned, then clear the block, row, and column candidates
				num = self.getCellValue(
					cellCoords.blockRow,
					cellCoords.blockCol,
					cellCoords.row,
					cellCoords.col,
				)
				if num:
					# Clears out available candidates from the affected block, row, and column
					self.__removeCandidateSeenBy(
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
	# printCandidates methods
	#
	def __rowSplit(self):
		return '-----------------------------------------------------------'

	def __blockRowSplit(self):
		return '==========================================================='
	#
	# printCandidates methods
	###### END

	###### START
	# __setSingletons methods
	#
	def __setSingletons(self):
		# Assign singletons within rows
		self.__setSingletonCandidates(self.__rowCoordsIter)

		# Assign singletons within columns
		self.__setSingletonCandidates(self.__columnCoordsIter)

	def __setSingletonCandidates(self, coordIter):

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
						candidates = self.getCellCandidates(cellCoords.blockRow, cellCoords.blockCol, cellCoords.row, cellCoords.col)
						# Keep track of how many positions will allow the current value
						if currentValue in candidates:
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
		technique = 'Candidate Lines'

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

					# Candidate line lies along a row, therefore remove number from the rest of the row
					if coords1.alignsByRow(coords2):
						# Remove the number from the candidates along the row
						self.__removeCandidateByIter(
							num,
							self.__rowCellCoordsIter,
							coords1.blockRow,
							coords1.row,
							[coords1, coords2],
							technique,
						)

					# Candidate line lies along a column, therefore remove number from the rest of the column
					elif coords1.alignsByCol(coords2):
						# Remove the number from the candidates along the column
						self.__removeCandidateByIter(
							num,
							self.__colCellCoordsIter,
							coords1.blockCol,
							coords1.col,
							[coords1, coords2],
							technique,
						)

	# Stores the coordinates for all hint positions
	def __generateHintCoords(self, cellCoordinatesList):
		hintCoords = numDictList(3)

		# Iterate through each cell's coordinates
		for cellCoords in cellCoordinatesList:
			# Store the coordinates where all numbers are found
			candidates = self.getCellCandidates(
				cellCoords.blockRow,
				cellCoords.blockCol,
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
		for cellCount in range(2, 5):
			# Search for valid xwing cells along rows to reduce candidates along the columns
			self.__reduceXwingSwordJellyRow(cellCount)

			# Search for valid xwing cells along columns to reduce candidates along the rows
			self.__reduceXwingSwordJellyCol(cellCount)

	def __reduceXwingSwordJellyRow(self, cellCount):
		technique = self.__xSwordJellyTechnique(cellCount)
		potentialCells = self.__potentialRectangleCells(cellCount, self.__rowCoordsIter)

		# Iterate through each number
		for num in potentialCells:

			# Iterate through all possible row triplets
			for dataset in combinations(potentialCells[num], cellCount):

				# Checks if the current triplet of rows forms a valid Swordfish across 3 columns
				if self.__validRectangleColCells(cellCount, *dataset):

					# Iterate through the 3 affected columns
					for blockCoords in self.__columnsInCommon(*dataset):

						# Remove the number from the candidates along the column, excluding the cells
						# that make up the Swordfish
						self.__removeCandidateByIter(
							num,
							self.__colCellCoordsIter,
							blockCoords.blockCol,
							blockCoords.col,
							list(chain(*dataset)),
							technique,
						)

	def __reduceXwingSwordJellyCol(self, cellCount):
		technique = self.__xSwordJellyTechnique(cellCount)

		potentialCells = self.__potentialRectangleCells(cellCount, self.__columnCoordsIter)

		# Iterate through each number
		for num in potentialCells:

			# Iterate through all possible cellCount cells
			for dataset in combinations(potentialCells[num], cellCount):

				# Checks if the current triplet of rows forms a valid Swordfish across 3 rows
				if self.__validRectangleRowCells(cellCount, *dataset):

					# Iterate through the 3 affected rows
					for blockCoords in self.__rowsInCommon(*dataset):

						# Remove the number from the candidates along the row, excluding the cells
						# that make up the Swordfish
						self.__removeCandidateByIter(
							num,
							self.__rowCellCoordsIter,
							blockCoords.blockRow,
							blockCoords.row,
							list(chain(*dataset)),
							technique,
						)

	def __validRectangleRowCells(self, cellCount, *dataList):

		rowData = DictCounter()
		completeDataLists = True

		for data in dataList:
			if not data:
				completeDataLists = False
			for coords in data:
				row = '%s,%s' % (coords.blockRow, coords.row)
				rowData.add(row)

		return rowData.keyCount() == cellCount and rowData.countsGE(2) and completeDataLists

	def __validRectangleColCells(self, cellCount, *dataList):

		colData = DictCounter()
		completeDataLists = True

		for data in dataList:
			if not data:
				completeDataLists = False
			for coords in data:
				col = '%s,%s' % (coords.blockCol, coords.col)
				colData.add(col)

		return colData.keyCount() == cellCount and colData.countsGE(2) and completeDataLists

	def __rowsInCommon(self, *dataList):
		rowSet = set()

		for data in dataList:
			for coords in data:
				rowSet.add(SudokuCoordinates(coords.blockRow, 0, coords.row, 0))

		return rowSet

	def __columnsInCommon(self, *dataList):
		colSet = set()

		for data in dataList:
			for coords in data:
				colSet.add(SudokuCoordinates(0, coords.blockCol, 0, coords.col))

		return colSet

	# Search all rows/columns for cells that have between 2 and cellCount candidates
	# cellCount is dependent on the technique.  This method is used in the xwing,
	# swordfish, jellyfish type puzzles
	def __potentialRectangleCells(self, cellCount, coordIter):

		potentialCells = numDictList(3)

		# Iterate through each row/cell in the sudoku grid
		for cellCoordinatesList in coordIter():
			hintCoords = numDictList(3)

			# Iterate through each cell's coordinates
			for cellCoords in cellCoordinatesList:

				# Loop through all candidates in the current cell
				candidates = self.getCellCandidates(
					cellCoords.blockRow,
					cellCoords.blockCol,
					cellCoords.row,
					cellCoords.col,
				)
				for num in candidates:
					# Store the current coordinates
					hintCoords[num].append(cellCoords)

			# Keep only the cells that have between 2 and cellCount candidates left in the row/column
			for num in hintCoords:
				if 2 <= len(hintCoords[num]) <= cellCount:
					potentialCells[num].append(hintCoords[num])

		return potentialCells

	def __xSwordJellyTechnique(self, cellCount):
		techniques = {
			2: 'X-Wing',
			3: 'Sword-Fish',
			4: 'Jelly-Fish',
		}
		try:
			return techniques[cellCount]
		except:
			raise Exception('Invalid  size used: %s.  Please modify code' % (cellCount))
	#
	# __reduceXwingSwordfishJellyfish methods
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
			candidateCoords = []
			candidateList = []

			# Iterate through each cell's coordinates
			for cellCoords in cellCoordinatesList:

				# Store the cell's coordinates and candidates
				candidates = self.getCellCandidates(
					cellCoords.blockRow,
					cellCoords.blockCol,
					cellCoords.row,
					cellCoords.col,
				)
				if candidates:
					candidateCoords.append(cellCoords)
					candidateList.append(candidates)

			# setSize determines the naked set size, 2 = naked pairs, 3 = naked trios, 4 = naked quads
			for setSize in range(2, 5):

				# Looks for naked sets in the current set of cells
				self.__findNakedSetCombinations(setSize, candidateList, candidateCoords, cellCoordinatesList)

	# Finds all valid naked sets.  If any are found, remove the numbers that are found in the naked
	# sets from all remaining neighboring cells.
	def __findNakedSetCombinations(self, setSize, candidateList, candidateCoords, cellCoordinatesList):
		technique = self.__nakedSetTechnique(setSize)

		# Generates a list with all combinations of size setSize.
		# If candidateList = [0, 1, 2] and setSize = 2, then 3 indexLists would be created
		# [0, 1], [0, 2], [1, 2]
		for indexList in combinations(range(len(candidateList)), setSize):

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
					for coords in cellCoordinatesList:

						# Skip the cells that are in the skip list (cells that made up the naked set)
						if not(self.__coordsInList(coords, skipCoordsList)):

							# Remove the numbers from the cell candidates
							self.__clearCellCandidateAndSet(
								num,
								coords.blockRow,
								coords.blockCol,
								coords.row,
								coords.col,
								technique,
							)

	# Generate a set of the unique candidates in candidateList
	def __combineCandidates(self, setList, coords):
		uniqueCandidates = set()
		for indexNum in coords:
			for num in list(setList[indexNum]):
				uniqueCandidates.add(num)
		return uniqueCandidates

	# Returns the technique name for a given setSize
	def __nakedSetTechnique(self, setSize):
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
		for cellCoordinatesList in self.__rowCoordsIter():

			# Iterate through each cell's coordinates
			for cellCoords in cellCoordinatesList:

				# Perform Y wing technique
				self.__findPotentialYwing(cellCoords)

	# Performs the Y wing technique
	def __findPotentialYwing(self, coords):
		technique = 'Y-Wing'

		# Look for a pivot cell that has 2 unknown candidates
		pivotCellCandidates = self.getCellCandidates(
			coords.blockRow,
			coords.blockCol,
			coords.row,
			coords.col,
		)

		# Y wing requires the pivot cell to contain exactly 2 candidates
		if len(pivotCellCandidates) == 2:

			# Get a list of coordinates and candidates seen by the current cell
			coordsList, candidatesList = self.__validCellsSeenBy(coords, pivotCellCandidates, self.__validYCell)

			# Iterate through all pairs of cells
			for indexList in combinations(range(len(coordsList)), 2):

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
								rCoords.blockRow,
								rCoords.blockCol,
								rCoords.row,
								rCoords.col,
								technique,
							)

	# Looks for a cell that has 2 candidate numbers and shares exactly 1 candidate between itself and the pivot cell
	def __validYCell(self, pivotCellCandidates, cellCandidates):
		return len(cellCandidates) == 2 and len(cellCandidates.intersection(pivotCellCandidates)) == 1
	#
	# __reduceYwing methods
	###### END

	###### START
	# __reduceXYZwing methods
	#
	def __reduceXYZwing(self):

		# Iterate through each row in the sudoku grid
		for cellCoordinatesList in self.__rowCoordsIter():

			# Iterate through each cell's coordinates
			for cellCoords in cellCoordinatesList:

				# Perform XYZ wing technique
				self.__findPotentialXYZwing(cellCoords)

	def __findPotentialXYZwing(self, coords):
		technique = 'XYZ-Wing'

		# Look for a pivot point that has 3 unknown candidates
		pivotCellCandidates = self.getCellCandidates(
			coords.blockRow,
			coords.blockCol,
			coords.row,
			coords.col,
		)

		# XYZ wing requires the pivot cell to contain exactly 3 candidates
		if len(pivotCellCandidates) == 3:

			# Get a list of coordinates and candidates seen by the current cell
			coordsList, candidatesList = self.__validCellsSeenBy(coords, pivotCellCandidates, self.__validXYZCell)

			# Iterate through all pairs of cells
			for indexList in combinations(range(len(coordsList)), 2):

				# Union between each pair
				candidatesUnion = self.__candidatesUnion(
					candidatesList[indexList[0]],
					candidatesList[indexList[1]],
				)

				if len(candidatesUnion) == 3:
					commonSet = self.__candidatesIntersection(candidatesList[indexList[0]], candidatesList[indexList[1]])
					removeNum = commonSet.pop()

					removeCoords = self.__coordsIntersection(
						coords,
						coordsList[indexList[0]],
						coordsList[indexList[1]],
					)

					for rCoords in removeCoords:
						self.__clearCellCandidateAndSet(
							removeNum,
							rCoords.blockRow,
							rCoords.blockCol,
							rCoords.row,
							rCoords.col,
							technique,
						)

	# Look for cells that have 2 unknown candidates that are all found
	# within the pivot cell
	def __validXYZCell(self, pivotCellCandidates, cellCandidates):
		return len(cellCandidates) == 2 and cellCandidates.issubset(pivotCellCandidates)
	#
	# __reduceXYZwing methods
	###### END

	###### START
	# __reduceWXYZwing methods
	#
	def __reduceWXYZwing(self):

		# Iterate through each row in the sudoku grid
		for cellCoordinatesList in self.__rowCoordsIter():

			# Iterate through each cell's coordinates
			for cellCoords in cellCoordinatesList:

				# Perform WXYZ wing technique
				self.__findPotentialWXYZwing(cellCoords)

	def __findPotentialWXYZwing(self, coords):
		technique = 'WXYZ-Wing'

		pivotCellCandidates = self.getCellCandidates(
			coords.blockRow,
			coords.blockCol,
			coords.row,
			coords.col,
		)

		# Get a list of coordinates and candidates seen by the current cell
		coordsList, candidatesList = self.__validCellsSeenBy(coords, pivotCellCandidates, self.__validWXYZCell)

		# Iterate through all pairs of cells
		for indexList in combinations(range(len(coordsList)), 3):

			candidatesUnion = self.__candidatesUnion(
				pivotCellCandidates,
				candidatesList[indexList[0]],
				candidatesList[indexList[1]],
				candidatesList[indexList[2]],
			)

			if len(candidatesUnion) == 4:
				removeNum = self.__findNonRestrictedCandidate(
					[candidatesList[indexList[0]], candidatesList[indexList[1]], candidatesList[indexList[2]]],
					[coordsList[indexList[0]], coordsList[indexList[1]], coordsList[indexList[2]]],
				)

				if not removeNum is None:

					coordsForIntersection = []
					if removeNum in pivotCellCandidates:
						coordsForIntersection.append(coords)
					for i in range(3):
						if removeNum in candidatesList[indexList[i]]:
							coordsForIntersection.append(coordsList[indexList[i]])

					removeCoords = self.__coordsIntersection(*coordsForIntersection)

					for rCoords in removeCoords:
						self.__clearCellCandidateAndSet(
							removeNum,
							rCoords.blockRow,
							rCoords.blockCol,
							rCoords.row,
							rCoords.col,
							technique,
						)

	def __findNonRestrictedCandidate(self, candidatesList, coordsList):
		candidateSet = set()

		# Iterate through each pair of cells
		for indexList in combinations(range(len(coordsList)), 2):

			# Look for cells that can't see each other
			if not coordsList[indexList[0]].alignsByRow(coordsList[indexList[1]]) and \
				not coordsList[indexList[0]].alignsByCol(coordsList[indexList[1]]) and \
				not coordsList[indexList[0]].alignsByBlock(coordsList[indexList[1]]):

				# Look for the numbers shared in common between both cells
				intersectionSet = candidatesList[indexList[0]].intersection(candidatesList[indexList[1]])
				candidateSet = candidateSet.union(intersectionSet)

		if len(candidateSet) == 1:
			return candidateSet.pop()
		else:
			return None

	# Look for cells that have candidates and at least 1 number in common
	def __validWXYZCell(self, pivotCellCandidates, cellCandidates):
		return len(cellCandidates) >= 2 and len(cellCandidates.intersection(pivotCellCandidates)) >= 1
	#
	# __reduceWXYZwing methods
	###### END

	###### START
	# __reduceMultipleLines methods
	#
	def __reduceMultipleLines(self):
		technique = 'Multiple Lines'
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

				# Identify the rows in the current block that can have the number eliminated from the candidates
				sharedRows = self.__findSharedLinesByRow(num, blockRow, blockCol)
				if sharedRows:

					# Remove the number from the cell's candidates
					for row in sharedRows:
						for col in range(3):
							self.__clearCellCandidateAndSet(
								num,
								blockRow,
								blockCol,
								row,
								col,
								technique,
							)

				# Identify the columns in the current block that can have the number eliminated from the candidates
				sharedCols = self.__findSharedLinesByCol(num, blockRow, blockCol)
				if sharedCols:

					# Remove the number from the cell's candidates
					for col in sharedCols:
						for row in range(3):
							self.__clearCellCandidateAndSet(
								num,
								blockRow,
								blockCol,
								row,
								col,
								technique,
							)

	# Identify the rows in the current block that can have the number eliminated from the candidates
	def __findSharedLinesByRow(self, num, blockRow, blockCol):
		sharedRows = set()
		affectedBlocks = set()

		# Iterate through the remaining columns except for the starting one
		for blockColLoop in filter(lambda x: x != blockCol, range(3)):

			# Iterate through each cell in the block
			for row, col in doubleIter(3):

				# Check the cell's candidates if num can be placed here.  If it can, track the row and block
				candidates = self.getCellCandidates(blockRow, blockColLoop, row, col)
				if num in candidates:
					sharedRows.add(row)
					affectedBlocks.add(blockColLoop)

		# Criteria for the multiple lines technique is that there are 2 shared rows
		# across 2 blocks with the same number.
		if len(sharedRows) == 2 and len(affectedBlocks) == 2:
			return sharedRows
		else:
			return set()

	# Identify the columns in the current block that can have the number eliminated from the candidates
	def __findSharedLinesByCol(self, num, blockRow, blockCol):
		sharedCols = set()
		affectedBlocks = set()

		# Iterate through the remaining rows except for the starting one
		for blockRowLoop in filter(lambda x: x != blockRow, range(3)):

			# Iterate through each cell in the block
			for row, col in doubleIter(3):

				# Check the cell's candidates if num can be placed here.  If it can, track the column and block
				candidates = self.getCellCandidates(blockRowLoop, blockCol, row, col)
				if num in candidates:
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

class DictCounter(object):
	def __init__(self):
		self.__counts = {}

	def countsGE(self, size):
		status = True
		for key in self.__counts.keys():
			if self.__counts[key] < size:
				status = False
				break
		return status

	def add(self, key):
		try:
			self.__counts[key] += 1
		except:
			self.__counts[key] = 1

	def keyCount(self):
		return len(self.__counts)
