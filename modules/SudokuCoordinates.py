# Simple class wrapper to make coordinate retrieval easier
class SudokuCoordinates(object):
	def __init__(self, blockRow, blockCol, row, col):
		self.blockRow = blockRow
		self.blockCol = blockCol
		self.row = row
		self.col = col

	def __str__(self):
		return '(%s,%s,%s,%s)' % (self.blockRow, self.blockCol, self.row, self.col)

	def __eq__(self, other):
		if self.blockRow == other.blockRow and self.blockCol == other.blockCol and \
			self.row == other.row and self.col == other.col:
			return True
		else:
			return False

	##################
	# Public Methosd #
	##################

	def alignsByBlock(self, other):
		if self.blockRow == other.blockRow and self.blockCol == other.blockCol:
			return True
		else:
			return False

	def alignsByRow(self, other):
		if self.blockRow == other.blockRow and self.row == other.row:
			return True
		else:
			return False

	def alignsByCol(self, other):
		if self.blockCol == other.blockCol and self.col == other.col:
			return True
		else:
			return False
