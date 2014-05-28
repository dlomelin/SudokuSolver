from optparse import OptionParser

class OptionParser(OptionParser):
	def check_required(self, param):
		option = self.get_option(param)
		if getattr(self.values, option.dest) is None:
			self.print_help()
			self.exit(2, '%s option was not supplied.\n' % (option))
