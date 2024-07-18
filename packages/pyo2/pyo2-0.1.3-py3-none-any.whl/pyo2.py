from ctypes import (
    CDLL,
    POINTER,
    Structure,
    _SimpleCData,
    c_char_p,
    c_double,
    c_int64,
    c_uint8,
    c_uint32,
)
from ctypes import cast as c_cast
from ctypes import create_string_buffer, pointer
from typing import TYPE_CHECKING, Any, cast

if TYPE_CHECKING:
    from ctypes import _CData, _FuncPointer

__all__ = ['RustDLL']

pyvec_cache = {}


def PyVec(typ: type['_CData']) -> type[Structure]:
    if typ in pyvec_cache:
        return pyvec_cache[typ]
    PyVec = type(
        'PyVec_' + typ.__name__,
        (Structure,),
        {
            '_pack_': 8,
            '_fields_': [('ptr', POINTER(typ)), ('len', c_uint32)],
            '__pyvec_ctype__': typ,
        },
    )
    pyvec_cache[typ] = PyVec
    return PyVec


def vec(typ: type['_CData'], ptr, len: int):
    return PyVec(typ)(ptr=c_cast(ptr, POINTER(typ)), len=len)


class RustDLL:
    def __init__(self, name: str):
        """Load a Rust `cdylib`."""
        self.dll = CDLL(name)

    def __getattr__(self, name: str):
        return RustFuncPtr(self.dll.__getattr__(name))


def convert_arg(arg: Any):
    if isinstance(arg, (int, _SimpleCData)):
        return arg
    if isinstance(arg, float):
        return c_double(arg)
    if isinstance(arg, str):
        arg = arg.encode()
    if isinstance(arg, bytes):
        return pointer(vec(c_uint8, ptr=c_char_p(arg), len=len(arg)))
    if isinstance(arg, list):
        if len(arg) == 0:
            return pointer(vec(c_uint8, ptr=create_string_buffer(0), len=0))
        pytype = type(arg[0])
        for x in arg:
            if type(x) is not pytype:
                typ = type(x)
                raise TypeError(
                    'Given list made of multiple types '
                    f'(found {pytype.__name__} and {typ.__name__})'
                )
        ctype = {
            int: c_int64,
            float: c_double,
            bytes: POINTER(PyVec(c_uint8)),
            str: POINTER(PyVec(c_uint8)),
        }.get(pytype)
        if ctype is None:
            raise TypeError(f'Unknown type {pytype.__name__}')
        arr = (ctype * len(arg))()
        for i, v in enumerate(arg):
            arr[i] = convert_arg(v)
        return pointer(vec(ctype, arr, len(arg)))
    raise TypeError(f'Unknown type {type(arg).__name__}')


def unwrap_vec(orig: list, vec):
    if not orig:
        return
    buf = vec.ptr
    typ = type(orig[0])
    if typ not in [int, float]:
        return
    for i, v in zip(range(len(orig)), buf):
        orig[i] = v


class RustFuncPtr:
    def __init__(self, func: '_FuncPointer'):
        self.func = func

    def __call__(self, *args: Any):
        """
        Calls the Rust-defined function.

        The `args` are translated in the following way:
        - `bytes` => `&mut PyStr`
        - `str` => `&PyStr`
        - `list[int]` => `&mut PyVec<i64>`
        - `float` => `f64`
        - `int` => any integer type (i32, u64, etc.)
        """
        real_args = []
        update_vecs = []
        for arg in args:
            converted = convert_arg(arg)
            real_args.append(converted)
            if isinstance(arg, list):
                update_vecs.append((arg, cast(Any, converted).contents))
        res = self.func(*real_args)
        for arg, vec in update_vecs:
            unwrap_vec(arg, vec)
        return res
