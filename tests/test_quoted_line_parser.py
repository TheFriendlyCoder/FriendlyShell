from friendlyshell.command_parsers import default_line_parser
import pytest
import pyparsing as pp


def test_no_params():
    parser = default_line_parser()
    res = parser.parseString('MyCommand')

    assert res is not None
    assert res.command == 'MyCommand'
    assert len(res.params) == 0


def test_no_params_whitespace():
    parser = default_line_parser()
    res = parser.parseString('     MyCommand    ')

    assert res is not None
    assert res.command == 'MyCommand'
    assert len(res.params) == 0


def test_one_param():
    parser = default_line_parser()
    res = parser.parseString('MyCommand param1')

    assert res is not None
    assert res.command == 'MyCommand'
    assert len(res.params) == 1
    assert res.params[0] == 'param1'


def test_two_params():
    parser = default_line_parser()
    res = parser.parseString('MyCommand param1 param2')

    assert res is not None
    assert res.command == 'MyCommand'
    assert len(res.params) == 2
    assert res.params[0] == 'param1'
    assert res.params[1] == 'param2'


def test_params_whitespace():
    parser = default_line_parser()
    res = parser.parseString('   MyCommand      param1   param2')

    assert res is not None
    assert res.command == 'MyCommand'
    assert len(res.params) == 2
    assert res.params[0] == 'param1'
    assert res.params[1] == 'param2'


def test_quoted_param():
    parser = default_line_parser()
    res = parser.parseString('MyCommand "param1"')

    assert res is not None
    assert res.command == 'MyCommand'
    assert len(res.params) == 1
    assert res.params[0] == 'param1'


def test_single_quoted_param():
    parser = default_line_parser()
    res = parser.parseString("MyCommand 'param1'")

    assert res is not None
    assert res.command == 'MyCommand'
    assert len(res.params) == 1
    assert res.params[0] == 'param1'


def test_params_with_spaces():
    parser = default_line_parser()
    res = parser.parseString("MyCommand 'param with spaces'")

    assert res is not None
    assert res.command == 'MyCommand'
    assert len(res.params) == 1
    assert res.params[0] == 'param with spaces'


def test_params_with_nested_quotes():
    parser = default_line_parser()
    res = parser.parseString('MyCommand "param with \'quotes\'"')

    assert res is not None
    assert res.command == 'MyCommand'
    assert len(res.params) == 1
    assert res.params[0] == "param with 'quotes'"


def test_params_with_nested_double_quotes():
    parser = default_line_parser()
    res = parser.parseString("MyCommand 'param with \"double quotes\"'")

    assert res is not None
    assert res.command == 'MyCommand'
    assert len(res.params) == 1
    assert res.params[0] == 'param with "double quotes"'


def test_invalid_command_parsing():
    parser = default_line_parser()
    # Invalid command with an exclamation mark in it

    with pytest.raises(pp.ParseException):
        res = parser.parseString('Hello_there!')
        print(res.command)
        print(res.params)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
