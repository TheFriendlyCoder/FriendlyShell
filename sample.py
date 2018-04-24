#!/usr/bin/env python
from friendlyshell.basic_shell import BasicShell


class MySubShell(BasicShell):
    def do_sub_op(self):
        print("Child sub op1")


class MyShell (BasicShell):
    def do_parent_op(self):
        print("Parent op1")

    def do_subshell(self):
        tmp = MySubShell(parent=self)
        tmp.prompt = "(child)> "
        return tmp.run(input_stream=self.input_stream)


if __name__ == "__main__":
    obj = MyShell()

    # obj.run()
    # exit()
    with open("test.fsh", "r") as fh:
        obj.run(input_stream=fh)
