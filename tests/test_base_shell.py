from __future__ import unicode_literals
import logging
from friendlyshell.base_shell import BaseShell
from friendlyshell.basic_logger_mixin import BasicLoggerMixin
from mock import patch
import pytest
from io import StringIO


def test_defaults():
    class MyShell(BasicLoggerMixin, BaseShell):
        pass
    obj = MyShell()

    assert obj.prompt == '> '


def test_basic_parseline():
    class MyShell(BasicLoggerMixin, BaseShell):
        pass
    obj = MyShell()
    exp_command = "MyCommand"
    exp_param1 = "Fu"
    exp_param2 = "Bar"

    res = obj._parse_line('{0} {1} {2}'.format(exp_command, exp_param1, exp_param2))

    assert res.command == exp_command
    assert len(res.params) == 2
    assert res.params[0] == exp_param1
    assert res.params[1] == exp_param2


def test_find_exit_command():
    class MyShell(BasicLoggerMixin, BaseShell):
        pass
    obj = MyShell()

    res = obj._find_command('exit')

    assert res is not None
    assert res.__name__ == 'do_exit'
    assert res == obj.do_exit


def test_find_missing_command():
    class MyShell(BasicLoggerMixin, BaseShell):
        pass
    obj = MyShell()

    res = obj._find_command('fubar')

    assert res is None


def test_simple_run_exit():
    class MyShell(BasicLoggerMixin, BaseShell):
        pass
    obj = MyShell()
    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.return_value = 'exit'
        obj.run()
        MockInput.assert_called_once()


@pytest.mark.timeout(5)
def test_simple_run_input_stream(caplog):
    expected_message = "My output from my command"
    class MyShell(BasicLoggerMixin, BaseShell):
        def do_my_cmd(self):
            self.info(expected_message)

    obj = MyShell()
    in_stream = StringIO("""my_cmd
    exit""")

    obj.run(input_stream=in_stream)
    assert expected_message in caplog.text

@pytest.mark.timeout(5)
def test_run_input_stream_no_exit(caplog):
    expected_message = "My output from my command"

    class MyShell(BasicLoggerMixin, BaseShell):
        def do_my_cmd(self):
            self.info(expected_message)

    obj = MyShell()
    in_stream = StringIO("""my_cmd""")

    obj.run(input_stream=in_stream)
    assert expected_message in caplog.text


@pytest.mark.timeout(5)
def test_run_input_stream_nested_exit(caplog):
    expected_message1 = "My output from my command"
    expected_message2 = "My Subcommand Output"

    class SubShell(BasicLoggerMixin, BaseShell):
        def do_my_sub_op(self):
            self.info(expected_message2)

    class MyShell(BasicLoggerMixin, BaseShell):
        def do_my_cmd(self):
            self.info(expected_message1)

        def do_my_subshell(self):
            tmp = SubShell()
            tmp.run(input_stream=self.input_stream)

    obj = MyShell()
    in_stream = StringIO("""my_cmd
    my_subshell
    my_sub_op
    exit""")

    obj.run(input_stream=in_stream)
    assert expected_message1 in caplog.text
    assert expected_message2 in caplog.text


@pytest.mark.timeout(5)
def test_run_input_stream_subshell_close(caplog):
    expected_message1 = "My output from my command"
    expected_message2 = "My Subcommand Output"
    expected_message3 = "Here's the other parents output"

    class SubShell(BasicLoggerMixin, BaseShell):
        def do_my_sub_op(self):
            self.info(expected_message2)

    class MyShell(BasicLoggerMixin, BaseShell):
        def do_my_cmd(self):
            self.info(expected_message1)

        def do_my_other_cmd(self):
            self.info(expected_message3)

        def do_my_subshell(self):
            tmp = SubShell()
            tmp.run(input_stream=self.input_stream)

    obj = MyShell()
    in_stream = StringIO("""my_cmd
    my_subshell
    my_sub_op
    close
    my_other_cmd
    exit""")

    obj.run(input_stream=in_stream)
    assert expected_message1 in caplog.text
    assert expected_message2 in caplog.text
    assert expected_message3 in caplog.text

def test_simple_nested_exit():
    class SubShell(BasicLoggerMixin, BaseShell):
        pass
    class MyShell(BasicLoggerMixin, BaseShell):
        def do_mysubshell (self):
            temp = SubShell(parent=self)
            return temp.run()

    obj = MyShell()
    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = ['mysubshell', 'exit']
        obj.run()
        assert MockInput.call_count == 2


def test_simple_run_close():
    class MyShell(BasicLoggerMixin, BaseShell):
        pass
    obj = MyShell()
    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.return_value = 'close'
        obj.run()
        MockInput.assert_called_once()


def test_invalid_run(caplog):
    caplog.set_level(logging.INFO)
    class MyShell(BasicLoggerMixin, BaseShell):
        pass
    obj = MyShell()
    with patch('friendlyshell.base_shell.input') as MockInput:
        # Return 2 different commands to execute - the first invalid, and the second to terminate the shell
        MockInput.side_effect = ['exit!', 'exit']
        obj.run()
        assert MockInput.call_count == 2
        assert 'Parsing error:' in caplog.text


def test_keyboard_interrupt():
    class MyShell(BasicLoggerMixin, BaseShell):
        pass
    obj = MyShell()
    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = KeyboardInterrupt()
        obj.run()
        MockInput.assert_called_once()


def test_unhandled_exception(caplog):
    caplog.set_level(logging.INFO)
    class MyShell(BasicLoggerMixin, BaseShell):
        pass
    obj = MyShell()
    with patch('friendlyshell.base_shell.input') as MockInput:
        expected_error = "Some crazy error"
        MockInput.side_effect = Exception(expected_error)
        obj.run()
        MockInput.assert_called_once()
        msg = 'Unexpected error during input sequence: ' + expected_error
        assert msg in caplog.text


def test_missing_command(caplog):
    caplog.set_level(logging.INFO)
    expected_error = "Command not found"
    expected_command_name = "fubar"
    class test_class(BasicLoggerMixin, BaseShell):
        pass
    obj = test_class()
    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = [expected_command_name, 'exit']
        obj.run()
        assert MockInput.call_count == 2
        assert expected_error in caplog.text
        assert expected_command_name in caplog.text

def test_command_exception(caplog):
    caplog.set_level(logging.INFO)
    expected_error = "Some weird thing just happened"

    class test_class(BasicLoggerMixin, BaseShell):
        def do_something(self):
            raise Exception(expected_error)

    obj = test_class()
    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = ['something', 'exit']
        obj.run()
        assert MockInput.call_count == 2
        assert expected_error in caplog.text


def test_command_with_params():
    expected_param = "FuBar"

    class test_class(BasicLoggerMixin, BaseShell):
        test_function_ran = False
        def do_something(self, my_param):
            assert my_param == expected_param
            self.test_function_ran = True

    obj = test_class()
    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = ['something ' + expected_param, 'exit']
        obj.run()
        assert MockInput.call_count == 2
        assert obj.test_function_ran


def test_command_too_many_params():
    expected_params = "Fu Bar"

    class test_class(BasicLoggerMixin, BaseShell):
        def do_something(self, my_param):
            pytest.fail("Test method should not be invoked")

    obj = test_class()
    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = ['something ' + expected_params, 'exit']
        obj.run()
        assert MockInput.call_count == 2


def test_command_missing_params():

    class test_class(BasicLoggerMixin, BaseShell):
        def do_something(self, my_param1, my_param2):
            pytest.fail("Test method should not be invoked")

    obj = test_class()

    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = ['something first', 'exit']
        obj.run()
        assert MockInput.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
