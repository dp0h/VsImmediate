VsImmediatePy
===========

Visual Studio's Immediate Window with Python syntax. Basically this is Python REPL which is connected to Visual Studio using add-in. The project include a Python module and VS add-on which allow to use Visual Studio Debugger expression evaluation in Python REPL (or in IronPython console emdedded in VS), so Python REPL could be used in a similar way as VS's Immediate Window.

### Installation
* Clone this repository
* Compile VSDebugConnector
* Add `.\PyImmediate\VSDebugConnector\bin\` path to Add-in File Path in Visual Studio options 
* Add `.\PyImmediate\vsdbg` path to `PYTHONPATH` in environment variables

### Usage
* Load VSDebugConnector add-in in Visual Studio
* Start Python IDLE or IronPython console and type:
* `from vsdbg import *`
* `detect()`
* Start Debugger in Visual Studio and put breakpoint
* When breakpoint triggered Python console can be used for expression evaluation

### Commands
* `detect()` - auto discover VsImmediatePy's port and host
* `port(port)` - set VsImmediatePy's port number
* `host(host)` - set VsImmediatePy's host name 
* `p(expression)` - print debug information for the expression
* `v(expression)` - return values of the expression
* `t(expression)` - return type of the expression
* `m(expression)` -  return list of members of the expression

### Example

Let's assume we have the following code in C#:

```
class Person {
    public string FirstName { get; internal set; }
    public string LastName { get; internal set; }
    public string Name { get { return FirstName + " " + LastName; } }
    public List<Phone> Phones { get; set; }

    public Person(string firstName, string lastName) {
        FirstName = firstName;
        LastName = lastName;
    }
}

...
var persons = new List<Person> {
        new Person("John", "Smith") {
                Phones = new List<Phone> {new Phone {Type = "Mobile", Number = "1234567890"}, new Phone {Type = "Work", Number = "2345678901"}}
            },
        new Person("Jack", "Brown") {
                Phones = new List<Phone> {new Phone {Type = "Home", Number = "3456789012"}}
            }
    };

var a = persons.ToArray();
...
```

So we can evaluate expression using tool:

TBD - add example with array of clases

### ToDo
* Add few python helper functions for printing some hierarchy valus based on some pattern (something like xpath).
* Add example
