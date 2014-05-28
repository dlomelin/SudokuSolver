from SudokuSolver.modules.Sudoku import Sudoku
from SudokuSolver.modules.OptionParser import OptionParser

def main():
	params = getParams()

	sudokuObj = Sudoku(file=params.puzzle)
	sudokuObj.solve()

	print sudokuObj

###

def getParams():
	parser = OptionParser()
	parser.add_option(
		"--puzzle",
		type="string",
		action="store",
		help="File with starting puzzle.",
	)

	(options, args) = parser.parse_args()
	parser.check_required("--puzzle")

	return options

###

if __name__ == '__main__':
	main()
