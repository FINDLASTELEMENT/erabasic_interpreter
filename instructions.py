from typing import *
from context import Context


class Node:
    def __init__(self):
        pass

    def evaluate(self, context):
        pass


class ValuedNode(Node):
    def __init__(self):
        super().__init__()

    def evaluate(self, context: Context) -> Tuple[Any, Any]:
        result = None
        return context, result


class Instruction(Node):
    def __init__(self):
        super().__init__()

    def evaluate(self, context: Context):
        pass


class Block(Node):
    def __init__(self, first: Node, second: Node):
        super().__init__()
        self.nodes = [first, second]

    def evaluate(self, context: Context):
        for n in self.nodes:
            context = n.evaluate(context)
        return context


class Operator(ValuedNode):
    def __init__(self, function: Callable[[Sequence], Any], args: Tuple[ValuedNode, ...]):
        super(Operator, self).__init__()
        self.function = function
        self.args = args

    def evaluate(self, context: Context) -> Tuple[Any, Any]:
        values = [a.evaluate(context) for a in self.args]
        return context, self.function(values)


class Variable(ValuedNode):
    def __init__(self, name):
        super(Variable, self).__init__()
        self.name = name

    def evaluate(self, context):
        return context, None


class Literal(ValuedNode):
    def __init__(self, value):
        super(Literal, self).__init__()
        self.value = value

    def evaluate(self, context: Context):
        return context, self.value


class String(Operator):
    def __init__(self, first: ValuedNode, second: ValuedNode):
        super().__init__(lambda x: x[0] + x[1], (first, second))

    def evaluate(self, context: Context):
        return super(String, self).evaluate(context)


class Print(Instruction):
    def __init__(self, string: String):
        super().__init__()
        self.string = string

    def evaluate(self, context: Context):
        print(self.string.evaluate(context))
        return context


def ternary(args: Sequence):
    if args[0]:
        return args[1]
    else:
        return args[2]
