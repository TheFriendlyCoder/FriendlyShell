"""Mixin class that adds online help to a friendly shell"""
import inspect
import tabulate


class ShellHelpMixin(object):
    """Mixin class to be added to any friendly shell to add online help"""
    def __init__(self):  # pylint: disable=useless-super-delegation
        super(ShellHelpMixin, self).__init__()

    def _list_commands(self):
        """Displays a list of supported commands"""
        all_methods = inspect.getmembers(self, inspect.ismethod)
        command_list = {
            'Command': [],
            'Description': [],
            'Extended Help': [],
        }
        for cur_method in all_methods:
            # Each method definition is a 2-tuple, with the first element being
            # the name of the method and the second a reference to the method
            # object
            method_name = cur_method[0]
            method_obj = cur_method[1]

            self._log.debug('Checking for command method %s', method_name)

            # Methods that start with 'do_' are interpreted as command operator
            if method_name.startswith('do_'):
                self._log.debug("Found a do command %s", method_name)
                # Extrapolate the command name by removing the 'do_' prefix
                cmd_name = cur_method[0][3:]

                # Generate our help data
                command_list['Command'].append(cmd_name)
                doc_string = inspect.getdoc(method_obj) or ''
                command_list['Description'].append(doc_string.split('\n')[0])

                if hasattr(self, method_name.replace('do_', 'help_')):
                    self._log.debug(
                        "Found an associated help method %s",
                        method_name.replace('do_', 'help_')
                    )
                    # NOTE:
                    # For the sake of online help, we'll assume that class
                    # attributes with 'help_' in their name are methods which
                    # can be called to display verbose help. We can add
                    # verification logic for this elsewhere when necessary
                    command_list['Extended Help'].append(
                        '`' + self.prompt + 'help ' + cmd_name + '`')
                else:
                    command_list['Extended Help'].append('N/A')

        self._log.info(tabulate.tabulate(command_list, headers="keys"))

    def do_help(self, arg=None):
        """Online help generation (this command)

        :param str arg:
            Optional command to generate online help for.
            If not defined, show a list of commands
        """
        if arg is None:
            self._log.debug("Showing help for available commands...")
            self._list_commands()
            return

        method_name = 'help_' + arg
        if not hasattr(self, method_name):
            self._log.info('No online help for command "%s"', arg)

            cmd_method_name = 'do_' + arg
            if hasattr(self, cmd_method_name):
                docs = self._log.getattr(self, 'do_' + arg).__doc__
                self._log.info(docs.split('\n')[0])
            return

        func = getattr(self, method_name)
        if not inspect.ismethod(func):
            self._log.error(
                'Error: definition "%s" in derived class must be a method. '
                'Check implementation',
                method_name)
            return

        self._log.info(func())

    def complete_help(self, parser, parameter_index, cursor_position):
        """Automatic completion method for the 'help' command"""
        return self._complete_command_names(
            parser.params[parameter_index][:cursor_position])

    def help_help(self):
        """Generates inline help for the 'help' command"""
        retval = [
            "Online help generation tool",
            "Running 'help' with no parameters displays a list of supported "
            "commands",
            "Passing any supported command to 'help' provides detailed help on "
            "the command",
            "example: " + self.prompt + "help exit"
            ]
        return '\n'.join(retval)
