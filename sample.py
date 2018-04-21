#!/usr/bin/env python
from friendlyshell.basic_shell import BasicShell


class MyShell (BasicShell):
    def do_mycmd(self):
        print("In my cmd")


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    obj = MyShell()
    obj.run()