import sys
from collections import deque
import functools
import inspect
from typing import Optional, Any
from dataclasses import dataclass


log_deque = deque()
root_call = False


@dataclass
class LogOperation:
    operation: str
    before: Optional[str]
    after: Optional[str]
    stream: Any
    immutable: bool = False

    def display(self, nested_call=False):
        out = ''
        if not nested_call:
            out += f'{"-" * 50}\n'
        indent = 4 if nested_call else 0
        sym = '↳' if nested_call else '→'
        out += f"{' ' * indent} {sym} {self.operation}"
        if not self.immutable:
            out += f"\n{' ' * (indent + 3)}Before: {self.before}\n" \
                   f"{' ' * (indent + 3)}After: {self.after}"
        print(out + '\n', file=self.stream)


def log_method(stdout=sys.stdout):
    def decorated(operation):
        @functools.wraps(operation)
        def wrap(*args, **kwargs):
            global root_call
            itself_is_root = False
            if not root_call:
                root_call, itself_is_root = True, True
            args_str = parse_args(operation, args)
            instance = args[0]
            class_name = instance.__class__.__name__
            operation_cls_name = operation.__qualname__.split('.')[0]
            is_super_call = instance.__class__.__name__ != operation_cls_name
            repr_before = repr(instance)
            result = operation(*args, **kwargs)
            repr_after = repr(instance)
            operation_header = f'Called <{class_name}>.{operation.__name__}({args_str})'
            if is_super_call:
                operation_header += f', base method of <{operation_cls_name}>'
            log_operation = LogOperation(operation_header, repr_before, repr_after, stdout)
            log_operation.immutable = operation.__name__ in instance.__class__.immutable_methods
            if itself_is_root:
                log_operation.display()
                while log_deque:
                    log_deque.popleft().display(nested_call=True)
                root_call = False
            else:
                log_deque.append(log_operation)
            return result
        return wrap
    return decorated


def parse_args(operation, args):
    args_str = ''
    arg_names = inspect.getfullargspec(operation).args
    for i in range(1, len(arg_names)):
        arg_name, arg_val = arg_names[i], args[i]
        args_str += f'{arg_name}={arg_val},'
    return args_str.removesuffix(",")


def enable_logging(stdout=sys.stdout):
    def decorated(cls: type):
        """ Функция-декоратор для класса, добавляющая логирование методам, имя которых не начинается на _"""
        logged_funcs = {}
        attrs = dict(cls.__dict__)
        for attr_name, attr_value in attrs.items():
            if inspect.isfunction(attr_value) and not attr_name.startswith('_'):
                logged_funcs[attr_name] = log_method(stdout)(attr_value)
        attrs.update(logged_funcs)
        cls = type(cls.__name__, cls.__bases__, attrs)
        return cls
    return decorated
