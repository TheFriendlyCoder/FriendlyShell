#!/usr/bin/env python
from friendlyshell.basic_shell import BasicShell


class MyShell (BasicShell):
    def do_mycmd(self):
        print("In my cmd")


if __name__ == "__main__":
    obj = MyShell()
    obj.run()