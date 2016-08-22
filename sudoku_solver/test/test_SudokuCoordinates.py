import unittest
from sudoku_solver.SudokuCoordinates import SudokuCoordinates

class TestSudokuBlock(unittest.TestCase):
    def setUp(self):
        pass

    def test_str(self):
        scObj1 = SudokuCoordinates(0, 0, 0, 0)
        self.assertEqual(str(scObj1), '(0,0,0,0)')

    def test_eq(self):
        scObj1 = SudokuCoordinates(0, 0, 0, 0)
        scObj2 = SudokuCoordinates(0, 0, 0, 0)
        self.assertEqual(scObj1, scObj2)

    def test_notEq(self):
        scObj1 = SudokuCoordinates(0, 0, 0, 0)
        scObj2 = SudokuCoordinates(1, 1, 1, 1)
        self.assertNotEqual(scObj1, scObj2)

    def test_alignsByBlockTrue(self):
        scObj1 = SudokuCoordinates(0, 0, 0, 0)
        scObj2 = SudokuCoordinates(0, 0, 1, 1)
        self.assertTrue(scObj1.alignsByBlock(scObj2))

    def test_alignsByBlockFalse(self):
        scObj1 = SudokuCoordinates(0, 0, 0, 0)
        scObj2 = SudokuCoordinates(1, 1, 0, 0)
        self.assertFalse(scObj1.alignsByBlock(scObj2))

    def test_alignsByRowTrue(self):
        scObj1 = SudokuCoordinates(0, 0, 0, 2)
        scObj2 = SudokuCoordinates(0, 2, 0, 1)
        self.assertTrue(scObj1.alignsByRow(scObj2))

    def test_alignsByRowFalse(self):
        scObj1 = SudokuCoordinates(0, 0, 0, 0)
        scObj2 = SudokuCoordinates(0, 0, 1, 0)
        self.assertFalse(scObj1.alignsByRow(scObj2))

    def test_alignsByColTrue(self):
        scObj1 = SudokuCoordinates(0, 0, 2, 0)
        scObj2 = SudokuCoordinates(2, 0, 1, 0)
        self.assertTrue(scObj1.alignsByCol(scObj2))

    def test_alignsByColFalse(self):
        scObj1 = SudokuCoordinates(0, 0, 0, 0)
        scObj2 = SudokuCoordinates(0, 0, 0, 1)
        self.assertFalse(scObj1.alignsByCol(scObj2))
