import unittest
from SudokuSolver.modules.Sudoku import Sudoku

class TestSudoku(unittest.TestCase):
	def setUp(self):
		pass

	def test_dataInputSolve(self):
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
		sudokuObj1 = Sudoku(data=startData)
		sudokuObj1.solve()

		endData = [
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
		sudokuObj2 = Sudoku(data=endData)

		self.assertEqual(sudokuObj1, sudokuObj2)

if __name__ == '__main__':
	unittest.main()
