
from setuptools import setup, find_packages
import codecs
import os

VERSION = '1.0.8'
DESCRIPTION = 'Chen-Fliess series computation'
LONG_DESCRIPTION = 'A package that allows to simulate the output of a control system by means of the Chen-Fliess series.'

# Setting up
setup(
    name="CFSpy",
    version=VERSION,
    author="Ivan Perez Avellaneda",
    author_email="<iperezave@gmail.com>",
    license="MIT",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['numpy', 'sympy'],
    keywords=['Chen-Fliess series', 'nonlinear system', 'input-output system', 'ODEs', 'control system', 'system theory', 'python'],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
