'''.'''

import unittest
import tempfile
from sudoku_solver.Sudoku import Sudoku, MissingArguments


class TestSudoku(unittest.TestCase):
    def setUp(self):
        pass

    # Tests the xwing solver using a puzzle that requires xwing technique
    def test_solveXwingColPuzzle(self):
        startData = [
            ['1', ' ', '9', '7', ' ', ' ', '6', ' ', '2'],
            [' ', '7', ' ', ' ', '6', ' ', ' ', '1', ' '],
            ['4', ' ', ' ', ' ', ' ', '9', '5', ' ', ' '],
            ['5', ' ', ' ', ' ', ' ', '3', '7', ' ', ' '],
            [' ', '8', '7', ' ', '5', ' ', ' ', '6', ' '],
            [' ', ' ', '1', '8', ' ', ' ', ' ', ' ', '5'],
            [' ', ' ', '3', '9', ' ', ' ', ' ', ' ', '6'],
            [' ', '1', ' ', ' ', '8', ' ', ' ', '9', ' '],
            ['7', '9', ' ', ' ', ' ', '4', '2', ' ', ' '],
        ]

        solvedData = [
            ['1', '5', '9', '7', '3', '8', '6', '4', '2'],
            ['3', '7', '2', '4', '6', '5', '8', '1', '9'],
            ['4', '6', '8', '1', '2', '9', '5', '7', '3'],
            ['5', '2', '4', '6', '9', '3', '7', '8', '1'],
            ['9', '8', '7', '2', '5', '1', '3', '6', '4'],
            ['6', '3', '1', '8', '4', '7', '9', '2', '5'],
            ['8', '4', '3', '9', '7', '2', '1', '5', '6'],
            ['2', '1', '5', '3', '8', '6', '4', '9', '7'],
            ['7', '9', '6', '5', '1', '4', '2', '3', '8'],
        ]

        self.__validateSolver(startData, solvedData)

    # Tests the multiple lines solver using a puzzle that requires multiple lines technique
    def test_solveMultipleLines(self):
        startData = [
            [' ', ' ', '9', ' ', '3', ' ', '6', ' ', ' '],
            [' ', '3', '6', ' ', '1', '4', ' ', '8', '9'],
            ['1', ' ', ' ', '8', '6', '9', ' ', '3', '5'],
            [' ', '9', ' ', ' ', ' ', ' ', '8', ' ', ' '],
            [' ', '1', ' ', ' ', ' ', ' ', ' ', '9', ' '],
            [' ', '6', '8', ' ', '9', ' ', '1', '7', ' '],
            ['6', ' ', '1', '9', ' ', '3', ' ', ' ', '2'],
            ['9', '7', '2', '6', '4', ' ', '3', ' ', ' '],
            [' ', ' ', '3', ' ', '2', ' ', '9', ' ', ' '],
        ]

        solvedData = [
            ['8', '4', '9', '5', '3', '2', '6', '1', '7'],
            ['5', '3', '6', '7', '1', '4', '2', '8', '9'],
            ['1', '2', '7', '8', '6', '9', '4', '3', '5'],
            ['3', '9', '5', '4', '7', '1', '8', '2', '6'],
            ['7', '1', '4', '2', '8', '6', '5', '9', '3'],
            ['2', '6', '8', '3', '9', '5', '1', '7', '4'],
            ['6', '8', '1', '9', '5', '3', '7', '4', '2'],
            ['9', '7', '2', '6', '4', '8', '3', '5', '1'],
            ['4', '5', '3', '1', '2', '7', '9', '6', '8'],
        ]

        self.__validateSolver(startData, solvedData)

    # Tests the naked sets solver using a puzzle that requires the naked sets technique
    def test_solveReduceNakedSets(self):
        startData = [
            ['4', ' ', ' ', '3', ' ', '8', ' ', ' ', '7'],
            [' ', '1', ' ', ' ', '7', '9', ' ', '4', ' '],
            [' ', ' ', ' ', '6', ' ', '4', ' ', ' ', ' '],
            [' ', '3', ' ', ' ', ' ', '7', ' ', '9', ' '],
            ['6', '4', '8', '1', '9', '3', '2', '7', '5'],
            [' ', '7', ' ', ' ', ' ', '2', ' ', '1', ' '],
            [' ', ' ', ' ', '9', ' ', '5', ' ', ' ', ' '],
            [' ', '2', ' ', '7', '4', '1', ' ', '3', ' '],
            ['1', ' ', ' ', '8', ' ', '6', ' ', ' ', '4'],
        ]

        solvedData = [
            ['4', '5', '2', '3', '1', '8', '9', '6', '7'],
            ['3', '1', '6', '2', '7', '9', '5', '4', '8'],
            ['9', '8', '7', '6', '5', '4', '3', '2', '1'],
            ['2', '3', '1', '5', '8', '7', '4', '9', '6'],
            ['6', '4', '8', '1', '9', '3', '2', '7', '5'],
            ['5', '7', '9', '4', '6', '2', '8', '1', '3'],
            ['7', '6', '4', '9', '3', '5', '1', '8', '2'],
            ['8', '2', '5', '7', '4', '1', '6', '3', '9'],
            ['1', '9', '3', '8', '2', '6', '7', '5', '4'],
        ]

        self.__validateSolver(startData, solvedData)

    # Tests the y wing solver using a puzzle that requires the y wing technique
    def test_solveYWing1(self):

        startData = [
            ['9', '6', '3', '5', '1', '8', '7', '4', '2'],
            [' ', '5', '1', '2', ' ', '3', '9', '6', '8'],
            [' ', '2', '8', ' ', '9', ' ', '1', '3', '5'],
            [' ', ' ', '2', ' ', ' ', ' ', '5', '8', '9'],
            ['5', ' ', '7', '8', ' ', '9', ' ', '1', '6'],
            [' ', '8', '9', ' ', '5', ' ', '3', ' ', ' '],
            [' ', '9', '4', ' ', '8', '5', '6', ' ', ' '],
            [' ', '7', '5', '4', '6', ' ', '8', '9', ' '],
            ['8', '1', '6', '9', ' ', '7', ' ', '5', ' '],
        ]

        solvedData = [
            ['9', '6', '3', '5', '1', '8', '7', '4', '2'],
            ['7', '5', '1', '2', '4', '3', '9', '6', '8'],
            ['4', '2', '8', '7', '9', '6', '1', '3', '5'],
            ['6', '4', '2', '3', '7', '1', '5', '8', '9'],
            ['5', '3', '7', '8', '2', '9', '4', '1', '6'],
            ['1', '8', '9', '6', '5', '4', '3', '2', '7'],
            ['2', '9', '4', '1', '8', '5', '6', '7', '3'],
            ['3', '7', '5', '4', '6', '2', '8', '9', '1'],
            ['8', '1', '6', '9', '3', '7', '2', '5', '4'],
        ]

        self.__validateSolver(startData, solvedData)

    def test_solveYWing2(self):
        startData = [
            ['9', ' ', ' ', '2', '4', ' ', ' ', ' ', ' '],
            [' ', '5', ' ', '6', '9', ' ', '2', '3', '1'],
            [' ', '2', ' ', ' ', '5', ' ', ' ', '9', ' '],
            [' ', '9', ' ', '7', ' ', ' ', '3', '2', ' '],
            [' ', ' ', '2', '9', '3', '5', '6', ' ', '7'],
            [' ', '7', ' ', ' ', ' ', '2', '9', ' ', ' '],
            [' ', '6', '9', ' ', '2', ' ', ' ', '7', '3'],
            ['5', '1', ' ', ' ', '7', '9', ' ', '6', '2'],
            ['2', ' ', '7', ' ', '8', '6', ' ', ' ', '9'],
        ]

        solvedData = [
            ['9', '3', '1', '2', '4', '7', '5', '8', '6'],
            ['7', '5', '4', '6', '9', '8', '2', '3', '1'],
            ['6', '2', '8', '1', '5', '3', '7', '9', '4'],
            ['1', '9', '5', '7', '6', '4', '3', '2', '8'],
            ['4', '8', '2', '9', '3', '5', '6', '1', '7'],
            ['3', '7', '6', '8', '1', '2', '9', '4', '5'],
            ['8', '6', '9', '5', '2', '1', '4', '7', '3'],
            ['5', '1', '3', '4', '7', '9', '8', '6', '2'],
            ['2', '4', '7', '3', '8', '6', '1', '5', '9'],
        ]

        self.__validateSolver(startData, solvedData)

    def test_solveSwordfishColumn(self):
        startData = [
            ['9', '2', '6', ' ', ' ', ' ', '1', ' ', ' '],
            ['5', '3', '7', ' ', '1', ' ', '4', '2', ' '],
            ['8', '4', '1', ' ', ' ', ' ', '6', ' ', '3'],
            ['2', '5', '9', '7', '3', '4', '8', '1', '6'],
            ['7', '1', '4', ' ', '6', ' ', ' ', '3', ' '],
            ['3', '6', '8', '1', '2', ' ', ' ', '4', ' '],
            ['1', ' ', '2', ' ', ' ', ' ', ' ', '8', '4'],
            ['4', '8', '5', ' ', '7', '1', '3', '6', ' '],
            ['6', ' ', '3', ' ', ' ', ' ', ' ', ' ', '1'],
        ]

        solvedData = [
            ['9', '2', '6', '5', '4', '3', '1', '7', '8'],
            ['5', '3', '7', '6', '1', '8', '4', '2', '9'],
            ['8', '4', '1', '2', '9', '7', '6', '5', '3'],
            ['2', '5', '9', '7', '3', '4', '8', '1', '6'],
            ['7', '1', '4', '8', '6', '9', '2', '3', '5'],
            ['3', '6', '8', '1', '2', '5', '9', '4', '7'],
            ['1', '9', '2', '3', '5', '6', '7', '8', '4'],
            ['4', '8', '5', '9', '7', '1', '3', '6', '2'],
            ['6', '7', '3', '4', '8', '2', '5', '9', '1'],
        ]

        self.__validateSolver(startData, solvedData)

    def test_solveSwordfishRow1(self):
        startData = [
            ['5', '2', '9', '4', '1', ' ', '7', ' ', '3'],
            [' ', ' ', '6', ' ', ' ', '3', ' ', ' ', '2'],
            [' ', ' ', '3', '2', ' ', ' ', ' ', ' ', ' '],
            [' ', '5', '2', '3', ' ', ' ', ' ', '7', '6'],
            ['6', '3', '7', ' ', '5', ' ', '2', ' ', ' '],
            ['1', '9', ' ', '6', '2', '7', '5', '3', ' '],
            ['3', ' ', ' ', ' ', '6', '9', '4', '2', ' '],
            ['2', ' ', ' ', '8', '3', ' ', '6', ' ', ' '],
            ['9', '6', ' ', '7', '4', '2', '3', ' ', '5'],
        ]

        solvedData = [
            ['5', '2', '9', '4', '1', '8', '7', '6', '3'],
            ['7', '1', '6', '5', '9', '3', '8', '4', '2'],
            ['8', '4', '3', '2', '7', '6', '1', '5', '9'],
            ['4', '5', '2', '3', '8', '1', '9', '7', '6'],
            ['6', '3', '7', '9', '5', '4', '2', '1', '8'],
            ['1', '9', '8', '6', '2', '7', '5', '3', '4'],
            ['3', '8', '5', '1', '6', '9', '4', '2', '7'],
            ['2', '7', '4', '8', '3', '5', '6', '9', '1'],
            ['9', '6', '1', '7', '4', '2', '3', '8', '5'],
        ]

        self.__validateSolver(startData, solvedData)

    def test_solveSwordfishRow2(self):
        startData = [
            [' ', '2', ' ', ' ', '4', '3', ' ', '6', '9'],
            [' ', ' ', '3', '8', '9', '6', '2', ' ', ' '],
            ['9', '6', ' ', ' ', '2', '5', ' ', '3', ' '],
            ['8', '9', ' ', '5', '6', ' ', ' ', '1', '3'],
            ['6', ' ', ' ', ' ', '3', ' ', ' ', ' ', ' '],
            [' ', '3', ' ', ' ', '8', '1', ' ', '2', '6'],
            ['3', ' ', ' ', ' ', '1', ' ', ' ', '7', ' '],
            [' ', ' ', '9', '6', '7', '4', '3', ' ', '2'],
            ['2', '7', ' ', '3', '5', '8', ' ', '9', ' '],
        ]

        solvedData = [
            ['5', '2', '8', '1', '4', '3', '7', '6', '9'],
            ['7', '1', '3', '8', '9', '6', '2', '4', '5'],
            ['9', '6', '4', '7', '2', '5', '8', '3', '1'],
            ['8', '9', '2', '5', '6', '7', '4', '1', '3'],
            ['6', '5', '1', '4', '3', '2', '9', '8', '7'],
            ['4', '3', '7', '9', '8', '1', '5', '2', '6'],
            ['3', '4', '5', '2', '1', '9', '6', '7', '8'],
            ['1', '8', '9', '6', '7', '4', '3', '5', '2'],
            ['2', '7', '6', '3', '5', '8', '1', '9', '4'],
        ]

        self.__validateSolver(startData, solvedData)

    def test_missing_arguments(self):
        with self.assertRaises(MissingArguments):
            Sudoku()

    def test_missing_file_load(self):
        fh = tempfile.NamedTemporaryFile()
        fh.write(
            '97 652  8\n   7395 6\n563481279\n62734    \n815967423\n'
            '43921    \n 56873   \n 9 52    \n   19',
        )
        fh.seek(0)
        sudokuObj = Sudoku(file=fh.name)
        sudokuObj.solve()
        self.assertTrue(sudokuObj.complete())

    # Test that the __eq__ method returns True for the same data sets
    def test_eq(self):
        data1 = [
            ['4', '5', '2', '3', '1', '8', '9', '6', '7'],
            ['3', '1', '6', '2', '7', '9', '5', '4', '8'],
            ['9', '8', '7', '6', '5', '4', '3', '2', '1'],
            ['2', '3', '1', '5', '8', '7', '4', '9', '6'],
            ['6', '4', '8', '1', '9', '3', '2', '7', '5'],
            ['5', '7', '9', '4', '6', '2', '8', '1', '3'],
            ['7', '6', '4', '9', '3', '5', '1', '8', '2'],
            ['8', '2', '5', '7', '4', '1', '6', '3', '9'],
            ['1', '9', '3', '8', '2', '6', '7', '5', '4'],
        ]
        sudokuObj1 = Sudoku(data=data1)
        sudokuObj2 = Sudoku(data=data1)

        self.assertEqual(sudokuObj1, sudokuObj2)

    # Test that the __eq__ method does not return True for different data sets
    def test_notEq(self):
        data1 = [
            ['4', '5', '2', '3', '1', '8', '9', '6', '7'],
            ['3', '1', '6', '2', '7', '9', '5', '4', '8'],
            ['9', '8', '7', '6', '5', '4', '3', '2', '1'],
            ['2', '3', '1', '5', '8', '7', '4', '9', '6'],
            ['6', '4', '8', '1', '9', '3', '2', '7', '5'],
            ['5', '7', '9', '4', '6', '2', '8', '1', '3'],
            ['7', '6', '4', '9', '3', '5', '1', '8', '2'],
            ['8', '2', '5', '7', '4', '1', '6', '3', '9'],
            ['1', '9', '3', '8', '2', '6', '7', '5', '4'],
        ]
        sudokuObj1 = Sudoku(data=data1)

        data2 = [
            ['8', '4', '9', '5', '3', '2', '6', '1', '7'],
            ['5', '3', '6', '7', '1', '4', '2', '8', '9'],
            ['1', '2', '7', '8', '6', '9', '4', '3', '5'],
            ['3', '9', '5', '4', '7', '1', '8', '2', '6'],
            ['7', '1', '4', '2', '8', '6', '5', '9', '3'],
            ['2', '6', '8', '3', '9', '5', '1', '7', '4'],
            ['6', '8', '1', '9', '5', '3', '7', '4', '2'],
            ['9', '7', '2', '6', '4', '8', '3', '5', '1'],
            ['4', '5', '3', '1', '2', '7', '9', '6', '8'],
        ]
        sudokuObj2 = Sudoku(data=data2)

        self.assertNotEqual(sudokuObj1, sudokuObj2)

    # test the output value of the grid_values method
    def test_gridValues(self):
        startData = [
            ['4', ' ', ' ', '3', ' ', '8', ' ', ' ', '7'],
            [' ', '1', ' ', ' ', '7', '9', ' ', '4', ' '],
            [' ', ' ', ' ', '6', ' ', '4', ' ', ' ', ' '],
            [' ', '3', ' ', ' ', ' ', '7', ' ', '9', ' '],
            ['6', '4', '8', '1', '9', '3', '2', '7', '5'],
            [' ', '7', ' ', ' ', ' ', '2', ' ', '1', ' '],
            [' ', ' ', ' ', '9', ' ', '5', ' ', ' ', ' '],
            [' ', '2', ' ', '7', '4', '1', ' ', '3', ' '],
            ['1', ' ', ' ', '8', ' ', '6', ' ', ' ', '4'],
        ]
        sudokuObj = Sudoku(data=startData)
        gridDataTest = sudokuObj.grid_values()

        gridData = [
            ['4', '.', '.', '3', '.', '8', '.', '.', '7'],
            ['.', '1', '.', '.', '7', '9', '.', '4', '.'],
            ['.', '.', '.', '6', '.', '4', '.', '.', '.'],
            ['.', '3', '.', '.', '.', '7', '.', '9', '.'],
            ['6', '4', '8', '1', '9', '3', '2', '7', '5'],
            ['.', '7', '.', '.', '.', '2', '.', '1', '.'],
            ['.', '.', '.', '9', '.', '5', '.', '.', '.'],
            ['.', '2', '.', '7', '4', '1', '.', '3', '.'],
            ['1', '.', '.', '8', '.', '6', '.', '.', '4'],
        ]

        self.assertEqual(gridData, gridDataTest)

    # Test that the string operator works as expected
    def test_string(self):
        data1 = [
            ['4', '5', '2', '3', '1', '8', '9', '6', '7'],
            ['3', '1', '6', '2', '7', '9', '5', '4', '8'],
            ['9', '8', '7', '6', '5', '4', '3', '2', '1'],
            ['2', '3', '1', '5', '8', '7', '4', '9', '6'],
            ['6', '4', '8', '1', '9', '3', '2', '7', '5'],
            ['5', '7', '9', '4', '6', '2', '8', '1', '3'],
            ['7', '6', '4', '9', '3', '5', '1', '8', '2'],
            ['8', '2', '5', '7', '4', '1', '6', '3', '9'],
            ['1', '9', '3', '8', '2', '6', '7', '5', '4'],
        ]
        sudokuObj = Sudoku(data=data1)

        self.assertEqual(
            str(sudokuObj),
            '        Incomplete       \n'
            '-------------------------\n'
            '| 4 5 2 | 3 1 8 | 9 6 7 |\n'
            '| 3 1 6 | 2 7 9 | 5 4 8 |\n'
            '| 9 8 7 | 6 5 4 | 3 2 1 |\n'
            '-------------------------\n'
            '| 2 3 1 | 5 8 7 | 4 9 6 |\n'
            '| 6 4 8 | 1 9 3 | 2 7 5 |\n'
            '| 5 7 9 | 4 6 2 | 8 1 3 |\n'
            '-------------------------\n'
            '| 7 6 4 | 9 3 5 | 1 8 2 |\n'
            '| 8 2 5 | 7 4 1 | 6 3 9 |\n'
            '| 1 9 3 | 8 2 6 | 7 5 4 |\n'
            '-------------------------\n',
        )

        sudokuObj.solve()

        self.assertEqual(
            str(sudokuObj),
            '         Solution        \n'
            '-------------------------\n'
            '| 4 5 2 | 3 1 8 | 9 6 7 |\n'
            '| 3 1 6 | 2 7 9 | 5 4 8 |\n'
            '| 9 8 7 | 6 5 4 | 3 2 1 |\n'
            '-------------------------\n'
            '| 2 3 1 | 5 8 7 | 4 9 6 |\n'
            '| 6 4 8 | 1 9 3 | 2 7 5 |\n'
            '| 5 7 9 | 4 6 2 | 8 1 3 |\n'
            '-------------------------\n'
            '| 7 6 4 | 9 3 5 | 1 8 2 |\n'
            '| 8 2 5 | 7 4 1 | 6 3 9 |\n'
            '| 1 9 3 | 8 2 6 | 7 5 4 |\n'
            '-------------------------\n',
        )

    # Test that the complete method returns True for a complete data set
    def test_complete(self):
        data1 = [
            ['4', '5', '2', '3', '1', '8', '9', '6', '7'],
            ['3', '1', '6', '2', '7', '9', '5', '4', '8'],
            ['9', '8', '7', '6', '5', '4', '3', '2', '1'],
            ['2', '3', '1', '5', '8', '7', '4', '9', '6'],
            ['6', '4', '8', '1', '9', '3', '2', '7', '5'],
            ['5', '7', '9', '4', '6', '2', '8', '1', '3'],
            ['7', '6', '4', '9', '3', '5', '1', '8', '2'],
            ['8', '2', '5', '7', '4', '1', '6', '3', '9'],
            ['1', '9', '3', '8', '2', '6', '7', '5', '4'],
        ]
        sudokuObj1 = Sudoku(data=data1)

        self.assertTrue(sudokuObj1.complete())

    # Test that the complete method returns False for a complete data set
    def test_not_complete(self):
        data1 = [
            [' ', '2', ' ', ' ', '4', '3', ' ', '6', '9'],
            [' ', ' ', '3', '8', '9', '6', '2', ' ', ' '],
            ['9', '6', ' ', ' ', '2', '5', ' ', '3', ' '],
            ['8', '9', ' ', '5', '6', ' ', ' ', '1', '3'],
            ['6', ' ', ' ', ' ', '3', ' ', ' ', ' ', ' '],
            [' ', '3', ' ', ' ', '8', '1', ' ', '2', '6'],
            ['3', ' ', ' ', ' ', '1', ' ', ' ', '7', ' '],
            [' ', ' ', '9', '6', '7', '4', '3', ' ', '2'],
            ['2', '7', ' ', '3', '5', '8', ' ', '9', ' '],
        ]
        sudokuObj1 = Sudoku(data=data1)

        self.assertFalse(sudokuObj1.complete())

    def test_getCellValue(self):
        data1 = [
            ['4', '5', '2', '3', '1', '8', '9', '6', '7'],
            ['3', '1', '6', '2', '7', '9', '5', '4', '8'],
            ['9', '8', '7', '6', '5', '4', '3', '2', '1'],
            ['2', '3', '1', '5', '8', '7', '4', '9', '6'],
            ['6', '4', '8', '1', '9', '3', '2', '7', '5'],
            ['5', '7', '9', '4', '6', '2', '8', '1', '3'],
            ['7', '6', '4', '9', '3', '5', '1', '8', '2'],
            ['8', '2', '5', '7', '4', '1', '6', '3', '9'],
            ['1', '9', '3', '8', '2', '6', '7', '5', '4'],
        ]
        sudokuObj1 = Sudoku(data=data1)

        self.assertTrue(sudokuObj1.get_cell_value(0, 0, 2, 1), 8)
        self.assertTrue(sudokuObj1.get_cell_value(2, 0, 0, 2), 4)
        self.assertTrue(sudokuObj1.get_cell_value(1, 1, 0, 1), 5)

    ###################
    # Private Methods #
    ###################

    def __validateSolver(self, startData, solvedData):
        sudokuObj1 = Sudoku(data=startData)
        sudokuObj1.solve()

        sudokuObj2 = Sudoku(data=solvedData)

        self.assertEqual(sudokuObj1, sudokuObj2)
