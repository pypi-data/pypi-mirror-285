import io
import contextlib
from Cython.Build import cythonize
from Cython.Compiler.Errors import CompileError, PyrexError
from setuptools.extension import Extension
from .config import CYTHON_LANGUAGE_LEVEL
import sys
def capture_cython_errors(extension):
    error_output = io.StringIO()
    with contextlib.redirect_stderr(error_output):
        try:
            cythonize([extension], compiler_directives={'language_level': CYTHON_LANGUAGE_LEVEL}, quiet=True)
            return True, None
        except (CompileError, PyrexError) as e:
            return False, error_output.getvalue()

def create_extension(pyx_file, module_name):
    extra_compile_args = [
        '-Wno-unreachable-code',
        '-Wno-unused-function',
        '-Wno-unused-variable'
    ]
    
    if sys.platform == 'darwin':  # macOS
        extra_compile_args.extend([
            '-Wno-unreachable-code-fallthrough',
            '-Wno-unused-private-field'
        ])
    
    return Extension(
        module_name,
        [pyx_file],
        extra_compile_args=extra_compile_args
    )