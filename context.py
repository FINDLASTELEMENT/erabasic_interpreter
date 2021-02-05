import regex
from collections.abc import Iterable
from typing import *
import numpy as np


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

    def check_valid(self, value, index: Iterable[int]):
        self.check_index(index)

        if type(value) != self.type:
            raise ValueError('input value type not matched')

    def get_elem(self, index: Iterable[int]):
        self.check_index(index)

        return self.array[index]

    def set_elem(self, value, index: Iterable[int]):
        self.check_valid(value, index)
        self.array[index] = value

    def __repr__(self):
        return str(self.array)


class StackElem:
    def __init__(self):
        self.return_pos = -1
        self.int_var = {}
        self.str_var = {}
        self.int_ary: Dict[str, Array] = {}
        self.str_ary: Dict[str, Array] = {}

    def __repr__(self):
        return f'{self.return_pos} {self.int_var} {self.str_var} {self.int_ary} {self.str_ary}'


class Context:
    def __init__(self):
        self.stack: List[StackElem] = [StackElem()]
        self.global_elem: StackElem = StackElem()

    def push_stack(self, return_pos):
        self.stack.append(StackElem())
        self.stack[-1].return_pos = return_pos

    def pop_stack(self):
        self.stack.pop()

    def get_stack_elem(self) -> StackElem:
        return self.stack[-1]

    def get_global_elem(self) -> StackElem:
        return self.global_elem

    def __repr__(self):
        return f'{str(self.stack)} {str(self.global_elem)}'


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

