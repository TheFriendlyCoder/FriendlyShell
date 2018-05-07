import logging
from friendlyshell.base_shell import BaseShell
from friendlyshell.shell_help_mixin import ShellHelpMixin
from friendlyshell.basic_logger_mixin import BasicLoggerMixin
from mock import patch
import pytest


def test_list_commands(caplog):
    caplog.set_level(logging.INFO)
    class MyShell (BasicLoggerMixin, BaseShell, ShellHelpMixin):
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
        assert '!' in caplog.text
        assert obj.do_something.__doc__ in caplog.text


def test_help_missing_command(caplog):
    caplog.set_level(logging.INFO)
    class MyShell (BasicLoggerMixin, BaseShell, ShellHelpMixin):
        pass

    obj = MyShell()

    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = ['help something', 'exit']
        obj.run()
        assert "Command does not exist: something" in caplog.text


def test_missing_help(caplog):
    caplog.set_level(logging.INFO)
    class MyShell(BasicLoggerMixin, BaseShell, ShellHelpMixin):
        def do_something(self):
            pass

    obj = MyShell()

    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = ['help something', 'exit']
        obj.run()
        assert 'No online help' in caplog.text

def test_default_help(caplog):
    caplog.set_level(logging.INFO)
    class MyShell(BasicLoggerMixin, BaseShell, ShellHelpMixin):
        def do_something(self):
            """Here's online help"""
            pass

    obj = MyShell()

    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = ['help something', 'exit']
        obj.run()
        assert "Here's online help" in caplog.text


def test_help_alias(caplog):
    caplog.set_level(logging.INFO)

    class MyShell(BasicLoggerMixin, BaseShell, ShellHelpMixin):
        def do_something(self):
            """Here's online help"""
            pass

    obj = MyShell()

    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = ['? something', 'exit']
        obj.run()
        assert "Here's online help" in caplog.text


def test_command_help(caplog):
    caplog.set_level(logging.INFO)
    expected_help = "Here's my verbose help for something..."

    class MyShell(BasicLoggerMixin, BaseShell, ShellHelpMixin):
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
    caplog.set_level(logging.INFO)
    class MyShell(BasicLoggerMixin, BaseShell, ShellHelpMixin):
        pass

    obj = MyShell()

    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = ['help help', 'exit']
        obj.run()
        assert "Online help generation tool" in caplog.text


def test_occluded_help(caplog):
    caplog.set_level(logging.INFO)
    class MyShell(BasicLoggerMixin, BaseShell, ShellHelpMixin):
        def do_something(self):
            """Here's online help"""
            pass

        help_something = "Should not see me"

    obj = MyShell()

    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = ['help something', 'exit']
        obj.run()
        assert "Error: " in caplog.text

def test_occluded_command(caplog):
    caplog.set_level(logging.INFO)
    class MyShell (BasicLoggerMixin, BaseShell, ShellHelpMixin):
        do_something = "Hello"

    obj = MyShell()

    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = ['help something', 'exit']
        obj.run()
        assert "Error: " in caplog.text
if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
