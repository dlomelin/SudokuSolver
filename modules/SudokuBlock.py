from SudokuSolver.modules.utilities import instantiateMatrix

class SudokuBlock(object):
	def __init__(self, numList):
		self.__validateNumList(numList)
		self.__values = numList
		self.__loadNoteNumbers()
		self.__eliminateKnownNumbers()

	def valid(self):
		validSolution = True
		validNums = {}
		for row in range(3):
			for col in range(3):
				num = self.value(row, col)
				if not num:
					validSolution = False
				else:
					validNums[num] = True
		if len(validNums) != 9:
			validSolution = False
		return validSolution

	def complete(self):
		allComplete = True
		for row in range(3):
			for col in range(3):
				if not self.value(row, col):
					allComplete = False
		return allComplete

	def value(self, row, col):
		value = None
		if self.__values[row][col].isdigit():
			value = self.__values[row][col]
		return value

	def noteNumsDict(self, row, col):
		return self.__noteNums[row][col]

	def setValue(self, num, row, col):
		self.__values[row][col] = num

	def removeNumber(self, num, row, col):
		if self.__noteNums[row][col].has_key(num):
			del self.__noteNums[row][col][num]

	def clearNotes(self, row, col):
		self.__noteNums[row][col] = {}

	@staticmethod
	def numDict():
		return dict({'1': True, '2': True, '3': True,
						 '4': True, '5': True, '6': True,
						 '7': True, '8': True, '9': True,
						})

	@staticmethod
	def numDictList():
		return dict({'1': [], '2': [], '3': [],
						 '4': [], '5': [], '6': [],
						 '7': [], '8': [], '9': [],
						})

	###################
	# Private Methods #
	###################

	def __eliminateKnownNumbers(self):
		for row in range(3):
			for col in range(3):
				if self.value(row, col):
					self.clearNotes(row, col)

	def __loadNoteNumbers(self):
		self.__noteNums = instantiateMatrix()
		for row in range(3):
			for col in range(3):
				self.__noteNums[row][col] = self.numDict()

	@staticmethod
	def __validateNumList(numList):
		listLen = len(numList)
		if listLen != 3:
			raise Exception('Invalid number of lists passed to SudokuBlock object.  Must contain 3 lists.')

		numCount = 0
		numDict = {}
		for itemList in numList:
			itemLen = len(itemList)
			if itemLen != 3:
				raise Exception('Invalid number of items passed to SudokuBlock object.  Must contain 3 items.')
			for num in itemList:
				if num.isdigit():
					numCount += 1
					numDict[num] = True
		numLen = len(numDict)
		if numLen != numCount:
			raise Exception('Duplicate numbers pre-assigned to SudokuBlock object.')
