"""Common shell interaction logic shared between different shells"""
import os
import sys
import inspect
import subprocess
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

        # text to be displayed upon launch of the shell, before displaying
        # the interactive prompt
        self.banner_text = None

        # Flag indicating whether this shell should be closed after the current
        # command finishes processing
        self._done = False

        # Command parser API for parsing tokens from command lines
        self._parser = default_line_parser()

        self._input_stream = None

    @property
    def input_stream(self):
        """Gets the input source where commands are parsed for this shell

        May return None if no input stream attached to this shell
        """
        return self._input_stream

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

    def _get_input(self):
        """Gets input to be processed from the appropriate source

        :returns: the input line retrieved from the source
        :rtype: :class:`str`
        """
        try:
            if self.input_stream:
                line = self.input_stream.readline()
                if not line:
                    raise EOFError()
                self.info(self.prompt + line)
            else:
                line = input(self.prompt)
            return line
        except KeyboardInterrupt:
            # When the user enters CTRL+C to terminate the shell, we just
            # terminate the currently running shell. That way if there is
            # a parent shell in play control can be returned to it so the
            # user can attempt to recover from whatever operation they
            # tried to abort
            self._done = True
            return None
        except EOFError:
            # When reading from an input stream, see if we've reached the
            # end of the stream. If so, assume we are meant to terminate
            # the shell and return control back to the caller. This avoids
            # having to force the user to always end their non-interactive
            # scripts with an 'exit' command at the end
            self.do_exit()
            return None
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
            return None

    def _execute_command(self, func, parser):
        """Calls a command function with a set of parsed parameters

        :param func: the command function to execute
        :param parser: The parsed command parameters to pass to the command
        """
        try:
            num_params = len(parser.params) if parser.params else 0
            required_params = self._count_required_params(func)
            all_params = self._count_params(func)
            if not required_params <= num_params <= all_params:
                msg = 'Command %s requires %s of %s parameters but ' \
                      '%s were provided.'
                self.error(
                    msg,
                    func.__name__.replace("do_", ""),
                    required_params,
                    all_params,
                    num_params)
                return

            if parser.params:
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
        except KeyboardInterrupt:
            self.debug("User interrupted operation...")
            # Typically, when a user cancels an operation there will be at
            # least some partial output gemerated by the command so we
            # write out a blank to ensure the interactive prompt appears on
            # the line below
            self.info("")

    def _run_shell_command(self, cmd):
        """Executes a shell command within the Friendly Shell environment

        :param str cmd: Shell command to execute
        """
        self.debug("Running shell command %s", cmd)
        try:
            output = subprocess.check_output(
                cmd,
                shell=True,
                stderr=subprocess.STDOUT)
            self.info(output)
        except subprocess.CalledProcessError as err:
            self.info("Failed to run command %s: %s", err.cmd, err.returncode)
            self.info(err.output)
        except KeyboardInterrupt:
            self.debug("User interrupted operation...")
            # Typically, when a user cancels an operation there will be at
            # least some partial output gemerated by the command so we
            # write out a blank to ensure the interactive prompt appears on
            # the line below
            self.info("")

    def run(self, *_args, **kwargs):
        """Main entry point function that launches our command line interpreter

        This method will wait for input to be given via the command line, and
        process each command provided until a request to terminate the shell is
        given.

        :param input_stream:
            optional Python input stream object where commands should be loaded
            from. Typically this will be a file-like object containing commands
            to be run, but any input stream object should work.
            If not provided, input will be read from stdin using :meth:`input`
        """
        self._input_stream = \
            kwargs.pop("input_stream") if "input_stream" in kwargs else None

        if self.banner_text:
            self.info(self.banner_text)

        while not self._done:
            line = self._get_input()
            if not line:
                continue

            if line[0] == "!":
                self._run_shell_command(line[1:])
                continue

            parser = self._parse_line(line)
            if parser is None:
                continue

            func = self._find_command(parser.command)
            if not func:
                self.error("Command not found: %s", parser.command)
                continue

            self._execute_command(func, parser)

    def _count_required_params(self, cmd_method):
        """Gets the number of required parameters from a command method

        :param cmd_method:
            :class:`inspect.Signature` for method to analyse
        :returns:
            Number of required parameters (ie: parameters without default
            values) for the given method
        :rtype: :class:`int`
        """
        if sys.version_info < (3, 3):
            params = inspect.getargspec(cmd_method)  # pylint: disable=deprecated-method
            self.debug(
                'Command %s params are: %s',
                cmd_method.__name__,
                params)
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

    def _count_params(self, cmd_method):
        """Gets the total number of parameters from a command method

        :param cmd_method:
            :class:`inspect.Signature` for method to analyse
        :returns:
            Number of parameters supported by the given method
        :rtype: :class:`int`
        """
        if sys.version_info < (3, 3):
            params = inspect.getargspec(cmd_method)  # pylint: disable=deprecated-method
            self.debug(
                'Command %s params are: %s',
                cmd_method.__name__,
                params)
            tmp = params.args

            if 'self' in tmp:
                tmp.remove('self')
            return len(tmp)

        func_sig = inspect.signature(cmd_method)  # pylint: disable=no-member
        return len(func_sig.parameters)

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
