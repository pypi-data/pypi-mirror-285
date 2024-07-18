from setuptools import Extension, setup
import platform


def get_extra_compile_args():
    compiler = platform.python_compiler()
    if "MSC" in compiler:
        return ["/W3"]
    elif "GCC" in compiler:
        return ["-Wno-unused-const-variable"]
    elif "Clang" in compiler:
        return ["-Wno-unused-const-variable"]
    else:
        print("Unknown compiler, install GCC/Clang/MSVC first!")
        exit(-1)


ext_modules = Extension(
    "_reprb",
    sources=["src/reprb/c_extension/_reprb.c"],
    extra_compile_args=get_extra_compile_args(),
)

setup(
    ext_modules=[ext_modules],
)
