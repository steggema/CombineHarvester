from distutils.core import setup
from Cython.Build import cythonize
import numpy

setup(
    ext_modules=cythonize('lowess.pyx'),
    include_dirs=[numpy.get_include()]
)

import shutil
shutil.move('python/lowess.so', 'lowess.so')
shutil.rmtree('python')
