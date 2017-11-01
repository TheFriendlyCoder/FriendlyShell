from friendlyshell.base_shell import BaseShell
from friendlyshell.command_complete_mixin import CommandCompleteMixin


def test_complete_command_names():
    class MyShell(BaseShell, CommandCompleteMixin):
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


if __name__ == "__main__":
    pass
