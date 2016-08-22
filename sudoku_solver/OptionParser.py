from optparse import OptionParser

# Add functionality to the OptionParser module
class OptionParser(OptionParser):

    # Make sure the specified parameter was supplied by the user
    # Ex: self.check_required('--file')
    def check_required(self, param):
        option = self.get_option(param)
        if getattr(self.values, option.dest) is None:
            self.print_help()
            self.exit(2, '%s option was not supplied.\n' % (option))
