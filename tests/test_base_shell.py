import logging
from friendlyshell.base_shell import BaseShell
from friendlyshell.basic_logger_mixin import BasicLoggerMixin
from mock import patch
import pytest


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


def test_exit_command():
    class MyShell(BasicLoggerMixin, BaseShell):
        pass
    obj = MyShell()

    assert obj._done is False

    obj.do_exit()

    assert obj._done is True


def test_simple_run():
    class MyShell(BasicLoggerMixin, BaseShell):
        pass
    obj = MyShell()
    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.return_value = 'exit'
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
