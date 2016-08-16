import unittest
from SudokuSolver.modules.SudokuBlock import SudokuBlock

class TestSudokuBlock(unittest.TestCase):
	def setUp(self):
		numListStart = [['9', '7', ' '], [' ', ' ', ' '], ['5', '6', '3']]
		self.sudokuBlockObj = SudokuBlock(numListStart)

	# Add missing values to the block using setValue and make sure
	# complete() method returns True
	def test_completeTrue(self):
		self.sudokuBlockObj.setValue(1, 0, 2)
		self.sudokuBlockObj.setValue(2, 1, 0)
		self.sudokuBlockObj.setValue(4, 1, 1)
		self.sudokuBlockObj.setValue(8, 1, 2)
		self.assertTrue(self.sudokuBlockObj.complete())

	# Starting values are incomplete so make sure complete() method returns False
	def test_completeFalse(self):
		self.assertFalse(self.sudokuBlockObj.complete())

	# Add missing values to the block using setValue and make sure
	# valid() method returns True (complete and unique numbers)
	def test_validTrue(self):
		self.sudokuBlockObj.setValue(1, 0, 2)
		self.sudokuBlockObj.setValue(2, 1, 0)
		self.sudokuBlockObj.setValue(4, 1, 1)
		self.sudokuBlockObj.setValue(8, 1, 2)
		self.assertTrue(self.sudokuBlockObj.valid())

	# Starting values are incomplete so make sure valid() method returns False
	def test_validFalse1(self):
		self.assertFalse(self.sudokuBlockObj.valid())

	# Add non unique missing values to the block using setValue and make sure
	# valid() method returns False (complete but not unique numbers)
	def test_validFalse2(self):
		self.sudokuBlockObj.setValue(1, 0, 2)
		self.sudokuBlockObj.setValue(2, 1, 0)
		self.sudokuBlockObj.setValue(4, 1, 1)
		self.sudokuBlockObj.setValue(7, 1, 2)
		self.assertFalse(self.sudokuBlockObj.valid())

	# Standard getValue() test
	def test_getValue1(self):
		self.assertEqual('9', self.sudokuBlockObj.getValue(0, 0))

	# Standard getValue() test
	def test_getValue2(self):
		self.assertEqual('6', self.sudokuBlockObj.getValue(2, 1))

	# Standard object equality test
	def test_equal(self):
		numListStart2 = [['9', '7', ' '], [' ', ' ', ' '], ['5', '6', '3']]
		sudokuBlockObj2 = SudokuBlock(numListStart2)
		self.assertEqual(self.sudokuBlockObj, sudokuBlockObj2)

	# Standard object equality test after using the setValue() method to one of the objects
	def test_equalAdd(self):
		# Create a new object
		numListStart2 = [['9', '7', ' '], ['1', ' ', ' '], ['5', '6', '3']]
		sudokuBlockObj2 = SudokuBlock(numListStart2)

		# Add to the original object, which should make the 2 objects the same
		self.sudokuBlockObj.setValue(1, 1, 0)
		self.assertEqual(self.sudokuBlockObj, sudokuBlockObj2)

	# Standard object equality test
	def test_notEqual(self):
		numListStart2 = [['9', '7', ' '], ['1', ' ', ' '], ['5', '6', '3']]
		sudokuBlockObj2 = SudokuBlock(numListStart2)
		self.assertNotEqual(self.sudokuBlockObj, sudokuBlockObj2)

	# Standard getCandidates() test
	def test_getNoteNumbers(self):
		notes = self.sudokuBlockObj.getCandidates(0, 2)
		self.assertEqual(notes, set(['1', '2', '3', '4', '5', '6', '7', '8', '9']))

	# Standard getCandidates() test after clearCandidates()
	def test_clearCandidates(self):
		self.sudokuBlockObj.clearCandidates(0, 2)
		notes = self.sudokuBlockObj.getCandidates(0, 2)
		self.assertEqual(notes, set())

	# Standard getCandidates() test after several deleteCandidateNumber()
	def test_deleteCandidateNumber(self):
		for num in [1, 3, 5]:
			self.sudokuBlockObj.deleteCandidateNumber(num, 0, 2)
		notes = self.sudokuBlockObj.getCandidates(0, 2)
		self.assertEqual(notes, set(['2', '4', '6', '7', '8', '9']))

if __name__ == '__main__':
	unittest.main()
