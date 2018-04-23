"""Common shell interaction logic shared between different shells"""
import sys
import os
import inspect
import pyparsing as pp
from six.moves import input
from friendlyshell.command_parsers import default_line_parser

# Path where configuration data is stored for friendly shells
CONFIG_FOLDER = os.path.expanduser(os.path.join("~", ".friendlyshell"))


# pylint: disable=no-member
class BaseShell(object):
    """Common base class for all Friendly Shells

    Defines basic IO and interactive shell logic common to all Friendly Shells

    :param parent:
        Optional parent shell which owns this shell. If none provided this
        shell is assumed to be a parent or first level shell session with
        no ancestry
    """
    def __init__(self, *args, **kwargs):
        # First we pop our parent argument off the call stack so it doesn't
        # propagate to the `object` base class. This needs to be done BEFORE
        # delegating to `super` to initialize the other classes in our
        # class hierarchy
        self._parent = kwargs.pop("parent") if "parent" in kwargs else None

        super(BaseShell, self).__init__(*args, **kwargs)

        # characters preceding the cursor when prompting for command entry
        self.prompt = '> '

        # Flag indicating whether this shell should be closed after the current
        # command finishes processing
        self._done = False

        # Command parser API for parsing tokens from command lines
        self._parser = default_line_parser()

    @property
    def _config_folder(self):
        """Gets the folder where config and log files should be stored

        :rtype: :class:`str`
        """
        # Create our config folder with restricted access to everyone but the
        # owner. This is just in case we write secrets to a log / history file
        # by accident then only the current user can see it.
        if not os.path.exists(CONFIG_FOLDER):
            os.makedirs(CONFIG_FOLDER, 0o700)

        return CONFIG_FOLDER

    def run(self):
        """Main entry point function that launches our command line interpreter

        This method will wait for input to be given via the command line, and
        process each command provided until a request to terminate the shell is
        given.
        """
        while not self._done:
            try:
                line = input(self.prompt)
            except KeyboardInterrupt:
                self._done = True
                continue
            except Exception as err:  # pylint: disable=broad-except
                self.error(
                    'Unexpected error during input sequence: %s',
                    err
                )

                # Reserve the detailed debug info / stack trace to the debug
                # output only. This avoids spitting out lots of technical
                # garbage to the user
                self.debug(err, exc_info=True)
                self._done = True
                continue

            parser = self._parse_line(line)
            if parser is None:
                continue
            func = self._find_command(parser.command)

            if not func:
                self.error("Command not found: %s", parser.command)
                continue

            try:
                if parser.params:
                    if len(parser.params) < self._count_required_params(func):
                        msg = 'Command %s requires %s parameters but ' \
                              '%s were provided.'
                        self.error(
                            msg,
                            func.__name__,
                            self._count_required_params(func),
                            len(parser.params))
                        continue
                    func(*parser.params)
                else:
                    func()
            except Exception as err:  # pylint: disable=broad-except
                # Log summary info about the error to standard error output
                self.error('Unknown error detected: %s', err)
                # Reserve the detailed debug info / stack trace to the debug
                # output only. This avoids spitting out lots of technical
                # garbage to the user
                self.debug(err, exc_info=True)

    def _count_required_params(self, cmd_method):
        """Gets the number of required parameters from a command method

        :param cmd_method:
            :class:`inspect.Signature` for method to analyse
        :returns:
            Number of required parameters (ie: parameters without default
            values) for the given method
        :rtype: :class:`int`
        """

        if sys.version_info < (3, 3):  # pragma: no cover
            # TODO: Consider whether I should drop Python 3.0-3.3 support
            params = inspect.getargspec(cmd_method)  # pylint: disable=deprecated-method
            self.debug(
                'Command %s params are: %s',
                cmd_method.__name__,
                params
            )
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
        self.debug('Parsing command input "%s"...', line)

        try:
            retval = self._parser.parseString(line, parseAll=True)
        except pp.ParseException as err:
            self.error('Parsing error:')
            self.error('\t%s', err.pstr)
            self.error('\t%s^', ' ' * (err.col-1))
            self.debug('Details: %s', err)
            return None
        self.debug('Parsed command line is "%s"', retval)
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
        self.debug('Terminating interpreter...')
        self._done = True

        # See if our shell has any parents, and force them to quit too
        if self._parent:
            self._parent.do_exit()

    def do_close(self):
        """Terminates the currently running shell

        If the current shell is a sub-shell spawned by another Friendly Shell
        instance, control will return to the parent shell which will continue
        running"""
        self.debug(
            'Closing shell %s (%s)',
            self.__class__.__name__,
            self.prompt)

        # Return control back to the parent Friendly Shell or the console,
        # whichever comes next in the shell's ancestry
        self._done = True


if __name__ == "__main__":
    pass
