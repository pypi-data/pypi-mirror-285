# pip install cython
# python compile.py build_ext --inplace

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
ext_modules = [
    Extension("prod",  ["prod.py"]),
    #Extension("file",  ["file.py"]),
    #Extension("filecache",  ["filecache.py"]),
#   ... all your modules that need be compiled ...
]
setup(
    name = 'VFX Pipeline Tools',
    cmdclass = {'build_ext': build_ext},
    ext_modules = ext_modules
)

