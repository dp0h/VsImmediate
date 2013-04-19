VsImmediatePy
===========

Visual Studio's Immediate Window with Python syntax. Basically this is Python REPL which is connected to Visual Studio using add-in. The project include a Python module and VS add-on which allow to use Visual Studio Debugger expression evaluation in Python REPL (or in IronPython console emdedded in VS), so Python REPL could be used in a similar way as VS's Immediate Window.

### Installation
* Clone this repository
* Compile VSDebugConnector
* Copy files from `.\PyImmediate\VSDebugConnector\bin\` to `%USERPROFILE%\Documents\Visual Studio 2010\Addins\`
* Add `.\PyImmediate\vsdbg` path to `PYTHONPATH` in environment variables

### Usage
* Load VSDebugConnector add-in in Visual Studio.
* Start Python IDLE or IronPython console
* type 

from vsdbg import *

### Commands

TBD

### ToDo
* Add few python helper functions for printing some hierarchy valus based on some pattern (something like xpath).
* Test in on home PC
