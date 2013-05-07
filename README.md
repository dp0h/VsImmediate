VsImmediate
===========

Visual Studio's Immediate Window alternative with Python syntax and flexible evaluation. Basically it's just Python Shell (IDLE) which is connected to Visual Studio using Add-in. The project include a Python module and VS Add-in which allow to use Visual Studio Debugger expression evaluation in Python Shell (or in IronPython console embedded in VS), so Python Shell could be used in a similar way as VS's Immediate Window.

### Installation
* Clone this repository
* Compile VSDebugConnector
* Add `.\VsImmediate\VSDebugConnector\bin\` path to Add-in File Path in Visual Studio options 
* Add `.\VsImmediate\vsdbg` path to `PYTHONPATH` in environment variables

### Usage
* Load VSDebugConnector Add-in in Visual Studio
* Start Python Shell or IronPython console and type:
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

```csharp
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
                Phones = new List<Phone> {
                    new Phone {Type = "Mobile", Number = "1234567890"}, 
                    new Phone {Type = "Work", Number = "2345678901"}
                }
            },
        new Person("Jack", "Brown") {
                Phones = new List<Phone> {new Phone {Type = "Home", Number = "3456789012"}}
            }
    };

var tmp = persons.ToArray();
...
```

If we put breakpoint at `var tmp = persons.ToArray();` and start using Python IDLE will have the following output:

* Evaluating `persons`

```
>>> print p("persons") 
Count = 2
	[0x00000000]: {ConsoleApplication2.Person}
	[0x00000001]: {ConsoleApplication2.Person}
	Raw View: 
```

```
>>> print p("persons, raw")
Count = 2
	_items: {ConsoleApplication2.Person[4]}
	_size: 2
	_syncRoot: {object}
	_version: 2
	Capacity: 4
	Count: 2
	System.Collections.Generic.ICollection<T>.IsReadOnly: false
	System.Collections.ICollection.IsSynchronized: false
	System.Collections.ICollection.SyncRoot: {object}
	System.Collections.IList.IsFixedSize: false
	System.Collections.IList.IsReadOnly: false
	Static members: 
```

```
>>> t("persons")
'System.Collections.Generic.List<ConsoleApplication2.Person>'
```

```
>>> v("persons")
'Count = 2'
```

```
>>> m("persons")
['[0x00000000]', '[0x00000001]', 'Raw View']
```

```
>>> m("persons, raw")
['_items', '_size', '_syncRoot', '_version', 'Capacity', 'Count', 'System.Collections.Generic.ICollection<T>.IsReadOnly', 'System.Collections.ICollection.IsSynchronized', 'System.Collections.ICollection.SyncRoot', 'System.Collections.IList.IsFixedSize', 'System.Collections.IList.IsReadOnly', 'Static members']
```

* Evaluating `persons[0]`

```
>>> print p("persons[0]")
{ConsoleApplication2.Person}
	FirstName: "John"
	LastName: "Smith"
	Name: "John Smith"
	Phones: Count = 2
```

```
>>> t("persons[0]")
'ConsoleApplication2.Person'
```

```
>>> v("persons[0]")
'{ConsoleApplication2.Person}'
```

```
>>> m("persons[0]")
['FirstName', 'LastName', 'Name', 'Phones']
```

* Evaluating `persons[0].Name`

```
>>> print p("persons[0].Name")
"John Smith"
```

```
>>> t("persons[0].Name")
'string'
```

```
>>> v("persons[0].Name")
'"John Smith"'
```

```
>>> m("persons[0].Name")
['']
```

* Evaluating `persons[0].Phones[0]`

```
>>> print p("persons[0].Phones[0]")
{ConsoleApplication2.Phone}
	Number: "1234567890"
	Type: "Mobile"
```

```
>>> t("persons[0].Phones[0]")
'ConsoleApplication2.Phone'
```

```
>>> v("persons[0].Phones[0]")
'{ConsoleApplication2.Phone}'
```

```
>>> m("persons[0].Phones[0]")
['Number', 'Type']
```

* Evaluating `persons[0].Phones[0].Number`

```
>>> v("persons[0].Phones[0].Number")
'"1234567890"'
```

