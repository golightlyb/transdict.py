Transdict (python)
==============

A [dictionary/mapping view](https://docs.python.org/3/library/stdtypes.html#dictionary-view-objects)
that provides a lazy bidirectional transformation between the source and a desired view.

Example
-------

Scenario: imagine you are creating a web application with Python. The HTTP
request headers are given to you in the following format:

```python
example_headers = {
    'HTTP_USER_AGENT':      'Example User Agent',
    'HTTP_FOO_BAR':         'Example value',
    'wsgi.not_important':   'A value you don\'t care about'
}
```


However, you'd prefer they were given to you in the following format instead:

```python
wanted_headers = {
    'user-agent': 'Example User Agent',
    'foo-bar':    'Example Value',
}
```

You could simply make a new dict, but suppose one of these applies:

* the dictionary is potentially large, and you don't want to look at every
key, so you don't want to convert things before you have to

* you want a view, not a seperate copy of the dict, so that updates to
one are reflected in the original

* you don't want to do `valuefunction(example_headers.get(keyfunction(key)))`
all the time


Let's create a new dictionary/mapping type based on Transdict:

```python
import transdict

class Headers(transdict.Transdict):

    def toKey(self, x):
        # how to map a key back to the orignal dict
        # e.g. 'user-agent' => 'HTTP_USER_AGENT'
        return 'HTTP_' + x.upper().replace('-', '_')

    def fromKey(self, x):
        # how the view transforms a key from the original dict
        # e.g. 'HTTP_USER_AGENT' => 'user-agent'

        if not x.startswith('HTTP_'):
            # anything else isn't a valid key in our new view
            # so raise a key error - this will automatically filter out
            # the (key, value) pair when iterating
            raise KeyError(x)

        return x[5:].casefold().replace('_', '-')

    def fromValue(self, x):
        # how the view transforms a value from the original dict
        # - raise ValueError if invalid
        return x
```

All the methods are optional, and default to the identity function, so
we could have ommitted the `fromValue` method.

If you wanted the view to be mutable, e.g. so you could append items in
the desired format and they would be reflected in the original dict,
you would instead subclass from `transdict.MutableTransdict` and also implement
`toValue(self, x)`:


```python
class MutableHeaders(transdict.MutableTransdict):
    def toKey(self, x):
        return 'HTTP_' + x.upper().replace('-', '_')

    def fromKey(self, x):
        if not x.startswith('HTTP_'):
            raise KeyError(x)
        return x[5:].casefold().replace('_', '-')

    # toValue, fromValue are just the identity functions here
    # so we don't need to implement them. If we did, they could raise
    # ValueError exceptions for invalid values.

```


Now you just construct your objects using a normal Python dictionary (or
any other mapping):

```python
headers_view = Headers(example_headers)
mutable_headers_view = MutableHeaders(example_headers)

for i in headers_view.items():
    print("%s: %s" % i)

# prints:
# foo-bar: Example value
# user-agent: Example User Agent

print('user-agent' in headers_view) # => True


mutable_headers_view['referer'] = 'https://example.org/'

for i in example_headers.items():
    print("%s: %s" % i)

# prints:
# HTTP_USER_AGENT: Example User Agent
# HTTP_REFERER: https://example.org/
# HTTP_FOO_BAR: Example value
# wsgi.not_important: A value you don't care about
```

Installation
------------

`sudo pip3 install transdict --upgrade`



COPYING
-------

[GNU All-Permissive License](https://www.gnu.org/licenses/license-list.en.html#GNUAllPermissive)

```
Copyright (C) 2018 Ben Golightly <golightly.ben@googlemail.com>

Copying and distribution of this file, with or without modification,
are permitted in any medium without royalty provided the copyright
notice and this notice are preserved.  This file is offered as-is,
without any warranty.
```

