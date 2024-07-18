#!/usr/bin/env python
# coding:utf-8
import os
import sys
import ctypes
import tempfile
from setuptools import find_packages, setup
from setuptools.command.install import install

long_description = """
STCube Command Executor v0.0.1
------------------------------------------------------------
>>> help
    -q|quit: 
        Quit the STCube command executor.
        
    -h|help: 
        Show the help information.
        .x: Show the help information of x.
        
    -s|set|setting: 
        Setting the STCube command executor.
        .en: Set the language to English.
        .zh: Set the language to Chinese.
        
    -l|lib: 
        Library management.
            - Library is made from stm32cube project directory.
            - Need gen codes first in cubemx
        .new: Create a new library from the stm32cube project directory.
        .exp: Open the library directory in the explorer.
        
    -m|mod: 
        Modules management.
            - Module is made from some .c/cpp .h/hpp files.
            - Import module will copy file and write the main.h
        .new: Create a new module from current project directory.
        .exp: Open the module directory in the explorer.
        
    -n|new: 
        Create a new Project from Library.
        
    -o|cd|open: 
        Change the current project directory.
            * will close the current project if has.
        
    -u|up|update: 
        Update the current project to create cpp Entrence.
            * won't action if the main.cpp already exists.
"""

setup(
    name='stcube',
    version='0.1.1.1',
    description='used to manage stm32cubemx template project and some user source file.',
    long_description=long_description,
    long_description_content_type="text/plain",
    author_email='2229066748@qq.com',
    maintainer="Eagle'sBaby",
    maintainer_email='2229066748@qq.com',
    packages=find_packages(),
    license='Apache Licence 2.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: Microsoft :: Windows',
    ],
    keywords=['management', "stm32cubemx"],
    python_requires='>=3.10',
    install_requires=[

    ],
    entry_points={
        'console_scripts': [
            'stcube = stcube:cmd_entry',
        ],
    },
    # cmdclass={
    #     'install': PostInstallCommand,
    # },
)
