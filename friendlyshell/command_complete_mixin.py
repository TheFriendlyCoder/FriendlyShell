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

    def _complete_command_names(self, partial_cmd):
        """Autocompletion method for command names"""
        all_methods = inspect.getmembers(self, inspect.ismethod)
        retval = []
        for cur_method in all_methods:
            if cur_method[0].startswith('do_' + partial_cmd):
                retval.append(cur_method[0][3:])
        return retval

    def _get_completion_matches(self, token):
        original_line = readline.get_line_buffer()
        if readline.get_begidx() == 0:
            return self._complete_command_names(token)

        parser = self._parse_line(original_line)
        method_name = 'complete_' + parser.command
        if not hasattr(self, method_name):
            self._log.debug('No completion method for command %s', parser.command)
            return None

        tmp_method = getattr(self, method_name)
        if not inspect.ismethod(tmp_method):
            self._log.debug('\tCompletion method %s should be callable with 2 input parameters. '
                            'Check derived class')
            return None

        self._log.debug('\tCalling into auto completion method %s...', method_name)
        # TODO: Test this with empty string and such (edge cases)
        tmp_str = original_line[readline.get_begidx():]
        # TODO: should try readline.get_completer_delims() for splitting the tokens
        #       just in case someone changes it from the default 'space' character
        self._log.debug('Delimiters are %s', readline.get_completer_delims())
        complete_token = tmp_str.split(' ')[0]
        self._log.debug('\tFull token text is %s', complete_token)
        param_index = 0
        for cur_param in parser.params:
            if cur_param == complete_token:
                break
            param_index += 1
        retval = tmp_method(parser, param_index)  # TODO: Consider passing cursor location here

        if not isinstance(retval, list):
            self._log.debug('\tUser defined completion method %s must return a list of matches',
                            method_name)
            self._log.debug('\tActual returned data was %s', retval)
            return None

        return retval

    def _complete_callback(self, token, index):
        """Autocomplete method called by readline library to retrieve candidates for the a partially entered command

        NOTE: Exceptions and errors in this callback, including returning of "invalid" data like :class:`None` are
        simply ignored and treated as though there were no matches found. As such there doesn't appear to be any way
        to force the interpreter to exit when errors occur in the method.

        NOTE: Seeing as how any output to stdout or stderr result in corruption of the interactive prompt which
        uses this callback, all output messages produced by this method are redirected to debug streams so they
        can be silently logged to disk for later diagnostics.

        :param str token: the text associated with the token that is to be completed
        :param int index: index of which matching result from the possible list of matching tokens to return. So for
                          example 0 means return the first potential match for the given token from the list of
                          compatible matches. 1 means return the second potential match, etc.
        :returns: Full text for the given token which partially matches the text of the currently selected token
                  Returns None if there are no matches for the given token"""

        retval = None   # Default return value
        try:
            if index == 0:
                self._log.debug('Beginning auto-completion routine...')

            # --------------------------------- DEBUG OUTPUT -----------------------------
            # NOTE: The begidx and endidx parameters specify the start and end+1 location of the sub-string
            #       being processed
            # NOTE: If the user has placed their input cursor in the middle of the token, only the characters
            #       up to but not including the one above the cursor are returned in this parameter
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

            matches = self._get_completion_matches(token)
            if matches is None:
                return None

            if not matches:
                self._log.debug('\tNo matches for token %s found', token)
                return None

            if index >= len(matches):
                self._log.debug('Completed auto completion routine.')
                return None

            retval = matches[index]
            self._log.debug('\tReturning partial match #%s: %s', index, retval)
        except Exception as err:  # pylint: disable=broad-except
            self._log.debug('Unknown error during command completion operation: %s', err, exec_info=True)
        finally:
            return retval  # pylint: disable=lost-exception


if __name__ == "__main__":
    pass
