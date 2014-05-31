import os, sys

from SudokuSolver.modules.utilities import instantiateMatrix, doubleIter, numberSet, numDictList
from SudokuSolver.modules.SudokuBlock import SudokuBlock

# TODO
# unittest for Sudoku class
# Modularize reduce methods into their own classes?
# work on __reduceMultipleLines() http://www.sudokuoftheday.com/pages/techniques-5.php
# Remove hardcoded square size 3 and pass argument to SudokuBlock (test size 2?)

class Sudoku(object):
	def __init__(self, **args):

		# Make sure one of the required arguments was passed in
		fieldsToCheck = set(['file', 'data'])
		self.__checkInputParameters(fieldsToCheck, args)

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

	def gridValues(self):
		values = []

		for matRow, row in doubleIter(3):
			values.append([])
			for matCol, col in doubleIter(3):
				num = self.value(matRow, matCol, row, col)
				if not num:
					num = '.'

				values[-1].append(num)

		return values

	def solve(self):
		# Mark this puzzle as unsolved
		self.__setSolvedFalse()

		while True:
			# Mark this as a new iteration without changes
			# Any modifications to the puzzle will mark the puzzle as changed
			# otherwise the loop will quit
			self.__setChangeFalse()

			# Assign numbers based on a row or column requiring all 9 numbers
			self.__assignUnitSum()

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

		# If puzzle was complete, validate the blocks, rows, and columns all have unique numbers.
		# Otherwise, if the puzzle could not be solved, print out the notes for each block
		if self.complete():
			self.checkValid()
		else:
			self.printNotes()

	def checkValid(self):
		self.__checkValidBlocks()
		self.__checkValidRows()
		self.__checkValidCols()
		self.__setSolvedTrue()

	# Checks if every cell has been filled in with a number.
	# Does not check if the numbers are valid though.
	def complete(self):
		allComplete = True

		# Iterate through each of the 9 blocks
		for blockRow, blockCol in doubleIter(3):
			# Check if the block is complete
			if not self.__matrix[blockRow][blockCol].complete():
				allComplete = False
				break

		return allComplete

	def printNotes(self, fhOut = sys.stdout):
		noteSets = [['1','2','3'], ['4','5','6'], ['7','8','9']]
		for blockRow in range(3):
			if blockRow == 0:
				fhOut.write('%s\n' % (self.__blockRowSplit()))
			for row in range(3):
				for i in range(len(noteSets)):
					fhOut.write('||')
					for blockCol in range(3):
						for col in range(3):
							numString = ''
							noteNums = self.__matrix[blockRow][blockCol].getNoteNumbers(row, col)
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

	def value(self, blockRow, blockCol, row, col):
		return self.__matrix[blockRow][blockCol].getValue(row, col)

	###################
	# Private Methods #
	###################

	def __checkInputParameters(self, fieldsToCheck, args):
		# Check if one of the required parameters was supplied
		missingFields = True
		for field in args:
			if field in fieldsToCheck:
				missingFields = False

		if missingFields:
			raise Exception('One of the following required fields was not provided: %s' % (','.join(fieldsToCheck)))

	def __loadInputData(self, args):
		if 'file' in args:
			# Parses file with starting Sudoku numbers and loads object
			self.__loadFromFile(args['file'])
		elif 'data' in args:
			# Parses list of lists with starting Sudoku numbers and loads object
			self.__loadFromData(args['data'])

	def __rowSplit(self):
		return '-----------------------------------------------------------'
	def __blockRowSplit(self):
		return '==========================================================='

	def __reduceNakedSets(self):
		self.__reduceNakedSetRow()
		self.__reduceNakedSetCol()
		self.__reduceNakedSetBlock()

	def __reduceMultipleLines(self):
		pass

	def __reduceNakedSetRow(self):
		allCoordinates = self.__rowCoordinates()
		self.__findNakedSets(allCoordinates)

	def __reduceNakedSetCol(self):
		allCoordinates = self.__colCoordinates()
		self.__findNakedSets(allCoordinates)

	def __reduceNakedSetBlock(self):
		allCoordinates = self.__blockCoordinates()
		self.__findNakedSets(allCoordinates)

	def __findNakedSets(self, allCoordinates):

		for coordinates in allCoordinates:
			noteCoords = []
			noteList = []
			for unitCoords in coordinates:
				blockRow = unitCoords[0]
				blockCol = unitCoords[1]
				row = unitCoords[2]
				col = unitCoords[3]

				noteNums = self.__matrix[blockRow][blockCol].getNoteNumbers(row, col)
				if noteNums:
					noteCoords.append((blockRow, blockCol, row, col))
					noteList.append(noteNums)

			noteLen = len(noteList)
			if noteLen >= 5:
				self.__findNakedPairs(noteList, noteCoords, noteLen, coordinates)
				self.__findNakedTrios(noteList, noteCoords, noteLen, coordinates)
				self.__findNakedQuads(noteList, noteCoords, noteLen, coordinates)
			elif noteLen <= 4:
				self.__findNakedPairs(noteList, noteCoords, noteLen, coordinates)
				self.__findNakedTrios(noteList, noteCoords, noteLen, coordinates)
			elif noteLen <= 3:
				self.__findNakedPairs(noteList, noteCoords, noteLen, coordinates)

	def __findNakedPairs(self, noteList, noteCoords, noteLen, coordinates):
		for i in range(noteLen - 1):
			for j in range(i + 1, noteLen):
				uniqueNums = self.__combineNotes(noteList, [i, j])
				if len(uniqueNums) == 2:
					self.__removeNakedSetNotes(uniqueNums, coordinates, noteCoords, [i, j])

	def __findNakedTrios(self, noteList, noteCoords, noteLen, coordinates):
		for i in range(noteLen - 2):
			for j in range(i + 1, noteLen - 1):
				for k in range(j + 1, noteLen):
					uniqueNums = self.__combineNotes(noteList, [i, j, k])
					if len(uniqueNums) == 3:
						self.__removeNakedSetNotes(uniqueNums, coordinates, noteCoords, [i, j, k])

	def __findNakedQuads(self, noteList, noteCoords, noteLen, coordinates):
		for i in range(noteLen - 3):
			for j in range(i + 1, noteLen - 2):
				for k in range(j + 1, noteLen - 1):
					for l in range(k + 1, noteLen):
						uniqueNums = self.__combineNotes(noteList, [i, j, k, l])
						if len(uniqueNums) == 4:
							self.__removeNakedSetNotes(uniqueNums, coordinates, noteCoords, [i, j, k, l])

	def __combineNotes(self, setList, coords):
		uniqueNums = {}
		for indexNum in coords:
			for num in list(setList[indexNum]):
				uniqueNums[num] = True
		return uniqueNums

	def __removeNakedSetNotes(self, removeNums, coordinates, skipCoords, skipCoordsIndex):
		for unitCoords in coordinates:
			blockRow = unitCoords[0]
			blockCol = unitCoords[1]
			row = unitCoords[2]
			col = unitCoords[3]

			if not self.__skipCoords(skipCoords, skipCoordsIndex, blockRow, blockCol, row, col):
				for num in removeNums.keys():
					self.__removeNumber(num, blockRow, blockCol, row, col)

	def __skipCoords(self, skipCoords, skipIndex, blockRow, blockCol, row, col):
		skip = False
		for i in skipIndex:
			testBlockRow = skipCoords[i][0]
			testBlockCol = skipCoords[i][1]
			testRow = skipCoords[i][2]
			testCol = skipCoords[i][3]
			if testBlockRow == blockRow and testBlockCol == blockCol and testRow == row and testCol == col:
				skip = True
		return skip

	def __rowCoordinates(self):
		coordinates = []
		for blockRow, row in doubleIter(3):
			rowCoords = []
			for blockCol, col in doubleIter(3):
				rowCoords.append((blockRow, blockCol, row, col))
			coordinates.append(rowCoords)
		return coordinates

	def __colCoordinates(self):
		coordinates = []
		for blockCol, col in doubleIter(3):
			colCoords = []
			for blockRow, row in doubleIter(3):
				colCoords.append((blockRow, blockCol, row, col))
			coordinates.append(colCoords)
		return coordinates

	def __blockCoordinates(self):
		coordinates = []
		for blockRow, blockCol in doubleIter(3):
			blockCoords = []
			for row, col in doubleIter(3):
				blockCoords.append((blockRow, blockCol, row, col))
			coordinates.append(blockCoords)
		return coordinates

	def __reduceXwing(self):
		self.__reduceXwingRow()
		self.__reduceXwingCol()

	def __removeNumber(self, num, blockRow, blockCol, row, col):

		noteNums = self.__matrix[blockRow][blockCol].getNoteNumbers(row, col)
		if num in noteNums:
			self.__matrix[blockRow][blockCol].deleteNoteNumber(num, row, col)

			nums = list(noteNums)
			if len(nums) == 1:
				self.__setValue(nums[0], blockRow, blockCol, row, col)
			self.__setChangeTrue()

	def __skip(self, blockRow, row, blockRowSkip, rowSkip):
		if blockRow == blockRowSkip and row == rowSkip:
			return True
		else:
			return False

	def __reduceCandidateLines(self):

		allCoordinates = self.__blockCoordinates()

		for coordinates in allCoordinates:
			hintCoords = self.__generateHintCoords(coordinates)
			blockRow = coordinates[0][0]
			blockCol = coordinates[0][1]

			for num in hintCoords:
				if len(hintCoords[num]) == 2:
					# Candidate line lies along a row, therefore remove from every blockColum on the same row
					if hintCoords[num][0][0] == hintCoords[num][1][0]:
						for testBlockCol in range(3):
							if testBlockCol == blockCol:
								continue
							for unitCol in range(3):
								self.__removeNumber(num, blockRow, testBlockCol, hintCoords[num][0][0], unitCol)
					# Candidate line lies along a column, therefore remove from every blockRow on the same column
					elif hintCoords[num][0][1] == hintCoords[num][1][1]:
						for testBlockRow in range(3):
							if testBlockRow == blockRow:
								continue
							for unitRow in range(3):
								self.__removeNumber(num, testBlockRow, blockCol, unitRow, hintCoords[num][0][1])

	def __generateHintCoords(self, coordinates):
		hintCoords = numDictList(3)

		for unitCoords in coordinates:
			blockRow = unitCoords[0]
			blockCol = unitCoords[1]
			row = unitCoords[2]
			col = unitCoords[3]

			noteNums = self.__matrix[blockRow][blockCol].getNoteNumbers(row, col)
			for num in noteNums:
				hintCoords[num].append((row, col))

		return hintCoords

	def __assignUnitSum(self):
		self.__assignRowSum()
		self.__assignColSum()

	def __assignRowSum(self):
		allCoordinates = self.__rowCoordinates()
		self.__assignSumNumbers(allCoordinates)

	def __assignColSum(self):
		allCoordinates = self.__colCoordinates()
		self.__assignSumNumbers(allCoordinates)

	def __assignSumNumbers(self, allCoordinates):
		for coordinates in allCoordinates:
			# Generate list of numbers that can fill out the remaining empty squares
			requiredNums = numberSet(3)
			for unitCoords in coordinates:
				blockRow = unitCoords[0]
				blockCol = unitCoords[1]
				row = unitCoords[2]
				col = unitCoords[3]

				self.__removeReqNum(requiredNums, blockRow, blockCol, row, col)

			for reqNum in requiredNums:
				# Check if there is only 1 position that can fill that number
				posCount = 0
				posBlockRow = None
				posBlockCol = None
				posRow = None
				posCol = None
				for unitCoords in coordinates:
					blockRow = unitCoords[0]
					blockCol = unitCoords[1]
					row = unitCoords[2]
					col = unitCoords[3]

					# If that position was already assigned a number then skip it
					if not self.value(blockRow, blockCol, row, col):
						noteNums = self.__matrix[blockRow][blockCol].getNoteNumbers(row, col)
						if reqNum in noteNums:
							posCount += 1
							posBlockRow = blockRow
							posBlockCol = blockCol
							posRow = row
							posCol = col

				if posCount == 1:
					self.__setValue(reqNum, posBlockRow, posBlockCol, posRow, posCol)

	def __setValue(self, num, blockRow, blockCol, row, col):
		#print 'Setting (%s,%s) (%s,%s) to value %s' % (blockRow, blockCol, row, col, num)
		#self.printNotes()
		#print self
		#print '----------'
		self.__matrix[blockRow][blockCol].setValue(num, row, col)

		# clears out available notes from the position whose value was just set
		self.__matrix[blockRow][blockCol].clearNoteNumbers(row, col)

		# clear out values within the block
		self.__clearBlockNoteNumber(blockRow, blockCol, num)

		# clear out rows/columns
		self.__cleanAssignedValue(blockRow, blockCol, row, col)

		self.__setChangeTrue()

		#print 'After'
		#self.printNotes()
		#print self
		#print '----------'

	def __puzzleChanged(self):
		return self.__changeStatus
	def __setChangeTrue(self):
		self.__changeStatus = True
	def __setChangeFalse(self):
		self.__changeStatus = False

	def __puzzleSolved(self):
		return self.__solvedStatus
	def __setSolvedTrue(self):
		self.__solvedStatus = True
	def __setSolvedFalse(self):
		self.__solvedStatus = False

	def __clearBlockNoteNumber(self, blockRow, blockCol, num):
		for row, col in doubleIter(3):
			self.__removeNumber(num, blockRow, blockCol, row, col)

	def __removeReqNum(self, requiredNums, blockRow, blockCol, row, col):
		num = self.value(blockRow, blockCol, row, col)
		if num:
			requiredNums.discard(num)

	# if position has an assigned value, then remove notes for all rows/columns
	def __cleanAssignedValue(self, blockRow, blockCol, row, col):
		num = self.value(blockRow, blockCol, row, col)
		if num:
			# If num is defined, then remove all note values in the columns/rows
			self.__reduceRow(num, blockRow, blockCol, row)
			self.__reduceCol(num, blockRow, blockCol, col)

	def __reduceCol(self, num, blockRow, blockCol, col):
		for blockRowLoop in range(3):
			if blockRowLoop == blockRow:
				continue
			for row in range(3):
				self.__removeNumber(num, blockRowLoop, blockCol, row, col)

	def __reduceRow(self, num, blockRow, blockCol, row):
		for blockColLoop in range(3):
			if blockColLoop == blockCol:
				continue
			for col in range(3):
				self.__removeNumber(num, blockRow, blockColLoop, row, col)

	def __rowDelimeter(self):
		return '-------------------------'

	def __loadFromFile(self, file):
		if os.path.isfile(file):
			tempMatrix = instantiateMatrix(3)
			currentRow = 0

			fhIn = open(file, 'rU')
			for line in fhIn:
				nums = self.__parseFileLine(line)

				# Every 3 lines get incremented
				if self.__currentRowFull(tempMatrix, currentRow):
					currentRow += 1

				tempMatrix[currentRow][0].append(nums[0:3])
				tempMatrix[currentRow][1].append(nums[3:6])
				tempMatrix[currentRow][2].append(nums[6:9])
			fhIn.close()

			self.__instantiateSudokuMatrix(tempMatrix)

		else:
			raise Exception('%s is not a valid file or does not exist.' % (file))

	def __loadFromData(self, data):
		tempMatrix = instantiateMatrix(3)
		currentRow = 0

		for nums in data:
			# Every 3 lines get incremented
			if self.__currentRowFull(tempMatrix, currentRow):
				currentRow += 1

			tempMatrix[currentRow][0].append(nums[0:3])
			tempMatrix[currentRow][1].append(nums[3:6])
			tempMatrix[currentRow][2].append(nums[6:9])

		self.__instantiateSudokuMatrix(tempMatrix)

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
				self.__clearBlockNoteNumber(blockRow, blockCol, num)

			# Reduce numbers across all rows/columns based on initial SudokuBlock values
			self.__reduceRowColNotes(blockRow, blockCol)

	def __validBlockNums(self, blockRow, blockCol):
		validNums = {}
		# Iterate through each of the 9 cells in blockRow, blockCol
		for row, col in doubleIter(3):
			num = self.value(blockRow, blockCol, row, col)
			if num:
				validNums[num] = True
		return validNums

	def __reduceRowColNotes(self, blockRow, blockCol):
		# Iterate through each of the 9 cells in blockRow, blockCol
		for row, col in doubleIter(3):
			self.__cleanAssignedValue(blockRow, blockCol, row, col)

	###
	# Private methods associated with the reduceXwing() method
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

						blockRow1 = row1[0][0]
						blockRow2 = row2[0][0]
						blockCol1_1 = row1[0][1]
						blockCol2_1 = row2[0][1]
						blockCol1_2 = row1[1][1]
						blockCol2_2 = row2[1][1]
						row1_1 = row1[0][2]
						row2_1 = row2[0][2]
						col1_1 = row1[0][3]
						col2_1 = row2[0][3]
						col1_2 = row1[1][3]
						col2_2 = row2[1][3]

						# Ensures the rows are in different blockRows
						# Ensures the columns are in the same blockColumns
						# Ensures the columns are in the same columns
						if blockRow1 != blockRow2 and \
							blockCol1_1 == blockCol2_1 and blockCol1_2 == blockCol2_2 and \
							col1_1 == col2_1 and col1_2 == col2_2:
							self.__removeXwingCol(num, blockCol1_1, col1_1, blockRow1, row1_1, blockRow2, row2_1)
							self.__removeXwingCol(num, blockCol1_2, col1_2, blockRow1, row1_1, blockRow2, row2_1)

	def __possibleRowXwings(self):
		allCoordinates = self.__rowCoordinates()
		potentialXwings = self.__potentialXwings(allCoordinates)
		return potentialXwings

	def __possibleColXwings(self):
		allCoordinates = self.__colCoordinates()
		potentialXwings = self.__potentialXwings(allCoordinates)
		return potentialXwings

	def __potentialXwings(self, allCoordinates):
		potentialXwings = numDictList(3)
		for coordinates in allCoordinates:
			hintCoords = numDictList(3)
			for unitCoords in coordinates:
				blockRow = unitCoords[0]
				blockCol = unitCoords[1]
				row = unitCoords[2]
				col = unitCoords[3]

				noteNums = self.__matrix[blockRow][blockCol].getNoteNumbers(row, col)
				for num in noteNums:
					hintCoords[num].append((blockRow, blockCol, row, col))

			for num in hintCoords:
				if len(hintCoords[num]) == 2:
					potentialXwings[num].append(hintCoords[num])

		return potentialXwings

	def __removeXwingRow(self, num, blockRow, row, blockCol1Skip, col1Skip, blockCol2Skip, col2Skip):
		for blockCol, col in doubleIter(3):
			if self.__skip(blockCol, col, blockCol1Skip, col1Skip) or self.__skip(blockCol, col, blockCol2Skip, col2Skip):
				continue
			self.__removeNumber(num, blockRow, blockCol, row, col)

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

						blockRow1_1 = row1[0][0]
						blockRow2_1 = row2[0][0]
						blockRow1_2 = row1[1][0]
						blockRow2_2 = row2[1][0]

						blockCol1_1 = row1[0][1]
						blockCol2_1 = row2[0][1]
						blockCol1_2 = row1[1][1]
						blockCol2_2 = row2[1][1]

						row1_1 = row1[0][2]
						row2_1 = row2[0][2]
						row1_2 = row1[1][2]
						row2_2 = row2[1][2]

						col1_1 = row1[0][3]
						col2_1 = row2[0][3]
						col1_2 = row1[1][3]
						col2_2 = row2[1][3]

						# Ensures the columns are in different blockColumns
						# Ensures the rows are in the same blockRows
						# Ensures the rows are in the same rows
						if blockCol1_1 != blockCol2_1 and \
							blockRow1_1 == blockRow2_1 and blockRow1_2 == blockRow2_2 and \
							row1_1 == row2_1 and row1_2 == row2_2:
							self.__removeXwingRow(num, blockRow1_1, row1_1, blockCol1_1, col1_1, blockCol2_1, col2_1)
							self.__removeXwingRow(num, blockRow1_2, row1_2, blockCol1_1, col1_1, blockCol2_1, col2_1)

	def __removeXwingCol(self, num, blockCol, col, blockRow1Skip, row1Skip, blockRow2Skip, row2Skip):
		for blockRow, row in doubleIter(3):
			if self.__skip(blockRow, row, blockRow1Skip, row1Skip) or self.__skip(blockRow, row, blockRow2Skip, row2Skip):
				continue
			self.__removeNumber(num, blockRow, blockCol, row, col)

	# Private methods associated with ensuring completed puzzles are valid

	def __checkValidBlocks(self):
		# Iterate through each of the 9 blocks to make sure each one has 9 unique numbers
		for blockRow, blockCol in doubleIter(3):
			if not self.__matrix[blockRow][blockCol].valid():
				print self
				raise Exception('Completed puzzle is not a valid solution.  Block (%s,%s) contains duplicate entries.  Check the code to remove bugs.' % (blockRow, blockCol))

	def __checkValidRows(self):
		# Checks that rows have 9 unique numbers
		for blockRow, row in doubleIter(3):
			if not self.__validRow(blockRow, row):
				print self
				raise Exception('Completed puzzle is not a valid solution.  Row (%s,%s) contains duplicate entries.  Check the code to remove bugs.' % (blockRow, row))

	def __validRow(self, blockRow, row):
		validSolution = True
		validNums = {}
		for blockCol, col in doubleIter(3):
			num = self.value(blockRow, blockCol, row, col)
			validNums[num] = True
		if len(validNums) != 9:
			validSolution = False
		return validSolution

	def __checkValidCols(self):
		# Checks that columns have 9 unique numbers
		for blockCol, col in doubleIter(3):
			if not self.__validCol(blockCol, col):
				print self
				raise Exception('Completed puzzle is not a valid solution.  Column (%s,%s) contains duplicate entries.  Check the code.' % (blockCol, col))

	def __validCol(self, blockCol, col):
		validSolution = True
		validNums = {}
		for blockRow, row in doubleIter(3):
			num = self.value(blockRow, blockCol, row, col)
			validNums[num] = True
		if len(validNums) != 9:
			validSolution = False
		return validSolution

	def __currentRowFull(self, matrix, currentRow):
		if len(matrix[currentRow][0]) == 3 and \
			len(matrix[currentRow][1]) == 3 and \
			len(matrix[currentRow][2]) == 3:
			return True
		else:
			return False

