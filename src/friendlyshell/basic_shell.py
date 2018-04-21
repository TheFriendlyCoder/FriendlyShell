"""Generic interactive shell with online help and auto completion support"""
from friendlyshell.base_shell import BaseShell
from friendlyshell.shell_help_mixin import ShellHelpMixin
from friendlyshell.command_complete_mixin import \
    CommandCompleteMixin, auto_complete_manager
from friendlyshell.basic_logger_mixin import BasicLoggerMixin


class BasicShell(
        BasicLoggerMixin, BaseShell, ShellHelpMixin, CommandCompleteMixin):
    """Friendly Shell with basic online help and command auto-completion"""
    def __init__(self):  # pylint: disable=useless-super-delegation
        super(BasicShell, self).__init__()

    def run(self):
        """Entry point method that launches our interactive shell.

        Input will be processed from the console to execute commands, until
        termination of the shell is invoked by the user via 'exit' or some
        other failure event.
        """

        # Configure our auto-completion callback
        with auto_complete_manager(self.complete_key, self._complete_callback):
            super(BasicShell, self).run()


if __name__ == "__main__":
    pass
