import random

from logger import enable_logging

stdout = open('logs.txt', 'w+', encoding='utf-8')


@enable_logging(stdout)
class Array:
    # вывод состояния 'ДО' и 'ПОСЛЕ' для методов, не изменяющих структуру, не осуществляется
    # такие методы перечисляются в immutable_methods
    immutable_methods = ('search',)

    def __init__(self, size: int):
        self._size = size
        self._top = 0
        self._arr = [None] * size

    def __repr__(self):
        return f'{repr(self._arr)} top={self._top}, size={self._size}'

    def __getitem__(self, item):
        if 0 <= item <= self._top:
            return self._arr[item]
        else:
            raise IndexError('Out of range')

    def __setitem__(self, key, value):
        if 0 <= key <= self._top:
            self._arr[key] = value
        else:
            raise IndexError('Out of range')

    def __len__(self):
        return self._top + 1

    def search(self, value):
        for i in range(self._top + 1):
            if self._arr == value:
                return i

    def _is_filled(self):  # вызовы методов, начинающихся с '_', не отображаются в логах
        return self._top == self._size - 1

    def _allocate(self):
        new_size = self._size * 2
        self._arr.extend([None] * (new_size - self._size))
        self._size = new_size

        return self._size

    def insert(self, item):
        if self._is_filled():
            self._allocate()
        self._top += 1
        self._arr[self._top] = item

    def pop(self):
        value = self._arr[self._top]
        self._arr[self._top] = None
        self._top -= 1
        return value

    def delete(self, value):
        if i := self.search(value):
            for k in range(i, self._top):
                self._arr[k] = self._arr[k + 1]
            self._arr[self._top] = None
            self._top -= 1
            return True
        return False

    def random_fill(self):
        for i in range(self._top, self._size):
            self._arr[i] = random.randrange(100)
        self._top = self._size - 1

    def _swap(self, a, b):
        val = self._arr[a]
        self._arr[a] = self._arr[b]
        self._arr[b] = val

    def selection_sort(self):
        for outer in range(self._top):
            min = outer
            for inner in range(outer + 1, self._top + 1):
                if self._arr[inner] < self._arr[min]:
                    min = inner
            self._swap(outer, min)
        self.__class__ = SortedArray

    def insertion_sort(self):
        for outer in range(self._top + 1):
            temp = self._arr[outer]
            inner = outer
            while inner > 0 and temp < self._arr[inner - 1]:
                self._arr[inner] = self._arr[inner - 1]
                inner -= 1
            self._arr[inner] = temp


@enable_logging(stdout)
class SortedArray(Array):
    def random_fill(self):
        super(self.__class__, self).random_fill()
        self.selection_sort()

    def search(self, value):
        front, end = 0, self._top
        while front <= end:
            mid = (front + end) // 2
            if self._arr[mid] == value:
                return mid
            if self._arr[mid] < value:
                front = mid + 1
            else:
                end = mid - 1
        return front

    def insert(self, item):
        if self._is_filled():
            self._allocate()
        index = self.search(item)
        for j in range(self._top+1, index, -1):
            self._arr[j] = self._arr[j-1]
        self._arr[index] = item
        self._top += 1

    def __setitem__(self, key, value):
        raise Exception


if __name__ == '__main__':
    s_arr = SortedArray(5)
    s_arr.random_fill()
    s_arr.insert(15)
    i = s_arr.search(15)
    s_arr.pop()
    item = s_arr[len(s_arr) - 3]
    s_arr.delete(item)

    arr = Array(10)
    arr.random_fill()
    arr.selection_sort()
    arr.pop()
    pass
