from sudoku_solver.Sudoku import Sudoku
from sudoku_solver.OptionParser import OptionParser


def main():
    params = getParams()

    sudokuObj = Sudoku(file=params.puzzle)

    # Prints starting values
    if not params.gridValues:
        print sudokuObj
    else:
        print 'Starting'
        printGridValues(sudokuObj.gridValues())

    # Solve the puzzle
    sudokuObj.solve()

    # If the solver was unable to fill in all cells
    # then print out the final notes
    if not sudokuObj.complete():
        sudokuObj.printCandidates()

    # Prints out final values after solving
    if not params.gridValues:
        print sudokuObj
    else:
        print 'Ending'
        printGridValues(sudokuObj.gridValues())

    if params.techniquesUsed:
        sudokuObj.printTechniquesUsed()


def printGridValues(gridList):
    print '['
    for i in xrange(len(gridList)):
        print '%s,' % (str(gridList[i]).replace('.', ' '))
    print ']'


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
    parser.add_option(
        "--gridValues",
        action = "store_true",
        default = False,
        help = "Prints out a list of grid values in list form instead of formatted.",
    )

    (options, args) = parser.parse_args()
    parser.check_required("--puzzle")

    return options


if __name__ == '__main__':
    main()
