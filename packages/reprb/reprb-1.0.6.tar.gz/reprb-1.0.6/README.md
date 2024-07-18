## reprb

Represent bytes with printable characters, similar to how python built-in functions repr() and eval() do.

## why

Bytes objects in Python 3 can already be read from and written to files (like load/dump), but you can't easily understand or edit them when you open a binary file directly in a text editor.

`reprb`'s goal is to dump bytes to printable bytes and load them back to the original bytes object quickly (at least faster than the built-in `repr()`), especially when you analysis/dump/load bytes contain both printable and unprintable characters(like http message), `reprb` make it more editable and understandable.

## how
### Install
#### from pip
``` bash
python3 -m pip install reprb
```

#### from source
```bash
git clone git@github.com:Testzero-wz/reprb.git

cd reprb && pip3 install .
```

### Usage

repr bytes object:

```python
>>> from reprb import reprb, evalb
>>> msg = "abc123\x00\x07\x11\x90\xff中文№".encode()
>>> repr_bytes = reprb(msg)
>>> repr_bytes
b'abc123\\0\\a\\x11\\xc2\\x90\\xc3\\xbf\\xe4\\xb8\\xad\\xe6\\x96\\x87\\xe2\\x84\\x96'
>>> eval_bytes = evalb(repr_bytes)
>>> eval_bytes == msg
True
```

dump/load bytes from/to file:

```python
from reprb import dump, load, load_iter

dump_bytes = b"abc123\x00\x07\x84\x96"
dump_file = "dump.txt"

# dump bytes to file, seperate by "\n" default
with open(dump_file, "wb") as f:

    # dump bytes object
    dump(dump_bytes, f)

    # dump all bytes object in list
    dump_bytes_list = [dump_bytes, dump_bytes, dump_bytes]
    dump(dump_bytes_list, f)

# load all bytes from file, seperate by "\n" default
load_bytes_from_path = load(dump_file)

# load all bytes from file handler
with open(dump_file, "rb") as f:
    load_bytes_from_file = load(f)

# load iter
load_bytes_from_iter = list(load_iter(dump_file))

assert (
    [dump_bytes] + dump_bytes_list
    == load_bytes_from_path
    == load_bytes_from_file
    == load_bytes_from_iter
)
```

If you want to store bytes with a more formatable structure like json:
``` python
from reprb import reprb, evalb

# you should decode reprb bytes since json.dump() only accept string object.
# btw, you can decode reprb(msg) bytes safely, because eprb(msg) bytes only contain ascii printable chars
stru = {
    "msg": reprb(http_msg).decode(),
    "extra_info": "whatever",
}

json.dump(stru)
```

## Benchmark

``` bash
$ python3 test.py
Test:
(6/6) Testcases passed. 
dump/load test passed.
Bench:
built-in repr: 1.2180822410s, 183074666.47 bytes/s
built-in eval: 4.8808067660s, 131310258.88 bytes/s
reprb/dumpb: 0.7567997570s, 294661828.23 bytes/s
evalb/loadb: 1.2524397970s, 491999696.49 bytes/s
```
