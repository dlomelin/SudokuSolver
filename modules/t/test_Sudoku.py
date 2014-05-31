import unittest
from SudokuSolver.modules.Sudoku import Sudoku

class TestSudoku(unittest.TestCase):
	def setUp(self):
		pass

	def test_solveHard1(self):
		startData = [
			[' ', '7', ' ', '6', '5', '2', ' ', ' ', '8'],
			[' ', ' ', ' ', '7', '3', '9', '5', ' ', '6'],
			['5', '6', '3', '4', '8', '1', '2', '7', '9'],
			['6', '2', '7', '3', '4', ' ', ' ', ' ', ' '],
			['8', '1', '5', '9', '6', '7', '4', '2', '3'],
			['4', '3', '9', '2', '1', ' ', ' ', ' ', ' '],
			[' ', '5', '6', '8', '7', '3', ' ', ' ', ' '],
			[' ', '9', ' ', '5', '2', ' ', ' ', ' ', ' '],
			[' ', ' ', ' ', '1', '9', ' ', ' ', ' ', ' '],
		]

		solvedData = [
			['9', '7', '4', '6', '5', '2', '1', '3', '8'],
			['1', '8', '2', '7', '3', '9', '5', '4', '6'],
			['5', '6', '3', '4', '8', '1', '2', '7', '9'],
			['6', '2', '7', '3', '4', '5', '8', '9', '1'],
			['8', '1', '5', '9', '6', '7', '4', '2', '3'],
			['4', '3', '9', '2', '1', '8', '7', '6', '5'],
			['2', '5', '6', '8', '7', '3', '9', '1', '4'],
			['3', '9', '1', '5', '2', '4', '6', '8', '7'],
			['7', '4', '8', '1', '9', '6', '3', '5', '2'],
		]

		self.__validateSolver(startData, solvedData)

	def test_solveHard2(self):
		startData = [
			[' ', ' ', '2', ' ', ' ', ' ', ' ', '1', ' '],
			[' ', '9', '4', ' ', ' ', ' ', ' ', '3', ' '],
			[' ', ' ', '3', '9', ' ', ' ', ' ', ' ', '7'],
			[' ', ' ', '1', '8', ' ', ' ', ' ', '6', ' '],
			[' ', '4', ' ', ' ', '5', ' ', '7', ' ', ' '],
			['5', '7', ' ', ' ', '6', ' ', ' ', '9', ' '],
			['1', ' ', ' ', ' ', ' ', '6', '5', ' ', ' '],
			[' ', ' ', '9', ' ', ' ', ' ', '1', '7', ' '],
			[' ', '3', ' ', '2', ' ', ' ', ' ', ' ', ' '],
		]

		solvedData = [
			['7', '5', '2', '6', '8', '3', '9', '1', '4'],
			['8', '9', '4', '7', '1', '5', '2', '3', '6'],
			['6', '1', '3', '9', '2', '4', '8', '5', '7'],
			['9', '2', '1', '8', '3', '7', '4', '6', '5'],
			['3', '4', '6', '1', '5', '9', '7', '2', '8'],
			['5', '7', '8', '4', '6', '2', '3', '9', '1'],
			['1', '8', '7', '3', '9', '6', '5', '4', '2'],
			['2', '6', '9', '5', '4', '8', '1', '7', '3'],
			['4', '3', '5', '2', '7', '1', '6', '8', '9'],
		]

		self.__validateSolver(startData, solvedData)

	def test_solveHard3(self):
		startData = [
			[' ', '5', '7', ' ', ' ', '8', ' ', ' ', '9'],
			['1', '9', ' ', '7', '4', ' ', ' ', ' ', ' '],
			['2', '8', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
			['5', ' ', ' ', ' ', ' ', '3', ' ', ' ', ' '],
			[' ', ' ', ' ', '9', ' ', '7', ' ', ' ', ' '],
			[' ', ' ', ' ', '1', ' ', ' ', ' ', '2', ' '],
			[' ', ' ', ' ', ' ', '8', ' ', ' ', '1', ' '],
			[' ', ' ', '3', ' ', ' ', '2', ' ', '5', ' '],
			[' ', ' ', ' ', '6', ' ', ' ', ' ', ' ', '8'],
		]

		solvedData = [
			['3', '5', '7', '2', '1', '8', '4', '6', '9'],
			['1', '9', '6', '7', '4', '5', '3', '8', '2'],
			['2', '8', '4', '3', '9', '6', '5', '7', '1'],
			['5', '4', '1', '8', '2', '3', '6', '9', '7'],
			['6', '2', '8', '9', '5', '7', '1', '3', '4'],
			['7', '3', '9', '1', '6', '4', '8', '2', '5'],
			['4', '6', '2', '5', '8', '9', '7', '1', '3'],
			['8', '1', '3', '4', '7', '2', '9', '5', '6'],
			['9', '7', '5', '6', '3', '1', '2', '4', '8'],
		]

		self.__validateSolver(startData, solvedData)

	"""
	def test_template(self):
		startData = [
			[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
			[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
			[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
			[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
			[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
			[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
			[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
			[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
			[' ', ' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '],
		]

		solvedData = [
		]

		self.__validateSolver(startData, solvedData)
	"""

	###################
	# Private Methods #
	###################

	def __validateSolver(self, startData, solvedData):
		sudokuObj1 = Sudoku(data=startData)
		sudokuObj1.solve()

		sudokuObj2 = Sudoku(data=solvedData)

		self.assertEqual(sudokuObj1, sudokuObj2)


if __name__ == '__main__':
	unittest.main()