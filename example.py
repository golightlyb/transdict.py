# Copyright (C) 2018 Ben Golightly <golightly.ben@googlemail.com>

# Copying and distribution of this file, with or without modification,
# are permitted in any medium without royalty provided the copyright
# notice and this notice are preserved.  This file is offered as-is,
# without any warranty.

# (https://www.gnu.org/licenses/license-list.en.html#GNUAllPermissive)




# Main Example
# ============================================================================

# Scenario: imagine you are creating a web application with Python. The HTTP
# request headers are given to you in the following format:

example_headers = {
    'HTTP_USER_AGENT':      'Example User Agent',
    'HTTP_FOO_BAR':         'Example value',
    'wsgi.not_important':   'A value you don\'t care about'
}

# However, you'd prefer they were given to you in the following format instead:

wanted_headers = {
    'user-agent': 'Example User Agent',
    'foo-bar':    'Example Value',
}


# and one of these applies:

# - the dictionary is potentially large, and you don't want to look at every
#   key, so you don't want to convert things before you have to

# - you want a view, not a transformed copy of the dict, so that updates to
#   one are reflected in the original

# - you don't want to do `valuefunction(example_headers.get(keyfunction(key)))`
#   all the time


# You can do this with transdict, which is a view over a dict that transparently
# applies your custom functions in order to create a bidirectional mapping
# between the source dict and the desired view.

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
        # how tge view transforms a value from the original dict
        return x

# All the methods are optional, and default to the identity function.

# If you wanted the view to be mutable, e.g. so you could append items in
# the desired format and they would be reflected in the original dict,
# you would instead subclass from `transdict.MutableTransdict` and also implement
# `toValue(self, x)`

class MutableHeaders(transdict.MutableTransdict):
    def toKey(self, x):
        return 'HTTP_' + x.upper().replace('-', '_')

    def fromKey(self, x):
        if not x.startswith('HTTP_'):
            raise KeyError(x)
        return x[5:].casefold().replace('_', '-')

    # toValue, fromValue are just the identity functions here
    # so we don't need to implement them


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

# (Note: this was a simplified example. In the real world, the WSGI dict also
# has a different encoding!)




# ============================================================================

# Example - case insensitive dict keys

print("")
print("Example - case insensitive dict keys:")
print("==================================================")

class MappingViewWithCaseInsensitiveKeyLookup(transdict.Transdict):
    def toKey(self, x):
        return x.casefold()

    def fromKey(self, x):
        if x == x.casefold(): return x
        raise KeyError(x)

# d, a normal dict
d = {
    'animal':   'cat',
    'colour':   'red',
    'city':     'Swansea',
    'IGNORED':  'Key not casefolded'
}

# f, a view over d
# (https://docs.python.org/3/library/stdtypes.html#dictionary-view-objects)
f = MappingViewWithCaseInsensitiveKeyLookup(d)

print(f.get('Animal'))  # => cat
print(f['Animal'])      # => cat
print('aNiMaL' in f)    # => True
print('ignored' in f)   # => False
print('IGNORED' in f)   # => False

# f is a view over d, so deleting from d means its gone from f too
del d['animal']

print('aNiMaL' in f)    # => False
print(f.get('Animal'))  # => None

for i in f.items():
    print("%s: %s" % i)

# prints:
# city: Swansea
# colour: red


print(list(f.items()))  # => [('city', 'Swansea'), ('colour', 'red')]

