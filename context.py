import regex
from collections.abc import Iterable
from typing import *
import numpy as np
from enum import Enum


class Array:
    def __init__(self, array_type, init_value, size):
        _size = reversed(size)

        self.array = np.full(size, init_value, dtype=object)
        self.size = size
        self.type = array_type

    def check_index(self, index):
        if len(index) != len(self.size):
            raise IndexError('unexpected extra dimension!')

        valid = [a > b for a, b in zip(self.size, index)]
        if not all(valid):
            raise IndexError('array index too big')

    def check_valid(self, value, index: Sequence[int]):
        self.check_index(index)

        if type(value) != self.type:
            raise ValueError('input value type not matched')

    def get_elem(self, index: Sequence[int]):
        self.check_index(index)

        return self.array[index][0]

    def set_elem(self, value, index: Sequence[int]):
        self.check_valid(value, index)
        self.array[index] = value

    def __repr__(self):
        return str(self.array)


class StrArray(Array):
    def __init__(self, init_value: str, size):
        super(StrArray, self).__init__(str, init_value, size)


class IntArray(Array):
    def __init__(self, init_value: int, size):
        super(IntArray, self).__init__(int, init_value, size)


class VarType(Enum):
    STR_SCALA = 0
    INT_SCALA = 1
    STR_ARY = 2
    INT_ARY = 3


class StackElem:
    def __init__(self):
        self.return_pos = -1
        self.int_var = {}
        self.str_var = {}
        self.int_ary: Dict[str, IntArray] = {}
        self.str_ary: Dict[str, StrArray] = {}

    def set(self, var_type: VarType, key: str, value, index: Sequence[int] = None):
        if var_type == VarType.STR_SCALA and type(value) == str:
            self.str_var[key] = value
        elif var_type == VarType.INT_SCALA and type(value) == int:
            self.int_var[key] = value
        elif var_type == VarType.STR_ARY:
            if type(value) == str:
                self.str_ary[key].set_elem(value, index)
            if type(value) == StrArray:
                self.str_ary[key] = value
        elif var_type == VarType.INT_ARY:
            if type(value) == int:
                self.int_ary[key].set_elem(value, index)
            if type(value) == IntArray:
                self.int_ary[key] = value
        else:
            raise ValueError

    def exist(self, var_type: VarType, key):
        if var_type == VarType.STR_SCALA:
            return key in self.str_var.keys()
        elif var_type == VarType.INT_SCALA:
            return key in self.int_var.keys()
        elif var_type == VarType.STR_ARY:
            return key in self.str_ary.keys()
        elif var_type == VarType.INT_ARY:
            return key in self.int_ary.keys()
        else:
            raise ValueError

    def get(self, key, index: Sequence[int] = None):
        if key in self.str_var.keys():
            return self.str_var[key]
        elif key in self.int_var.keys():
            return self.int_var[key]
        elif key in self.str_ary.keys():
            return self.str_ary[key].get_elem(index)
        elif key in self.int_ary.keys():
            return self.int_ary[key].get_elem(index)
        else:
            raise ValueError

    def __repr__(self):
        return f'{self.return_pos} {self.int_var} {self.str_var} {self.int_ary} {self.str_ary}'


class Context:
    def __init__(self):
        self.stack: List[StackElem] = [StackElem()]
        self.global_elem: StackElem = StackElem()
        self.add_var('RESULT', 0, VarType.INT_SCALA)

    def push_stack(self, return_pos):
        self.stack.append(StackElem())
        self.stack[-1].return_pos = return_pos
        self.stack[-1].set(VarType.STR_ARY, 'LOCALS', StrArray("", (1000, )))
        self.stack[-1].set(VarType.INT_ARY, 'LOCAL', IntArray(0, (1000, )))

    def pop_stack(self, result=0):
        self.set_var('RESULT', result)
        self.stack.pop()

    def get_stack_elem(self) -> StackElem:
        return self.stack[-1]

    def get_global_elem(self) -> StackElem:
        return self.global_elem

    def get_var(self, var_name):
        try:
            return self.get_stack_elem().get(*parse_array(var_name))
        except ValueError:
            try:
                return self.get_global_elem().get(*parse_array(var_name))
            except ValueError:
                raise ValueError

    def set_var(self, var_name: str, value):
        # this function will not be make variable.
        # if you pass variable that does not exist, then this function will raise error.
        targets = (self.get_stack_elem(), self.get_global_elem())
        sub_targets = (VarType.STR_SCALA, VarType.INT_SCALA, VarType.STR_ARY, VarType.INT_ARY)
        parsed = parse_array(var_name)
        var_type = VarType(0)
        for t in targets:
            for s in sub_targets:
                if t.exist(s, parsed[0]):
                    t.set(s, parsed[0], value, parsed[1])
                    return

        raise ValueError

    def add_var(self, var_name: str, value, var_type: VarType, local=False):
        try:
            self.get_var(var_name)
        except ValueError:
            if local:
                self.get_stack_elem().set(var_type, var_name, value)
            else:
                self.get_global_elem().set(var_type, var_name, value)

        else:
            raise ValueError("cannot add existing variable")

    def __repr__(self):
        return f'{str(self.stack)} {str(self.global_elem)}'


def parse_array(string: str):
    result = string.split(':')
    if len(result) != 0:
        return result[0], [int(i) for i in result[1:]]
    else:
        return result[0], None


if __name__ == '__main__':
    # test
    a = Array(int, 0, (2, 2))
    print(a)
    a.set_elem(1, (1, 1))
    print(a)

    b = Array(str, "a", (2, 2))
    print(b)
    b.set_elem("b", (0, 0))
    print(b)
    print(b.get_elem((1, 1)))

    c = Context()
    c.add_var("asdf", 1, VarType.INT_SCALA)
    print(c.get_var("asdf"))

    c.add_var("array", IntArray(0, (10, )), VarType.INT_ARY)
    print(c.get_var("array"))
    c.set_var("asdf", 15)
    print(c.get_var("asdf"))
    ar = c.get_var("array")
    ar.set_elem(20, (2, ))
    c.set_var("array", ar)
    print(c.get_var("array"))
