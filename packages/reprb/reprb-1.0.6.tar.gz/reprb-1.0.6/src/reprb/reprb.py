import io
from _reprb import c_reprb, c_evalb
from collections.abc import Iterable

dumpb = c_reprb
loadb = c_evalb
reprb = c_reprb
evalb = c_evalb


def dump(obj: bytes, file, sep="\n"):

    assert isinstance(obj, (bytes, Iterable))
    assert isinstance(sep, str)
    sep = sep.encode()

    f = None
    should_close = False
    try:
        if isinstance(file, str):
            f = open(file, "wb")
            should_close = True
        elif isinstance(file, (io.TextIOWrapper, io.BufferedWriter)) and all(
            hasattr(file, method) for method in ("write", "close")
        ):
            f = file
        else:
            raise ValueError("file must be a filename or a file object")

        if isinstance(obj, bytes):
            f.write(dumpb(obj))
            f.write(sep)

        elif isinstance(obj, Iterable):
            for o in obj:
                assert isinstance(
                    o, bytes
                ), f"Expect Iterable object, but got {type(o)}"
                f.write(dumpb(o))
                f.write(sep)

    finally:
        if hasattr(f, "close") and should_close:
            f.close()


def load(file, sep="\n"):

    assert isinstance(sep, str)

    f = None
    should_close = False
    objs = list()
    try:
        if isinstance(file, str):
            f = open(file, "rb")
            should_close = True
        elif isinstance(file, (io.TextIOWrapper, io.BufferedReader)) and all(
            hasattr(file, method) for method in ("readline", "close")
        ):
            f = file
        else:
            raise ValueError("file must be a filename or a file object")

        for line in _read_line_iter(f):
            objs.append(loadb(line))
        return objs
    finally:
        if hasattr(f, "close") and should_close:
            f.close()


def load_iter(file, sep="\n"):

    assert isinstance(sep, str)

    f = None
    should_close = False
    try:
        if isinstance(file, str):
            f = open(file, "rb")
            should_close = True
        elif isinstance(file, (io.TextIOWrapper, io.BufferedReader)) and all(
            hasattr(file, method) for method in ("readline", "close")
        ):
            f = file
        else:
            raise ValueError("file must be a filename or a file object")

        for line in _read_line_iter(f):
            yield loadb(line)
    finally:
        if hasattr(f, "close") and should_close:
            f.close()


def _read_line_iter(f, sep: bytes = b"\n", chunk_size=10240):
    reminder = b""
    while True:
        chunk = f.read(chunk_size)
        if len(chunk) == 0:
            if len(reminder) != 0:
                yield reminder
            return
        splits = chunk.split(sep)
        for i in range(len(splits) - 1):
            if len(reminder) != 0:
                yield reminder + splits[i]
                reminder = b""
            else:
                yield splits[i]
        if len(splits[-1]) != 0:
            reminder = splits[-1]
