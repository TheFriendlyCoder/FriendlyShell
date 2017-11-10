"""Mixin class that adds command completion to a friendly shell"""
import inspect
import platform
from contextlib import contextmanager

try:
    if platform.system() == 'Windows':
        # TODO: Test this on a Windows platform
        import pyreadline as readline
    else:
        import readline
    AUTOCOMPLETE_ENABLED = True
except ImportError:
    AUTOCOMPLETE_ENABLED = False


@contextmanager
def auto_complete_manager(key, callback):
    """Context manager for enabling command line auto-completion

    :param str key: descriptor for keyboard key to use for auto completion trigger
    :param callback: method point for the callback to run when completion key is pressed"""
    if not AUTOCOMPLETE_ENABLED:
        # If auto-completion isn't supported, do nothing
        yield
        return

    # TODO: Consider whether we need to synchronize the readline.get_completer_delims()
    # with our command parser objects for consistency

    # Configure our auto-completion callback
    old_completer = readline.get_completer()
    readline.set_completer(callback)
    readline.parse_and_bind(key + ": complete")

    # Return control back to the caller
    yield

    # When the context manager goes out of scope, restore it's previous state
    readline.set_completer(old_completer)


class CommandCompleteMixin(object):  # pylint: disable=too-few-public-methods
    """Mixin class to be added to any friendly shell to add command completion support"""

    def __init__(self):
        super(CommandCompleteMixin, self).__init__()
        self.complete_key = 'tab'
        self._latest_matches = None

    def _complete_command_names(self, partial_cmd):
        """Autocompletion method for command names"""
        all_methods = inspect.getmembers(self, inspect.ismethod)
        retval = []
        for cur_method in all_methods:
            if cur_method[0].startswith('do_' + partial_cmd):
                retval.append(cur_method[0][3:])
        return retval

    def _get_completion_callback(self, cmd):
        """Finds the callback method for completing command parameters for a given command"""
        # Next we check to see if the specified command has an auto-completion method
        # As a general convention we assume such helper methods are named with the
        # prefix "complete_".
        method_name = 'complete_' + cmd
        if not hasattr(self, method_name):
            self._log.debug('No completion method for command %s', cmd)
            return None

        # Make sure the auto-completion method looks correct (ie: is callable)
        tmp_method = getattr(self, method_name)
        if not inspect.ismethod(tmp_method):
            self._log.debug('\tCompletion method %s should be callable with 2 input parameters. '
                            'Check derived class')
            return None

        return tmp_method

    def _get_callback_param_index(self, parser, original_line, token):
        """Calculates which command parameter is being completed."""
        param_index = None
        for i in range(len(parser.params)):
            self._log.debug("\tSeeing if token %s is the one to match", parser.params[i])
            self._log.debug("\t\tMatching offset is %s", readline.get_begidx())
            self._log.debug("\t\tMatching token is %s", token)
            self._log.debug("\t\tOffset of %s in %s is %s",
                            parser.params[i],
                            original_line,
                            original_line.find(parser.params[i], len(parser.command)))
            if original_line.find(parser.params[i], len(parser.command)) == readline.get_begidx():
                self._log.debug("\tFound match at parameter %s", i)
                param_index = i
                break

        # Sanity checks...
        if param_index is None:
            self._log.debug('Unable to match param %s to index', token)
            return None

        if not parser.params[param_index].startswith(token):
            self._log.debug('Screwed up token matching %s != %s', token, parser.params[param_index])
            return None

        return param_index

    def _get_completions(self, tmp_method, parser, param_index, token):
        """Gets a list of possible matches for a given command parameter"""
        self._log.debug('\tCalling into auto completion method %s...', tmp_method.__name__)
        retval = tmp_method(parser, param_index, len(token))
        self._log.debug('Found matches: %s', retval)
        # Sanity Check: command completion methods MUST always return a list of possible
        # token matches. THe list may be empty, but they must always return a list
        if not isinstance(retval, list):
            self._log.debug('\tUser defined completion method %s must return a list of matches',
                            tmp_method.__name__)
            self._log.debug('\tActual returned data was %s', retval)
            return None

        return retval

    def _get_completion_matches(self, token):
        """Given a partially completed command token, return a list of potential matches for
        a completed token cmopatible with the command being entered

        :param str token: token to be matched
        :returns: list of 0 or more compatible tokens that partially match the one given
        :rtype: :class:`list`
        """
        # Get the full input line as it appears on the prompt
        original_line = readline.get_line_buffer()

        # If the start of our current token is the start of the line, we can assume
        # the user wants us to complete the name of one of the Friendly Shell's
        # commands (since all commands begin with a command name)
        # Therefore, we simply return a list of command names that partially match
        # the current token
        if readline.get_begidx() == 0:
            return self._complete_command_names(token)

        # Once here, we know we've at least got a command name and the user now wishes
        # to auto-complete one of the parameters to that command. So we next parse our
        # partially entered command to get more contextual information
        parser = self._parse_line(original_line)

        tmp_method = self._get_completion_callback(parser.command)
        if not tmp_method:
            return None

        # Figure out which of our parsed command tokens is the one to be auto-completed
        param_index = self._get_callback_param_index(parser, original_line, token)
        if not param_index:
            return None

        # Call our auto-completion helper method to get a list of possible matches to
        # the partially entered parameter
        return self._get_completions(tmp_method, parser, param_index, token)

    def _complete_callback(self, token, index):
        """Autocomplete method called by readline library to retrieve candidates for a partially entered command

        NOTE: Exceptions and errors in this callback, including returning of "invalid" data like :class:`None` are
        simply ignored and treated as though there were no matches found. As such there doesn't appear to be any way
        to force the interpreter to exit when errors occur in this method.

        NOTE: Seeing as how any output to stdout or stderr result in corruption of the interactive prompt which
        uses this callback, all output messages produced by this method are redirected to debug streams so they
        can be silently logged to disk for later diagnostics.

        :param str token: the text associated with the token that is to be completed
        :param int index: index of which matching result from the possible list of matching tokens to return. So for
                          example 0 means return the first potential match for the given token from the list of
                          compatible matches. 1 means return the second potential match, etc.
        :returns: Full text for the given token which partially matches the text of the currently selected token
                  Returns None if there are no matches for the given token"""
        try:
            # --------------------------------- DEBUG OUTPUT -----------------------------
            # NOTE: The begidx and endidx parameters specify the start and end+1 location of the sub-string
            #       being processed
            # NOTE: If the user has placed their input cursor in the middle of the token, only the characters
            #       up to but not including the one above the cursor are returned in this parameter
            if index == 0:
                self._log.debug('Beginning auto-completion routine...')

            self._log.debug('\t\tSelected token "%s"', token)
            self._log.debug('\t\tMatch to return "%s"', index)
            # All text currently entered at the prompt, less the prompt itself
            self._log.debug('\t\tline "%s"', readline.get_line_buffer())
            # represents the offset from the start of the string to the first character in the token to process
            self._log.debug('\t\tBeginning index "%s"', readline.get_begidx())
            # represents the offset from the start of the string to the character under the cursor
            # NOTE: this may be the end of the current token or it may not...
            # NOTE: if the cursor is past the end of the last token (ie: preparing to accept a new character)
            #       this index would be: len(line) + 1
            self._log.debug('\t\tEnding index "%s"', readline.get_endidx())
            # -----------------------------------------------------------------------------

            if index != 0:
                if index >= len(self._latest_matches):
                    self._log.debug('Completed auto completion routine.')
                    return None

                self._log.debug('\tReturning partial match #%s: %s', index, self._latest_matches[index])
                return self._latest_matches[index]

            self._latest_matches = self._get_completion_matches(token)

            if self._latest_matches is None:
                self._log.debug('\tFailed to get completion matches for token %s', token)
                return None

            assert isinstance(self._latest_matches, list)

            if not self._latest_matches:
                self._log.debug('\tNo matches for token %s found', token)
                return None

            self._log.debug('\tReturning first match %s', self._latest_matches[0])
            return self._latest_matches[0]

        except Exception as err:  # pylint: disable=broad-except
            self._log.debug('Unknown error during command completion operation: %s', err, exec_info=True)
            return None  # pylint: disable=lost-exception


if __name__ == "__main__":
    pass
