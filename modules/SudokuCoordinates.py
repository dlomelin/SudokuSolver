# Simple class wrapper to make coordinate retrieval easier
class SudokuCoordinates(object):
	def __init__(self, blockRow, blockCol, row, col):
		self.blockRow = blockRow
		self.blockCol = blockCol
		self.row = row
		self.col = col
