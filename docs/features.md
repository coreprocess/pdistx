**Pyscriptpacker** provide the following:

## Single file distribution

Pyscriptpacker will go through all the source files within the requested module and pack them into a single file. The user can place the file anywhere, under any module and the result file still work pretty well thanks to **our custom loader code**.

You can take a look at some examples in [here](/example).

## Extending the libraries

You can also pack external Python modules to your packed file as well by installing it in your Python environment and then provide the **site-packages** path to the Pyscriptpacker.

For example:

``` console
$ pip install pyscriptpacker, toposort
$ pyscriptpacker toposort <path_to_site-packages> output.py
```

The `output.py` will contain a virtual_module similar to this one.

``` python
_virtual_modules = {
    "toposort": {
        "is_package": False,
        "code": '#######################################################################\n# Implements a topological sort algorithm.\n#\n# Copyright 2014 True Blade Systems, Inc.\n#\n# Licensed under the Apache License, Version 2.0 (the "License");\n# you may not use this file except in compliance with the License.\n# You may obtain a copy of the License at\n#\n# http://www.apache.org/licenses/LICENSE-2.0\n#\n# Unless required by applicable law or agreed to in writing, software\n# distributed under the License is distributed on an "AS IS" BASIS,\n# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n# See the License for the specific language governing permissions and\n# limitations under the License.\n#\n# Notes:\n#  Based on http://code.activestate.com/recipes/578272-topological-sort\n#   with these major changes:\n#    Added unittests.\n#    Deleted doctests (maybe not the best idea in the world, but it cleans\n#     up the docstring).\n#    Moved functools import to the top of the file.\n#    Changed assert to a ValueError.\n#    Changed iter[items|keys] to [items|keys], for python 3\n#     compatibility. I don\'t think it matters for python 2 these are\n#     now lists instead of iterables.\n#    Copy the input so as to leave it unmodified.\n#    Renamed function from toposort2 to toposort.\n#    Handle empty input.\n#    Switch tests to use set literals.\n#\n########################################################################\n\nfrom functools import reduce as _reduce\n\n__all__ = [\'toposort\', \'toposort_flatten\', \'CircularDependencyError\']\n\n\nclass CircularDependencyError(ValueError):\n    def __init__(self, data):\n        # Sort the data just to make the output consistent, for use in\n        #  error messages.  That\'s convenient for doctests.\n        s = \'Circular dependencies exist among these items: {{{}}}\'.format(\', \'.join(\'{!r}:{!r}\'.format(key, value) for key, value in sorted(data.items())))\n        super(CircularDependencyError, self).__init__(s)\n        self.data = data\n\n\ndef toposort(data):\n    """Dependencies are expressed as a dictionary whose keys are items\nand whose values are a set of dependent items. Output is a list of\nsets in topological order. The first set consists of items with no\ndependences, each subsequent set consists of items that depend upon\nitems in the preceeding sets.\n"""\n\n    # Special case empty input.\n    if len(data) == 0:\n        return\n\n    # Copy the input so as to leave it unmodified.\n    data = data.copy()\n\n    # Ignore self dependencies.\n    for k, v in data.items():\n        v.discard(k)\n    # Find all items that don\'t depend on anything.\n    extra_items_in_deps = _reduce(set.union, data.values()) - set(data.keys())\n    # Add empty dependences where needed.\n    data.update({item:set() for item in extra_items_in_deps})\n    while True:\n        ordered = set(item for item, dep in data.items() if len(dep) == 0)\n        if not ordered:\n            break\n        yield ordered\n        data = {item: (dep - ordered)\n                for item, dep in data.items()\n                    if item not in ordered}\n    if len(data) != 0:\n        raise CircularDependencyError(data)\n\n\ndef toposort_flatten(data, sort=True):\n    """Returns a single list of dependencies. For any set returned by\ntoposort(), those items are sorted and appended to the result (just to\nmake the results deterministic)."""\n\n    result = []\n    for d in toposort(data):\n        result.extend((sorted if sort else list)(d))\n    return result\n',
    },
}
```

## Compressing

Pyscriptpacker does have an option to compress the source code using the [bz2](https://docs.python.org/3/library/bz2.html) method, so it will add a security layer to your source file and still can be imported as module and working correctly.

Take the above **toposort** module source code as an example, here is the packing result from Pyscriptpacker with and without the compression option.

`-c, --compress`

=== "With"

    ``` python
    _virtual_modules = {
        "toposort": {
            "is_package": False,
            "code": 'import bz2, base64\nexec(bz2.decompress(base64.b64decode("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")))\n',
        },
    }
    ```

=== "Without"

    ``` python
    _virtual_modules = {
        "toposort": {
            "is_package": False,
            "code": '#######################################################################\n# Implements a topological sort algorithm.\n#\n# Copyright 2014 True Blade Systems, Inc.\n#\n# Licensed under the Apache License, Version 2.0 (the "License");\n# you may not use this file except in compliance with the License.\n# You may obtain a copy of the License at\n#\n# http://www.apache.org/licenses/LICENSE-2.0\n#\n# Unless required by applicable law or agreed to in writing, software\n# distributed under the License is distributed on an "AS IS" BASIS,\n# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.\n# See the License for the specific language governing permissions and\n# limitations under the License.\n#\n# Notes:\n#  Based on http://code.activestate.com/recipes/578272-topological-sort\n#   with these major changes:\n#    Added unittests.\n#    Deleted doctests (maybe not the best idea in the world, but it cleans\n#     up the docstring).\n#    Moved functools import to the top of the file.\n#    Changed assert to a ValueError.\n#    Changed iter[items|keys] to [items|keys], for python 3\n#     compatibility. I don\'t think it matters for python 2 these are\n#     now lists instead of iterables.\n#    Copy the input so as to leave it unmodified.\n#    Renamed function from toposort2 to toposort.\n#    Handle empty input.\n#    Switch tests to use set literals.\n#\n########################################################################\n\nfrom functools import reduce as _reduce\n\n__all__ = [\'toposort\', \'toposort_flatten\', \'CircularDependencyError\']\n\n\nclass CircularDependencyError(ValueError):\n    def __init__(self, data):\n        # Sort the data just to make the output consistent, for use in\n        #  error messages.  That\'s convenient for doctests.\n        s = \'Circular dependencies exist among these items: {{{}}}\'.format(\', \'.join(\'{!r}:{!r}\'.format(key, value) for key, value in sorted(data.items())))\n        super(CircularDependencyError, self).__init__(s)\n        self.data = data\n\n\ndef toposort(data):\n    """Dependencies are expressed as a dictionary whose keys are items\nand whose values are a set of dependent items. Output is a list of\nsets in topological order. The first set consists of items with no\ndependences, each subsequent set consists of items that depend upon\nitems in the preceeding sets.\n"""\n\n    # Special case empty input.\n    if len(data) == 0:\n        return\n\n    # Copy the input so as to leave it unmodified.\n    data = data.copy()\n\n    # Ignore self dependencies.\n    for k, v in data.items():\n        v.discard(k)\n    # Find all items that don\'t depend on anything.\n    extra_items_in_deps = _reduce(set.union, data.values()) - set(data.keys())\n    # Add empty dependences where needed.\n    data.update({item:set() for item in extra_items_in_deps})\n    while True:\n        ordered = set(item for item, dep in data.items() if len(dep) == 0)\n        if not ordered:\n            break\n        yield ordered\n        data = {item: (dep - ordered)\n                for item, dep in data.items()\n                    if item not in ordered}\n    if len(data) != 0:\n        raise CircularDependencyError(data)\n\n\ndef toposort_flatten(data, sort=True):\n    """Returns a single list of dependencies. For any set returned by\ntoposort(), those items are sorted and appended to the result (just to\nmake the results deterministic)."""\n\n    result = []\n    for d in toposort(data):\n        result.extend((sorted if sort else list)(d))\n    return result\n',
        },
    }
    ```

## Zipping output

`-z zip_file, --zip=zip_file`  and `-r path, --resources=path,...`

These two options allow Pyscriptpacker instead of just output into a single file, it will add the result file into the desired zip file and also includes all the resource files/folders (if any).

Moreover, the resource flag does have a support for custom path, where PyscriptPacker will structure the resource file as you wish by using color `:` as an annotation and then define your custom path.

For example:

=== "-r README.md:Folder/README.md"
    ```
    zip_file.zip
    ├─ Folder/
    │  └─ README.md
    └─ other_file.py
    ```
=== "-r README.md"
    ```
    zip_file.zip
    ├─ README.md
    └─ other_file.py
    ```
