from SudokuSolver.modules.Sudoku import Sudoku
from SudokuSolver.modules.OptionParser import OptionParser

def main():
	params = getParams()

	sudokuObj = Sudoku(file=params.puzzle)

	# Prints starting values
	print sudokuObj

	# Solve the puzzle
	sudokuObj.solve()

	# If the solver was unable to fill in all cells
	# then print out the final notes
	if not sudokuObj.complete():
		sudokuObj.printCandidates()

	# Prints out final values after solving
	print sudokuObj

	if params.techniquesUsed:
		sudokuObj.printTechniquesUsed()


###

def getParams():
	parser = OptionParser()
	parser.add_option(
		"--puzzle",
		type = "string",
		action = "store",
		help = "File with starting puzzle.",
	)
	parser.add_option(
		"--techniquesUsed",
		action = "store_true",
		default = False,
		help = "Prints out a list of techniques used.",
	)

	(options, args) = parser.parse_args()
	parser.check_required("--puzzle")

	return options

###

if __name__ == '__main__':
	main()
