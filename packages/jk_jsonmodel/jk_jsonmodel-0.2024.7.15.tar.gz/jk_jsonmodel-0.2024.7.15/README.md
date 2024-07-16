jk_jsonmodel
=======

Introduction
------------

This python module provides a special parser for JSON files that produces a data model where each value is associated with the location it originated from in the source file. The purpose of this is to simplify instantiation of objects derived from the original JSON data while providing useful error messages if something is wrong.

Information about this module can be found here:

* [github.org](https://github.com/jkpubsrc/python-module-jk-jsonmodel)
* [pypi.python.org](https://pypi.python.org/pypi/jk_jsonmodel)

The problem
------------------

Sometimes you have a configuration file or you have JSON data returned by a REST API and want to instantiate an object model from this data. However, there might be something wrong with the original JSON data: Some values might be missing or some other value might have the wrong type. This is the case especially if JSON configuration files are modified by hand.

If you're parsing JSON you might run in a situation where there is something wrong with your data. For example you might encounter a numeric value where you would expect a string value - or vice versa. However, if you're using the standard python JSON parser you will be able to inform the user that there *is definitively* such a type mismatch, but you will not be able to inform the user *where exactly* this type mismatch occurs in the original data.

The solution
------------------

This is what `jk_jsonmodel` is about. This module provides a special parser that creates special data objects that still hold the original location of each parsing token internally. Therefore the parser will not produce the standard JSON data model well known in python but substitute objects of similar structure that still maintain the location information.

Having these special JSON based data objects you now can this approach: As your software knows what kind of values to expect you simply query these special objects for values of the desired type. Whenever the data encountered does not meet the expectations you express in your queries the special data objects will automatically raise an exception. This exception will then contain a clear explanation *what* went wrong and *where* the mismatch is located in the original JSON data. By using this approach a user can immediately learn about where exactly he or she needs to correct an input file. This is important information python's classic JSON parser cannot provide.

Limitations
----------------------

A preliminary note. This python module `jk_jsonmodel` is designed to assist in parsing JSON data in a very good way. Howerver, it currently is *not* designed to do this in the most efficient way possible. When writing this module the focus was on convenience of use not on achieving the best JSON parsing performance possible. The latter would be a completely different goal.

Please note that in respect to performance this JSON parser will be more expensive than the python's classic JSON parser. If you require a maximum of performance this python module is definitively not what you want to use. But if you require a maximum of simplicity of your code and a maximum of development speed, this python module might be the module of your choice.

State of development
----------------------

**It is not recommended to use this module in production yet. This module is still under development. The API may still change significantly.**

There are several development goals that are in conflict with each other:

* convenient API
* modular design
* viable performance

Some of the approaches currently taken could still change significantly. This could lead to an equally significant change in the API.
The first stable release is to be expected somewhere in Q2 2023.

Installation
----------------------

This module can be installed via pip:

```bash
$ pip install jk_jsonmodel
```

How to use this module
----------------------

### Select the JSON data you want to load

In this example we assume that the data originates from the following JSON file representing a contact:

```json
{
	"name": "John",
	"surename": "Doe",
	"birthday": {
		"month": 5,
		"day": 23
	},
	"phoneNumbers": {
		"home": "+39 123 45678",
		"office": null,
		"cell": "+39 234 56789"
	}
}
```

### Import

First import this module in all files necessary:

`import jk_jsonmodel`

### Write your data classes

Now let's make use of this module and write a set of data classes that form a hierarchy.

Let's start with `ContactDataRecord`:

```python
class ContactDataRecord(object):

	def __init__(self, jData:jk_jsonmodel.JMDict):
		assert isinstance(jData, jk_jsonmodel.JMDict)

		self.name = jData.getStrE("name")
		self.surename = jData.getStrE("surename")
		self.birthday = BirthdayRecord(jData.getDictE("birthday")) if "birthday" in jData else None
		self.phoneNumbers = {}
		for k, v in jData.getDictE("phoneNumbers").items():
			self.phoneNumbers[k] = PhoneNumberRecord(k, v)
```

As you can see the class will receive a `JMDict` object that represents the root node dictionary/object from the JSON file.
In `__init__` all data is retrieved using specialized methods and data get's converted to instances of `BirthdayRecord` and `PhoneNumberRecord` as needed.

Now for class `BirthdayRecord`:

```python
class BirthdayRecord(object):

	def __init__(self, jData:jk_jsonmodel.JMDict):
		assert isinstance(jData, jk_jsonmodel.JMDict)

		self.month = jData.getIntE("month")
		self.day = jData.getIntE("day")
		self.year = jData.getIntN("year")
```

As you can see this is straight forward. We simply retrieve the values.
Please note that there are convenience methods ending with `E` and `N` such as these:

* `getBoolE(..)`
* `getBoolN(..)`
* `getIntE(..)`
* `getIntN(..)`
* `getStrE(..)`
* `getStrN(..)`
* ...

And so on. These methods differ in a single aspect only:

* Methods ending with `E` will raise an exception if no value has been provided in the JSON
* Methods ending with `N` will tolerate a `null` in JSON

This naming convention allows you to see immediately if a JSON object property is required or if it is optional.

Now for class `PhoneNumberRecord`:

```python
class PhoneNumberRecord(object):

	def __init__(self, key:str, value:jk_jsonmodel.JMValue):
		assert isinstance(key, str)
		assert isinstance(value, jk_jsonmodel.JMValue)

		self.key = key
		self.value = value.vStrN()
```

Same thing here with methods ending with `E` or `N`.
However, this data class will receive an instance of `JMValue` for `value` even if there is a `null` in the JSON file.
In such a situation `JMValue` will contain `null` as data while still maintaining the location information of the token `null`.
But because of this here `value.vStrN()` is used to retrieve the value as a string (if it is not `null`).

### Write the main code to load the data

Now for the main part that loads the data:

```python
jData = jk_jsonmodel.loadDictModelFromFile("somedata.json")
theModel = ContactDataRecord(jData)
```

The first step is to load the JSON into an instance of `JMDict`.
As we know that the JSON file should contain a JSON object we safely can call `loadDictModelFromFile(..)`.

The next step then is to convert the raw data into our data model.
This is done by passing the `JMDict` instance to the constructor method of `ContactDataRecord` as this
constructor method has been designed specifically in the way of processing the raw data.

The result is an initialized `ContactDataRecord` object with nested subobjects of type `PhoneNumerRecord` and `BirthdayRecord`.

### What if something is wrong?

Now let's asume that there is something wrong with the data. We might find a `float` value instead of an `int` here:

```JSON
"birthday": {
	"month": 5.0,
	"day": 23
},
```

In this case the parser will emit the following error message:

> Exception: Expecting value at 'birthday.month' to be an integer (somedata.json:4:3)

TODO: Verify checks. If null raise apropriate exception. If not null raise exception with appropriate location.
TODO: Note all keys not retrieved. Implement two methods:
	* getSuperfluousKeys()
	* errorOnSuperfluousKeys(ignoreKeys:typing.Set[str])

### Pretty print the instantiated data model (using jk_prettyprintobj)

If we would now add some `jk_prettyprintobj` suggar we can visualize the resulting data model quite easily by dumping it to STDOUT. Example:

```
<ContactDataRecord(
        name = 'John'
        surename = 'Doe'
        birthday = <BirthdayRecord(
                month = 5
                day = 23
                year = (null)
        )>
        phoneNumbers = {
                'home' : <PhoneNumberRecord(
                        key = 'home'
                        phoneNumber = '+39 123 45678'
                )>,
                'office' : <PhoneNumberRecord(
                        key = 'office'
                        phoneNumber = (null)
                )>,
                'cell' : <PhoneNumberRecord(
                        key = 'cell'
                        phoneNumber = '+39 234 56789'
                )>,
        }
)>
```

For more details about `jk_prettyprintobj` have a look at the example file(s) and the following URLs:

* [github.org](https://github.com/jkpubsrc/python-module-jk-prettyprintobj)
* [pypi.python.org](https://pypi.python.org/pypi/jk_prettyprintobj)

Author(s)
-------------------

* Jürgen Knauth: pubsrc@binary-overflow.de

License
-------

This software is provided under the following license:

* Apache Software License 2.0



