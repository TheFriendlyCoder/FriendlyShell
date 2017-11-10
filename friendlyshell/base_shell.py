"""Common shell interaction logic shared between different shells"""
import logging
import sys
import inspect
import pyparsing as pp
from six.moves import input
from friendlyshell.command_parsers import default_line_parser


class BaseShell(object):
    """Common base class for all Friendly Shells

    Defines basic IO and interactive shell logic common to all Friendly Shells"""

    def __init__(self):
        super(BaseShell, self).__init__()
        # characters preceding the cursor when prompting for command entry
        self.prompt = '> '
        # flag controlling whether the command loop should continue processing commands
        # If a command sets this flag to True, the main command loop will terminate
        self._done = False
        # Command parser API for parsing tokens from command lines
        self._parser = default_line_parser()
        # logger
        self._log = logging.getLogger(__name__)

    def run(self):
        """Main entry point function that launches our command line interpreter

        This method will wait for input to be given via the command line, and process
        each command provided until a request to terminate the shell is given."""
        while not self._done:
            try:
                line = input(self.prompt)
            except KeyboardInterrupt:
                self._done = True
                continue
            except Exception as err:  # pylint: disable=broad-except
                self._log.error('Unexpected error during input sequence: %s', err)
                # Reserve the detailed debug info / stack trace to the debug output only
                # This avoids spitting out lots of technical garbage to the user
                self._log.debug(err, exc_info=True)
                self._done = True
                continue

            parser = self._parse_line(line)
            if parser is None:
                continue
            func = self._find_command(parser.command)

            try:
                if parser.params:
                    if len(parser.params) < self._count_required_params(func):
                        self._log.error('Command %s requires %s parameters but %s were provided.',
                                        func.__name__,
                                        self._count_required_params(func),
                                        len(parser.params))
                        continue
                    func(*parser.params)
                else:
                    func()
            except Exception as err:  # pylint: disable=broad-except
                # Log summary info about the error to standard error output
                self._log.error('Unknown error detected: %s', err)
                # Reserve the detailed debug info / stack trace to the debug output only
                # This avoids spitting out lots of technical garbage to the user
                self._log.debug(err, exc_info=True)

    def _count_required_params(self, cmd_method):
        """Gets the number of required parameters from a command method

        :param cmd_method: :class:`inspect.Signature` for method to analyse
        :returns: Number of required parameters (ie: parameters without default values) for the given method
        :rtype: :class:`int`
        """

        if sys.version_info < (3, 3):
            params = inspect.getargspec(cmd_method)  # pylint: disable=deprecated-method
            self._log.debug('Command %s params are: %s', cmd_method.__name__, params)
            tmp = params.args
            if 'self' in tmp:
                tmp.remove('self')
            return len(tmp) - (len(params.defaults) if params.defaults else 0)

        func_sig = inspect.signature(cmd_method)  # pylint: disable=no-member
        retval = 0
        for cur_param in func_sig.parameters.values():
            if cur_param.default is inspect.Parameter.empty:  # pylint: disable=no-member
                retval += 1
        return retval

    def _parse_line(self, line):
        """Parses a single line of command text and returns the parsed output

        :param str line: line of command text to be parsed
        :returns: Parser object describing all of the parsed command tokens
        :rtype: :class:`pyparsing.ParseResults`"""
        self._log.debug('Parsing command input "%s"...', line)

        try:
            retval = self._parser.parseString(line, parseAll=True)
        except pp.ParseException as err:
            self._log.error('Parsing error:')
            self._log.error('\t%s', err.pstr)
            self._log.error('\t' + ' ' * (err.col-1) + '^')
            self._log.debug('Details: %s', err)
            return None
        self._log.debug('Parsed command line is "%s"', retval)
        return retval

    def _find_command(self, command_name):
        """Attempts to locate the command handler for a given command

        :param str command_name: The name of the command to find the handler for
        :returns: Reference to the method to be called to execute the command
                  Returns None if no command method found
        :rtype: :class:`meth`
        """
        all_methods = inspect.getmembers(self, inspect.ismethod)
        for cur_method in all_methods:
            if cur_method[0] == 'do_' + command_name:
                return cur_method[1]
        return None

    def do_exit(self):
        """Terminates the command interpreter"""
        self._log.debug('Terminating interpreter...')
        self._done = True


if __name__ == "__main__":
    pass
