#!/usr/bin/env python
#
# GAMS - General Algebraic Modeling System Python API
#
# Copyright (c) 2016-2024 GAMS Software GmbH <support@gams.com>
# Copyright (c) 2016-2024 GAMS Development Corp. <support@gams.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# This file was generated.

from setuptools import Extension, setup, find_packages
import numpy as np
import os
import sys

core_extensions = [
    Extension(
        name=f'gams.core.{api[:3]}._{api}cc',
        sources=[
            os.path.join('src', 'gams', 'core', api[:3], f'{api}cc_wrap.c'),
            os.path.join('src', 'gams', 'core', api[:3], f'{api}cc.c')
        ],
        define_macros=[
            (f'PYPREFIX{api[:3].upper()}', None),
            ('_CRT_SECURE_NO_WARNINGS', None),
            # disable warning about memory leak in swig/Lib/python/pyrun.swg
            # we believe that we cannot do anything about it
            # see also https://github.com/swig/swig/issues/2037
            ('SWIG_PYTHON_SILENT_MEMLEAK', None)
        ],
        include_dirs=[os.path.join('src', 'gams', 'core')]
    ) for api in ['gdx', 'gmd', 'opt', 'idx', 'dctm', 'gmom', 'gevm', 'cfgm']
]

extras = {
    'connect':  ['pandas>=1.5,<2.3', 'pyyaml', 'openpyxl>=3.1.0', 'sqlalchemy', 'cerberus', 'pyodbc', 'psycopg2-binary', 'pymysql', 'pymssql'],
    'control':  ['urllib3'],
    'core':     ['ply', 'numpy'],
    'engine':   ['python_dateutil', 'urllib3'],
    'magic':    ['ipython', 'pandas>=1.5,<2.3'],
    'tools':    ['pandas>=1.5,<2.3'],
    'transfer': ['pandas>=1.5,<2.3', 'scipy']
}
extras['all'] = list(set([x for k,v in extras.items() for x in v]))


classifiers = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Intended Audience :: Science/Research",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3 :: Only",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Topic :: Scientific/Engineering"
]

long_description = """
<div align="center">
  <img src="https://www.gams.com/img/gams_logo.svg"><br>
</div>

-----------------

# gamsapi: powerful Python toolkit to manage GAMS (i.e., sparse) data and control GAMS solves

## What is it?

**gamsapi** is a Python package that includes submodules to control GAMS, manipulate and
transfer data to/from the GAMS modeling system (through GDX files or in-memory objects).
This functionality is available from a variety of different Python interfaces including
standard Python scripts and Jupyter Notebooks. We strive to make it as **simple** as
possible for users to generate, debug, customize, and ultimately use data to solve
optimization problems -- all while maintaining high performance.


## Main Features
Here are just a few of the things that **gamsapi** does well:

  - Seamlessly integrates GAMS data requirements into standard data pipelines (i.e., Pandas, Numpy)
  - Link and harmonize data sets across different symbols
  - Clean/debug data **before** it enters the modeling environment
  - Customize the look and feel of the data (i.e., labeling conventions)
  - Bring data to GAMS from a variety of different starting points
  - Send model output to a variety of different data endpoints (SQL, CSV, Excel, etc.)
  - Automatic data reshaping and standardization -- will work to translate your data formats into the Pandas DataFrame standard
  - Control GAMS model solves and model specification

## Where to get it
The source code is currently available with any typical [GAMS system](https://www.gams.com/download/).
No license is needed in order to use **gamsapi**.  A license is necessary in order to solve GAMS models.

A free [demo license](https://www.gams.com/try_gams/) is available!

## Dependencies
Installing **gamsapi** will not install any third-party dependencies, as such, it only contains basic functionality.
Users should modify this base installation by choosing **extras** to install -- extras are described in the [documentation](https://www.gams.com/latest/docs/API_PY_GETTING_STARTED.html#PY_PIP_INSTALL_BDIST).

```sh
# from PyPI (with extra "transfer")
pip install gamsapi[transfer]
```

```sh
# from PyPI (with extras "transfer" and "magic")
pip install gamsapi[transfer,magic]
```

```sh
# from PyPI (include all dependencies)
pip install gamsapi[all]
```

## Documentation
The official documentation is hosted on [gams.com](https://www.gams.com/latest/docs/API_PY_GETTING_STARTED.html).

## Getting Help

For usage questions, the best place to go to is [GAMS](https://www.gams.com/latest/docs/API_PY_GETTING_STARTED.html).
General questions and discussions can also take place on the [GAMS World Forum](https://forum.gamsworld.org).

## Discussion and Development
If you have a design request or concern, please write to support@gams.com.
"""


setup(
    name="gamsapi",
    version="47.3.0",
    description="GAMS Python API",
    url="http://www.gams.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="GAMS Development Corporation",
    author_email="support@gams.com",
    project_urls={"Documentation":"https://www.gams.com/latest/docs/API_PY_OVERVIEW.html"},
    packages=find_packages(where="src") + ["gams.connect.agents.schema"],
    package_dir={"": "src"},
    license="MIT",
    python_requires=">=3.8",
    extras_require=extras,
    classifiers=classifiers,
    include_package_data=True,
    exclude_package_data={'':['*.h', '*.c']},
    ext_modules=[
        Extension(
            name="gams.core.numpy._gams2numpy",
            sources=[
                os.path.join('src', 'gams', 'core', 'numpy', '_gams2numpy.c'),
                os.path.join('src', 'gams', 'core', 'gdx', 'gdxcc.c'),
                os.path.join('src', 'gams', 'core', 'gmd', 'gmdcc.c')
            ],
            include_dirs=[
                np.get_include(),
                os.path.join('src', 'gams', 'core', 'gdx'),
                os.path.join('src', 'gams', 'core', 'gmd'),
                os.path.join('src', 'gams', 'core')
            ]
        ),
    ] + core_extensions,
)
