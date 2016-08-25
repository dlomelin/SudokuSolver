import unittest
from sudoku_solver.SudokuBlock import SudokuBlock


class TestSudokuBlock(unittest.TestCase):
    def setUp(self):
        numListStart = [['9', '7', ' '], [' ', ' ', ' '], ['5', '6', '3']]
        self.sudokuBlockObj = SudokuBlock(numListStart)

    # Add missing values to the block using set_value and make sure
    # complete() method returns True
    def test_completeTrue(self):
        self.sudokuBlockObj.set_value(1, 0, 2)
        self.sudokuBlockObj.set_value(2, 1, 0)
        self.sudokuBlockObj.set_value(4, 1, 1)
        self.sudokuBlockObj.set_value(8, 1, 2)
        self.assertTrue(self.sudokuBlockObj.complete())

    # Starting values are incomplete so make sure complete() method returns False
    def test_completeFalse(self):
        self.assertFalse(self.sudokuBlockObj.complete())

    # Add missing values to the block using set_value and make sure
    # valid() method returns True (complete and unique numbers)
    def test_validTrue(self):
        self.sudokuBlockObj.set_value(1, 0, 2)
        self.sudokuBlockObj.set_value(2, 1, 0)
        self.sudokuBlockObj.set_value(4, 1, 1)
        self.sudokuBlockObj.set_value(8, 1, 2)
        self.assertTrue(self.sudokuBlockObj.valid())

    # Starting values are incomplete so make sure valid() method returns False
    def test_validFalse1(self):
        self.assertFalse(self.sudokuBlockObj.valid())

    # Add non unique missing values to the block using set_value and make sure
    # valid() method returns False (complete but not unique numbers)
    def test_validFalse2(self):
        self.sudokuBlockObj.set_value(1, 0, 2)
        self.sudokuBlockObj.set_value(2, 1, 0)
        self.sudokuBlockObj.set_value(4, 1, 1)
        self.sudokuBlockObj.set_value(7, 1, 2)
        self.assertFalse(self.sudokuBlockObj.valid())

    # Standard get_value() test
    def test_getValue1(self):
        self.assertEqual('9', self.sudokuBlockObj.get_value(0, 0))

    # Standard get_value() test
    def test_getValue2(self):
        self.assertEqual('6', self.sudokuBlockObj.get_value(2, 1))

    # Standard object equality test
    def test_equal(self):
        numListStart2 = [['9', '7', ' '], [' ', ' ', ' '], ['5', '6', '3']]
        sudokuBlockObj2 = SudokuBlock(numListStart2)
        self.assertEqual(self.sudokuBlockObj, sudokuBlockObj2)

    # Standard object equality test after using the set_value() method to one of the objects
    def test_equalAdd(self):
        # Create a new object
        numListStart2 = [['9', '7', ' '], ['1', ' ', ' '], ['5', '6', '3']]
        sudokuBlockObj2 = SudokuBlock(numListStart2)

        # Add to the original object, which should make the 2 objects the same
        self.sudokuBlockObj.set_value(1, 1, 0)
        self.assertEqual(self.sudokuBlockObj, sudokuBlockObj2)

    # Standard object equality test
    def test_notEqual(self):
        numListStart2 = [['9', '7', ' '], ['1', ' ', ' '], ['5', '6', '3']]
        sudokuBlockObj2 = SudokuBlock(numListStart2)
        self.assertNotEqual(self.sudokuBlockObj, sudokuBlockObj2)

    # Standard get_candidates() test
    def test_getNoteNumbers(self):
        notes = self.sudokuBlockObj.get_candidates(0, 2)
        self.assertEqual(notes, set(['1', '2', '3', '4', '5', '6', '7', '8', '9']))

    # Standard get_candidates() test after clear_candidates()
    def test_clearCandidates(self):
        self.sudokuBlockObj.clear_candidates(0, 2)
        notes = self.sudokuBlockObj.get_candidates(0, 2)
        self.assertEqual(notes, set())

    # Standard get_candidates() test after several delete_candidate_number()
    def test_deleteCandidateNumber(self):
        for num in [1, 3, 5]:
            self.sudokuBlockObj.delete_candidate_number(num, 0, 2)
        notes = self.sudokuBlockObj.get_candidates(0, 2)
        self.assertEqual(notes, set(['2', '4', '6', '7', '8', '9']))
