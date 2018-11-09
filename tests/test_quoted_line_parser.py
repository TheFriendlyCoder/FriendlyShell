from friendlyshell.command_parsers import default_line_parser
import pytest


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
    assert res.params[0] == '"param1"'


def test_single_quoted_param():
    parser = default_line_parser()
    res = parser.parseString("MyCommand 'param1'")

    assert res is not None
    assert res.command == 'MyCommand'
    assert len(res.params) == 1
    assert res.params[0] == "'param1'"


def test_params_with_spaces():
    parser = default_line_parser()
    res = parser.parseString("MyCommand 'param with spaces'")

    assert res is not None
    assert res.command == 'MyCommand'
    assert len(res.params) == 1
    assert res.params[0] == "'param with spaces'"


def test_params_with_nested_quotes():
    parser = default_line_parser()
    res = parser.parseString('MyCommand "param with \'quotes\'"')

    assert res is not None
    assert res.command == 'MyCommand'
    assert len(res.params) == 1
    assert res.params[0] == "\"param with 'quotes'\""


def test_params_with_nested_double_quotes():
    parser = default_line_parser()
    res = parser.parseString("MyCommand 'param with \"double quotes\"'")

    assert res is not None
    assert res.command == 'MyCommand'
    assert len(res.params) == 1
    assert res.params[0] == '\'param with "double quotes"\''


def test_last_param_quoted():
    parser = default_line_parser()
    res = parser.parseString("MyCommand first_param second_param \"third param\"")
    assert res is not None
    assert res.command == "MyCommand"
    assert len(res.params) == 3
    assert res.params[0] == "first_param"
    assert res.params[1] == "second_param"
    assert res.params[2] == "\"third param\""


def test_nested_quoted_param():
    parser = default_line_parser()
    res = parser.parseString("MyCommand first_param \"second param\" third_param")
    assert res is not None
    assert res.command == "MyCommand"
    assert len(res.params) == 3
    assert res.params[0] == "first_param"
    assert res.params[1] == "\"second param\""
    assert res.params[2] == "third_param"


def test_mixed_param_quotes():
    parser = default_line_parser()
    res = parser.parseString("MyCommand first_param \"second param\" 'third param' fourth_param")
    assert res is not None
    assert res.command == "MyCommand"
    assert len(res.params) == 4
    assert res.params[0] == "first_param"
    assert res.params[1] == "\"second param\""
    assert res.params[2] == "'third param'"
    assert res.params[3] == "fourth_param"

if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
