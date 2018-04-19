import logging
from friendlyshell.base_shell import BaseShell
from friendlyshell.shell_help_mixin import ShellHelpMixin
from mock import patch
import pytest


def test_list_commands(caplog):
    class MyShell (BaseShell, ShellHelpMixin):
        def do_something(self):
            """Here's online help for my 'something' command"""
            pass

    obj = MyShell()

    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = ['help', 'exit']
        obj.run()
        assert 'exit' in caplog.text
        assert 'help' in caplog.text
        assert 'something' in caplog.text
        assert obj.do_something.__doc__ in caplog.text


def test_missing_help(caplog):
    class MyShell(BaseShell, ShellHelpMixin):
        def do_something(self):
            """Here's online help"""
            pass

    obj = MyShell()

    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = ['help something', 'exit']
        obj.run()
        assert 'No online help' in caplog.text


def test_command_help(caplog):
    expected_help = "Here's my verbose help for something..."

    class MyShell(BaseShell, ShellHelpMixin):
        def do_something(self):
            """Here's online help"""
            pass

        def help_something(self):
            return expected_help

    obj = MyShell()

    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = ['help something', 'exit']
        obj.run()
        assert expected_help in caplog.text


def test_help_help(caplog):
    class MyShell(BaseShell, ShellHelpMixin):
        pass

    obj = MyShell()

    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = ['help help', 'exit']
        obj.run()
        assert "Online help generation tool" in caplog.text


def test_occluded_help(caplog):

    class MyShell(BaseShell, ShellHelpMixin):
        def do_something(self):
            """Here's online help"""
            pass

        help_something = "Should not see me"

    obj = MyShell()

    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = ['help something', 'exit']
        obj.run()
        assert "Error: " in caplog.text


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
