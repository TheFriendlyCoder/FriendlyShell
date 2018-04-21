from friendlyshell.basic_shell import BasicShell
import pytest
from mock import patch


def test_init():
    obj = BasicShell()

    with patch('friendlyshell.base_shell.input') as MockInput:
        MockInput.side_effect = ['exit!', 'exit']
        obj.run()
        assert MockInput.call_count == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])