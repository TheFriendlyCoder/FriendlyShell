from friendlyshell.base_shell import BaseShell
from friendlyshell.command_complete_mixin import CommandCompleteMixin
from friendlyshell.basic_logger_mixin import BasicLoggerMixin
import pytest
from mock import patch


def test_complete_command_names():
    class MyShell(BaseShell, CommandCompleteMixin, BasicLoggerMixin):
        def do_something(self):
            """Here's online help"""
            pass

        def do_something2(self):
            """Here's more help"""
            pass

        def some_other_thing(self):
            """Should not see me"""
            pass

    obj = MyShell()

    matches = obj._complete_command_names('some')
    assert len(matches) == 2
    assert "something" in matches
    assert "something2" in matches


@patch("friendlyshell.command_complete_mixin.readline")
def test_command_callback(mock_readline):
    class MyShell(BaseShell, CommandCompleteMixin, BasicLoggerMixin):
        def do_another_thing(self):
            assert False, "action method should not be called"

        def do_something(self):
            assert False, "action method should not be called"

        def complete_something(self, params, index):
            assert False, "completion method should not be called"

    input_line = "some"
    mock_readline.get_line_buffer.return_value = input_line
    mock_readline.get_begidx.return_value = 0
    mock_readline.get_endidx.return_value = len(input_line)

    obj = MyShell()

    matches = obj._complete_callback("some", 0)
    assert matches == "something"


@patch("friendlyshell.command_complete_mixin.readline")
def test_basic_callback(mock_readline):
    expected_matches = ["my_param_value"]

    class MyShell(BaseShell, CommandCompleteMixin, BasicLoggerMixin):
        completion_called = False
        def do_something(self):
            pass

        def complete_something(self, params, index):
            MyShell.completion_called = True
            assert len(params) == 1
            assert index <= len(params)

            return expected_matches

    input_line = "something my_param_"
    mock_readline.get_line_buffer.return_value = input_line
    mock_readline.get_begidx.return_value = len("something ")
    mock_readline.get_endidx.return_value = len(input_line)

    obj = MyShell()

    matches = obj._complete_callback("my_param_", 0)
    assert matches == expected_matches[0]
    assert MyShell.completion_called


@patch("friendlyshell.command_complete_mixin.readline")
def test_basic_callback_second_param(mock_readline):
    expected_matches = ["my_param_value1", "my_param_value2"]

    class MyShell(BaseShell, CommandCompleteMixin, BasicLoggerMixin):
        completion_called = False
        def do_something(self):
            pass

        def complete_something(self, params, index):
            MyShell.completion_called = True
            assert len(params) == 2
            assert index <= len(params)

            return expected_matches

    input_line = "something fubar my_param_"
    mock_readline.get_line_buffer.return_value = input_line
    mock_readline.get_begidx.return_value = len("something fubar ")
    mock_readline.get_endidx.return_value = len(input_line)

    obj = MyShell()

    matches = obj._complete_callback("my_param_", 0)
    assert matches == expected_matches[0]
    assert MyShell.completion_called

    matches = obj._complete_callback("my_param_", 1)
    assert matches == expected_matches[1]


@patch("friendlyshell.command_complete_mixin.readline")
def test_basic_callback_no_matches(mock_readline):
    class MyShell(BaseShell, CommandCompleteMixin, BasicLoggerMixin):
        completion_called = False
        def do_something(self):
            pass

        def complete_something(self, params, index):
            MyShell.completion_called = True
            assert len(params) == 1
            assert index <= len(params)

            return list()

    input_line = "something my_param_"
    mock_readline.get_line_buffer.return_value = input_line
    mock_readline.get_begidx.return_value = len("something ")
    mock_readline.get_endidx.return_value = len(input_line)

    obj = MyShell()

    matches = obj._complete_callback("my_param_", 0)
    assert matches is None
    assert MyShell.completion_called


@patch("friendlyshell.command_complete_mixin.readline")
def test_basic_callback_multiple_completions(mock_readline):
    expected_matches = ["my_param_value1", "my_param_value2"]

    class MyShell(BaseShell, CommandCompleteMixin, BasicLoggerMixin):
        call_count = 0
        def do_something(self):
            pass

        def complete_something(self, params, index):
            MyShell.call_count += 1
            assert len(params) == 1
            assert index <= len(params)

            return expected_matches

    input_line = "something my_param_"
    mock_readline.get_line_buffer.return_value = input_line
    mock_readline.get_begidx.return_value = len("something ")
    mock_readline.get_endidx.return_value = len(input_line)

    obj = MyShell()

    matches = obj._complete_callback("my_param_", 0)
    assert matches == expected_matches[0]
    assert MyShell.call_count == 1

    matches = obj._complete_callback("my_param_", 1)
    assert matches == expected_matches[1]
    # Out command completion callback should only be called once per
    # completion. The results should then be cached and reused by the
    # FShell APIs
    assert MyShell.call_count == 1

    matches = obj._complete_callback("my_param_", 2)
    assert matches is None
    assert MyShell.call_count == 1


@patch("friendlyshell.command_complete_mixin.readline")
def test_complete_first_parameter(mock_readline):
    expected_matches = ["my_param_value"]

    class MyShell(BaseShell, CommandCompleteMixin, BasicLoggerMixin):
        completion_called = False
        def do_something(self):
            pass

        def complete_something(self, params, index):
            MyShell.completion_called = True
            assert len(params) == 1
            assert index == 0
            assert params[0] == ""

            return expected_matches

    input_line = "something "
    mock_readline.get_line_buffer.return_value = input_line
    mock_readline.get_begidx.return_value = len("something ")
    mock_readline.get_endidx.return_value = len(input_line)

    obj = MyShell()

    matches = obj._complete_callback("", 0)
    assert MyShell.completion_called
    assert matches == expected_matches[0]


@patch("friendlyshell.command_complete_mixin.readline")
def test_complete_last_parameter(mock_readline):
    expected_matches = ["my_param_value"]

    class MyShell(BaseShell, CommandCompleteMixin, BasicLoggerMixin):
        completion_called = False
        def do_something(self):
            pass

        def complete_something(self, params, index):
            MyShell.completion_called = True
            assert len(params) == 2
            assert index == 1
            assert params[1] == ""

            return expected_matches

    input_line = "something FuBar "
    mock_readline.get_line_buffer.return_value = input_line
    mock_readline.get_begidx.return_value = len("something FuBar ")
    mock_readline.get_endidx.return_value = len(input_line)

    obj = MyShell()

    matches = obj._complete_callback("", 0)
    assert MyShell.completion_called
    assert matches == expected_matches[0]


@patch("friendlyshell.command_complete_mixin.readline")
def test_complete_repeated_parameter(mock_readline):
    expected_matches = ["FuBar2"]

    class MyShell(BaseShell, CommandCompleteMixin, BasicLoggerMixin):
        completion_called = False
        def do_something(self):
            pass

        def complete_something(self, params, index):
            MyShell.completion_called = True
            assert len(params) == 2
            assert index == 1
            assert params[0] == "FuBar1"
            assert params[1] == "FuBar"

            return expected_matches

    input_line = "something FuBar1 FuBar"
    mock_readline.get_line_buffer.return_value = input_line
    mock_readline.get_begidx.return_value = len("something FuBar1 ")
    mock_readline.get_endidx.return_value = len(input_line)

    obj = MyShell()

    matches = obj._complete_callback("", 0)
    assert MyShell.completion_called
    assert matches == expected_matches[0]



@patch("friendlyshell.command_complete_mixin.readline")
def test_complete_single_quote(mock_readline):
    matches = ["'My Van'"]

    class MyShell(BaseShell, CommandCompleteMixin, BasicLoggerMixin):
        completion_called = False
        def do_something(self):
            pass

        def complete_something(self, params, index):
            MyShell.completion_called = True
            assert len(params) == 1
            assert index == 0
            assert params[0] == "'My V"

            return matches

    input_line = "something 'My V"
    mock_readline.get_line_buffer.return_value = input_line
    mock_readline.get_begidx.return_value = len(input_line) - 1
    mock_readline.get_endidx.return_value = len(input_line)

    obj = MyShell()

    res = obj._complete_callback("", 0)
    assert MyShell.completion_called
    assert res == "Van'"


@patch("friendlyshell.command_complete_mixin.readline")
def test_complete_single_quote_trailing_space(mock_readline):
    matches = ["'My Van Rocks'"]

    class MyShell(BaseShell, CommandCompleteMixin, BasicLoggerMixin):
        completion_called = False
        def do_something(self):
            pass

        def complete_something(self, params, index):
            MyShell.completion_called = True
            assert len(params) == 1
            assert index == 0
            assert params[0] == "'My Van "

            return matches

    input_line = "something 'My Van "
    mock_readline.get_line_buffer.return_value = input_line
    mock_readline.get_begidx.return_value = len(input_line)
    mock_readline.get_endidx.return_value = len(input_line)

    obj = MyShell()

    res = obj._complete_callback("", 0)
    assert MyShell.completion_called
    assert res == "Rocks'"


@patch("friendlyshell.command_complete_mixin.readline")
def test_complete_double_quote(mock_readline):
    matches = ['"My Van"']

    class MyShell(BaseShell, CommandCompleteMixin, BasicLoggerMixin):
        completion_called = False
        def do_something(self):
            pass

        def complete_something(self, params, index):
            MyShell.completion_called = True
            assert len(params) == 1
            assert index == 0
            assert params[0] == '"My V'

            return matches

    input_line = 'something "My V'
    mock_readline.get_line_buffer.return_value = input_line
    mock_readline.get_begidx.return_value = len(input_line) - 1
    mock_readline.get_endidx.return_value = len(input_line)

    obj = MyShell()

    res = obj._complete_callback("", 0)
    assert MyShell.completion_called
    assert res == 'Van"'


@patch("friendlyshell.command_complete_mixin.readline")
def test_complete_double_quote_trailing_space(mock_readline):
    matches = ['"My Van Rocks"']

    class MyShell(BaseShell, CommandCompleteMixin, BasicLoggerMixin):
        completion_called = False
        def do_something(self):
            pass

        def complete_something(self, params, index):
            MyShell.completion_called = True
            assert len(params) == 1
            assert index == 0
            assert params[0] == '"My Van '

            return matches

    input_line = 'something "My Van '
    mock_readline.get_line_buffer.return_value = input_line
    mock_readline.get_begidx.return_value = len(input_line)
    mock_readline.get_endidx.return_value = len(input_line)

    obj = MyShell()

    res = obj._complete_callback("", 0)
    assert MyShell.completion_called
    assert res == 'Rocks"'


@patch("friendlyshell.command_complete_mixin.readline")
def test_no_completion_helper(mock_readline):

    class MyShell(BaseShell, CommandCompleteMixin, BasicLoggerMixin):
        def do_something(self):
            pass

    input_line = "something my_param_"
    mock_readline.get_line_buffer.return_value = input_line
    mock_readline.get_begidx.return_value = len("something") + 1
    mock_readline.get_endidx.return_value = len(input_line)

    obj = MyShell()

    matches = obj._complete_callback("my_param_", 0)
    assert matches is None


@patch("friendlyshell.command_complete_mixin.readline")
def test_ocluded_completion_helper(mock_readline):

    class MyShell(BaseShell, CommandCompleteMixin, BasicLoggerMixin):
        def do_something(self):
            pass

        @property
        def complete_something(self):
            return None

    input_line = "something my_param_"
    mock_readline.get_line_buffer.return_value = input_line
    mock_readline.get_begidx.return_value = len("something") + 1
    mock_readline.get_endidx.return_value = len(input_line)

    obj = MyShell()

    matches = obj._complete_callback("my_param_", 0)
    assert matches is None


@patch("friendlyshell.command_complete_mixin.readline")
def test_completion_method_invalid_return_type(mock_readline):

    class MyShell(BaseShell, CommandCompleteMixin, BasicLoggerMixin):
        completion_called = False
        def do_something(self):
            pass

        def complete_something(self, params, index):
            MyShell.completion_called = True
            assert len(params) == 1
            assert index <= len(params)

            # Completion methods are always expected to return a list of 0
            # or more potential matches to the parsed parameters
            return "SomeMatch"

    input_line = "something my_param_"
    mock_readline.get_line_buffer.return_value = input_line
    mock_readline.get_begidx.return_value = len("something ")
    mock_readline.get_endidx.return_value = len(input_line)

    obj = MyShell()

    matches = obj._complete_callback("my_param_", 0)
    assert matches is None
    assert MyShell.completion_called


@patch("friendlyshell.command_complete_mixin.readline")
def test_callback_exception(mock_readline):
    class MyShell(BaseShell, CommandCompleteMixin, BasicLoggerMixin):
        completion_called = False
        def do_something(self):
            pass

        def complete_something(self, params, index):
            MyShell.completion_called = True
            assert len(params) == 1
            assert index <= len(params)

            # Exceptions should never percolate up to the caller. They should
            # be caught by the API and gracefully handled by returning an
            # empty set of token matches
            raise Exception("Should not see me here")

    input_line = "something my_param_"
    mock_readline.get_line_buffer.return_value = input_line
    mock_readline.get_begidx.return_value = len("something ")
    mock_readline.get_endidx.return_value = len(input_line)

    obj = MyShell()

    matches = obj._complete_callback("my_param_", 0)
    assert matches is None
    assert MyShell.completion_called


@patch("friendlyshell.command_complete_mixin.readline")
def test_callback_interrupt(mock_readline):
    class MyShell(BaseShell, CommandCompleteMixin, BasicLoggerMixin):
        completion_called = False

        def do_something(self):
            pass

        def complete_something(self, params, index):
            MyShell.completion_called = True
            assert len(params) == 1
            assert index <= len(params)

            # Exceptions should never percolate up to the caller. They should
            # be caught by the API and gracefully handled by returning an
            # empty set of token matches
            raise KeyboardInterrupt()

    input_line = "something my_param_"
    mock_readline.get_line_buffer.return_value = input_line
    mock_readline.get_begidx.return_value = len("something ")
    mock_readline.get_endidx.return_value = len(input_line)

    obj = MyShell()

    matches = obj._complete_callback("my_param_", 0)
    assert matches is None
    assert MyShell.completion_called


@patch("friendlyshell.command_complete_mixin.readline")
def test_clear_history(mock_readline):
    class MyShell(BaseShell, CommandCompleteMixin, BasicLoggerMixin):
        pass

    input_line = "something my_param_"
    mock_readline.get_line_buffer.return_value = input_line
    mock_readline.get_begidx.return_value = len("something ")
    mock_readline.get_endidx.return_value = len(input_line)

    obj = MyShell()
    obj.do_clear_history()

    mock_readline.clear_history.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
