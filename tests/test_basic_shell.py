from friendlyshell.basic_shell import BasicShell
import pytest


def test_init():
    obj = BasicShell()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])