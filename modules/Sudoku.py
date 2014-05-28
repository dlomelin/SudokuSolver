import os

from SudokuSolver.modules.utilities import instantiateMatrix
from SudokuSolver.modules.SudokuBlock import SudokuBlock

# TODO reduce code for row/col operations

class Sudoku(object):
	def __init__(self, **args):
		fieldsToCheck = ['file']
		self.__checkParameters(fieldsToCheck, args)

		# Parses file with starting Sudoku numbers and loads object
		self.__loadFromFile(args['file'])

	def solve(self):

		while True:
			self.__setChangeFalse()

			# Assign numbers based on a row or column requiring all 9 numbers
			self.__assignUnitSum()

			# Reduce numbers based on hint pairs in the same row or column
			self.__reduceCandidateLines()

			# Reduce numbers based on using the xwing method
			self.__reduceXwing()

			# Reduce numbers based on naked pairs/trios
			self.__reduceNakedSets()

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

	def complete(self):
		allComplete = True
		for blockRow in range(3):
			for blockCol in range(3):
				if not self.matrix[blockRow][blockCol].complete():
					allComplete = False
		return allComplete

	def printNotes(self):
		noteSets = [['1','2','3'], ['4','5','6'], ['7','8','9']]
		for blockRow in range(3):
			if blockRow == 0:
				print self.__blockRowSplit()
			for row in range(3):
				for i in range(len(noteSets)):
					print '||',
					for blockCol in range(3):
						for col in range(3):
							numString = ''
							noteNums = self.matrix[blockRow][blockCol].noteNumsDict(row, col)
							for num in noteSets[i]:
								if noteNums.has_key(num):
									numString += '%s' % (num)
								else:
									numString += ' '
							if col == 2:
								colSplit = '||'
							else:
								colSplit = '|'
							print '%s %s' % (numString, colSplit),
					print
				if row == 2:
					print self.__blockRowSplit()
				else:
					print self.__rowSplit()

	def value(self, blockRow, blockCol, row, col):
		return self.matrix[blockRow][blockCol].value(row, col)

	###################
	# Private Methods #
	###################

	def __checkParameters(self, requiredList, data):
		missingFields = []
		for field in requiredList:
			if not field in data:
				missingFields.append('The following required field was not provided: %s' % (field))
		if missingFields:
			raise Exception('\n'.join(missingFields))

	@staticmethod
	def __rowSplit():
		return '-----------------------------------------------------------'
	@staticmethod
	def __blockRowSplit():
		return '==========================================================='

	def __reduceNakedSets(self):
		self.__reduceNakedSetRow()
		self.__reduceNakedSetCol()
		self.__reduceNakedSetBlock()

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

				noteNums = self.matrix[blockRow][blockCol].noteNumsDict(row, col)
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

	@staticmethod
	def __combineNotes(list, coords):
		uniqueNums = {}
		for indexNum in coords:
			for num in list[indexNum].keys():
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

	@staticmethod
	def __skipCoords(skipCoords, skipIndex, blockRow, blockCol, row, col):
		skip = False
		for i in skipIndex:
			testBlockRow = skipCoords[i][0]
			testBlockCol = skipCoords[i][1]
			testRow = skipCoords[i][2]
			testCol = skipCoords[i][3]
			if testBlockRow == blockRow and testBlockCol == blockCol and testRow == row and testCol == col:
				skip = True
		return skip

	@staticmethod
	def __rowCoordinates():
		coordinates = []
		for blockRow in range(3):
			for row in range(3):
				rowCoords = []
				for blockCol in range(3):
					for col in range(3):
						rowCoords.append((blockRow, blockCol, row, col))
				coordinates.append(rowCoords)
		return coordinates

	@staticmethod
	def __colCoordinates():
		coordinates = []
		for blockCol in range(3):
			for col in range(3):
				colCoords = []
				for blockRow in range(3):
					for row in range(3):
						colCoords.append((blockRow, blockCol, row, col))
				coordinates.append(colCoords)
		return coordinates

	@staticmethod
	def __blockCoordinates():
		coordinates = []
		for blockRow in range(3):
			for blockCol in range(3):
				blockCoords = []
				for row in range(3):
					for col in range(3):
						blockCoords.append((blockRow, blockCol, row, col))
				coordinates.append(blockCoords)
		return coordinates

	def __reduceXwing(self):
		self.__reduceXwingRow()
		self.__reduceXwingCol()

	def __removeNumber(self, num, blockRow, blockCol, row, col):

		noteNums = self.matrix[blockRow][blockCol].noteNumsDict(row, col)
		if noteNums.has_key(num):
			self.matrix[blockRow][blockCol].removeNumber(num, row, col)

			nums = noteNums.keys()
			if len(nums) == 1:
				self.__setValue(nums[0], blockRow, blockCol, row, col)
			self.__setChangeTrue()

	@staticmethod
	def __skip(blockRow, row, blockRowSkip, rowSkip):
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
		hintCoords = SudokuBlock.numDictList()

		for unitCoords in coordinates:
			blockRow = unitCoords[0]
			blockCol = unitCoords[1]
			row = unitCoords[2]
			col = unitCoords[3]

			noteNums = self.matrix[blockRow][blockCol].noteNumsDict(row, col)
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
			requiredNums = SudokuBlock.numDict()
			for unitCoords in coordinates:
				blockRow = unitCoords[0]
				blockCol = unitCoords[1]
				row = unitCoords[2]
				col = unitCoords[3]

				self.__removeReqNum(requiredNums, blockRow, blockCol, row, col)

			for reqNum in requiredNums.keys():
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
						noteNums = self.matrix[blockRow][blockCol].noteNumsDict(row, col)
						if noteNums.has_key(reqNum):
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
		self.matrix[blockRow][blockCol].setValue(num, row, col)

		# clears out available notes from the position whose value was just set
		self.matrix[blockRow][blockCol].clearNotes(row, col)

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
		return self.__newChange
		
	def __setChangeTrue(self):
		self.__newChange = True
	def __setChangeFalse(self):
		self.__newChange = False

	def __clearBlockNoteNumber(self, blockRow, blockCol, num):
		for row in range(3):
			for col in range(3):
				self.__removeNumber(num, blockRow, blockCol, row, col)

	def __removeReqNum(self, requiredNums, blockRow, blockCol, row, col):
		num = self.value(blockRow, blockCol, row, col)
		if num and requiredNums.has_key(num):
			del requiredNums[num]

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

	def __str__(self):
		string = '%s\n' % (self.__rowDelimeter())

		for matRow in range(3):
			for row in range(3):
				string += '| '
				for matCol in range(3):
					for col in range(3):
						num = self.value(matRow, matCol, row, col)
						if not num:
							num = '.'
						string += '%s ' % (num)
					string += '| '
				string += '\n'
			string += '%s\n' % (self.__rowDelimeter())

		return string

	@staticmethod
	def __rowDelimeter():
		return '-------------------------'

	def __loadFromFile(self, file):
		if os.path.isfile(file):
			tempMatrix = instantiateMatrix()
			currentRow = 0

			fhIn = open(file, 'rU')
			for line in fhIn:
				line = line.strip('\n')
				nums = list(line)

				if self.__currentRowFull(tempMatrix, currentRow):
					currentRow += 1

				tempMatrix[currentRow][0].append(nums[0:3])
				tempMatrix[currentRow][1].append(nums[3:6])
				tempMatrix[currentRow][2].append(nums[6:9])
			fhIn.close()

			self.__instantiateSudokuMatrix(tempMatrix)

		else:
			raise Exception('%s is not a valid file or does not exist.' % (file))

	def __instantiateSudokuMatrix(self, tempMatrix):
		self.matrix = instantiateMatrix()
		for blockRow in range(3):
			for blockCol in range(3):
				self.matrix[blockRow][blockCol] = SudokuBlock(tempMatrix[blockRow][blockCol])

		print '     Starting Puzzle'
		print self

		self.__clearInitialValueNotes()

	def __clearInitialValueNotes(self):
		for blockRow in range(3):
			for blockCol in range(3):
				# Reduce numbers within the SudokuBlock based on initial values
				for num in self.__validBlockNums(blockRow, blockCol):
					self.__clearBlockNoteNumber(blockRow, blockCol, num)

				# Reduce numbers across all rows/columns based on initial SudokuBlock values
				self.__reduceRowColNotes(blockRow, blockCol)

	def __validBlockNums(self, blockRow, blockCol):
		validNums = {}
		for row in range(3):
			for col in range(3):
				num = self.value(blockRow, blockCol, row, col)
				if num:
					validNums[num] = True
		return validNums

	def __reduceRowColNotes(self, blockRow, blockCol):
		# Loop through all positions in blockRow, blockCol
		for row in range(3):
			for col in range(3):
				self.__cleanAssignedValue(blockRow, blockCol, row, col)

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
		potentialXwings = SudokuBlock.numDictList()
		for coordinates in allCoordinates:
			hintCoords = SudokuBlock.numDictList()
			for unitCoords in coordinates:
				blockRow = unitCoords[0]
				blockCol = unitCoords[1]
				row = unitCoords[2]
				col = unitCoords[3]

				noteNums = self.matrix[blockRow][blockCol].noteNumsDict(row, col)
				for num in noteNums:
					hintCoords[num].append((blockRow, blockCol, row, col))

			for num in hintCoords:
				if len(hintCoords[num]) == 2:
					potentialXwings[num].append(hintCoords[num])

		return potentialXwings

	def __removeXwingRow(self, num, blockRow, row, blockCol1Skip, col1Skip, blockCol2Skip, col2Skip):
		for blockCol in range(3):
			for col in range(3):
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
		for blockRow in range(3):
			for row in range(3):
				if self.__skip(blockRow, row, blockRow1Skip, row1Skip) or self.__skip(blockRow, row, blockRow2Skip, row2Skip):
					continue
				self.__removeNumber(num, blockRow, blockCol, row, col)

	# Private methods associated with ensuring completed puzzles are valid

	def __checkValidBlocks(self):
		# Checks that each block has 9 unique numbers
		for blockRow in range(3):
			for blockCol in range(3):
				if not self.matrix[blockRow][blockCol].valid():
					print self
					raise Exception('Completed puzzle is not a valid solution.  Block (%s,%s) contains duplicate entries.  Check the code.' % (blockRow, blockCol))

	def __checkValidRows(self):
		# Checks that rows have 9 unique numbers
		for blockRow in range(3):
			for row in range(3):
				if not self.__validRow(blockRow, row):
					print self
					raise Exception('Completed puzzle is not a valid solution.  Row (%s,%s) contains duplicate entries.  Check the code.' % (blockRow, row))

	def __validRow(self, blockRow, row):
		validSolution = True
		validNums = {}
		for blockCol in range(3):
			for col in range(3):
				num = self.value(blockRow, blockCol, row, col)
				validNums[num] = True
		if len(validNums) != 9:
			validSolution = False
		return validSolution

	def __checkValidCols(self):
		# Checks that columns have 9 unique numbers
		for blockCol in range(3):
			for col in range(3):
				if not self.__validCol(blockCol, col):
					print self
					raise Exception('Completed puzzle is not a valid solution.  Column (%s,%s) contains duplicate entries.  Check the code.' % (blockCol, col))

	def __validCol(self, blockCol, col):
		validSolution = True
		validNums = {}
		for blockRow in range(3):
			for row in range(3):
				num = self.value(blockRow, blockCol, row, col)
				validNums[num] = True
		if len(validNums) != 9:
			validSolution = False
		return validSolution

	@staticmethod
	def __currentRowFull(matrix, currentRow):
		if len(matrix[currentRow][0]) == 3 and \
			len(matrix[currentRow][1]) == 3 and \
			len(matrix[currentRow][2]) == 3:
			return True
		else:
			return False

