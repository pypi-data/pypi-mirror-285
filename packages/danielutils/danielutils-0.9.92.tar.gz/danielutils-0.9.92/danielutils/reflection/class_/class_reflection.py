import inspect, re
from typing import Any, List as List, Optional, Tuple as Tuple
from dataclasses import dataclass
from ..interpreter import get_python_version

argument_kwargs = dict(frozen=True)
FunctionDeclaration_kwargs = dict(frozen=True)
if get_python_version() >= (3, 9):
    from builtins import list as List, tuple as Tuple  # type:ignore

elif get_python_version() >= (3, 10):
    argument_kwargs.update(slots=True)
    FunctionDeclaration_kwargs.update(slots=True)


def get_explicitly_declared_functions(cls: type) -> List[str]:
    """
    Returns the names of the functions that are explicitly declared in a class.

    This function does not return inherited functions.

    Args:
        cls (type): The class to inspect.

    Returns:
        list[str]: A list of names of the functions explicitly declared in the class.
    """
    return [func for func, val in inspect.getmembers(cls, predicate=inspect.isfunction)]


def get_mro(obj: Any) -> List[type]:
    """returns the mro of an object

    Args:
        obj (Any): any object, instance or class

    Returns:
        list[type]: the resulting mro for the object
    """
    if isinstance(obj, type):
        return obj.mro()
    return get_mro(obj.__class__)


@dataclass(**argument_kwargs)
class Argument:
    name: str
    type: Optional[str]
    default: Optional[str]


func_pattern = re.compile(
    r"(.*def[\s\\]*?(\w+)[\s\\]*?\(([\w\W]*?)\)(?:[\s\\]*?->[\s\\]*?([\w\(\)\[\]\,]+))?[\s\\]*?:)",
    flags=re.MULTILINE)
not_whitespace_pattern = re.compile(r"\S+", flags=re.MULTILINE)
arg_pattern = re.compile(r"([\w\*\/]+)(?:\s*?:\s*?([\w\[\]\(\)\,]+))?(?:\s*?=\s*?(.+))?")
class_pattern = re.compile(r"\s*class\s+?\w+\s*?(?:\((.*)\))?\s*?:")


def split_args(args: str) -> List[str]:
    from danielutils import Stack
    res = []
    s: Stack[str] = Stack()
    start = 0
    for i, c in enumerate(args):
        if c not in {'(', ')', '[', ']', ','}:
            continue
        if c in {'(', "["}:
            s.push(c)
        elif c in {')', ']'}:
            s.pop()
        else:
            if s.is_empty():
                res.append(args[start:i])
                start = i + 1

    res.append(args[start:len(args)])
    return res


def remove_whitespace(text: str) -> str:
    return "".join(not_whitespace_pattern.findall(text.strip())).replace("\\", "")


@dataclass(**FunctionDeclaration_kwargs)
class FunctionDeclaration:
    name: str
    arguments: Tuple[Argument, ...]
    return_type: Optional[str]
    decorators: Optional[List[str]] = None
    generics: Optional[Tuple[str]] = None

    def duplicate(self, **override_kwargs) -> 'FunctionDeclaration':
        dct = dict(
            name=self.name,
            arguments=self.arguments,
            return_type=self.return_type,
            decorators=self.decorators,
            generics=self.generics,
        )
        dct.update(override_kwargs)
        return FunctionDeclaration(**dct)

    @property
    def has_generics(self) -> bool:
        return self.generics is not None and len(self.generics) > 0

    @staticmethod
    def get_declared_functions(cls) -> List['FunctionDeclaration']:
        """will yield the names of all the functions declared inside a class

        Yields:
            Generator[str, None, None]: yields str values which are names of declared functions
        """
        if not isinstance(cls, type):
            raise TypeError('cls must be a Class')
        src = inspect.getsource(cls)
        bases = [o for o in map(remove_whitespace, class_pattern.findall(src)) if len(o) > 0]
        parameters = []
        for base in bases:
            if '[' in base and ']' in base:
                s = base[base.index('[') + 1:base.rindex(']')]
                for arg in split_args(s):
                    if len(arg) == 1:
                        parameters.append(arg)
        res = []
        for code, name, args, ret in func_pattern.findall(src):
            name: str = name.strip()
            args: Optional[str] = remove_whitespace(args) if args is not None else None
            arguments = []
            if args is not None:
                for arg in split_args(args):
                    arguments.append(Argument(*arg_pattern.match(remove_whitespace(arg)).groups()))
            ret: Optional[str] = ret.strip() if ret is not None and len(ret) != 0 else None
            res.append(FunctionDeclaration(name, tuple(arguments), ret, decorators=None, generics=tuple(parameters)))

        return res

    def __eq__(self, other) -> bool:
        if not isinstance(other, FunctionDeclaration):
            return False

        return self.name == other.name and self.arguments == self.arguments and self.return_type == other.return_type

    def __hash__(self) -> int:
        return hash((self.name, self.arguments, self.return_type))

    def __repr__(self) -> str:
        args = ",\n\t\t".join(map(str, self.arguments))
        return f"{self.__class__.__name__}(\n" \
               f"\tname='{self.name}',\n" \
               f"\targuments=(\n" \
               f"\t\t{args}\n" \
               f"\t),\n" \
               f"\treturn_type={self.return_type},\n" \
               f"\tdecorators={self.decorators}\n" \
               f")"


__all__ = [
    "get_explicitly_declared_functions",
    "get_mro",
    "FunctionDeclaration"
]
