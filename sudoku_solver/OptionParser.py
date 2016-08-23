'''.'''

from optparse import OptionParser


class OptionParser(OptionParser):  # pylint: disable=function-redefined
    ''' Add functionality to the OptionParser module '''

    def check_required(self, param):
        '''
        Make sure the specified parameter was supplied by the user
        Ex: self.check_required('--file')
        '''
        option = self.get_option(param)
        if getattr(self.values, option.dest) is None:
            self.print_help()
            self.exit(2, '%s option was not supplied.\n' % (option))
