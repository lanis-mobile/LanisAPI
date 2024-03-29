# Example custom module

from ..module import Module


class HelloWorld(Module):
    _name = "hello_world"
    _link = None

    def get(self) -> str:
        return "Hello World!"
