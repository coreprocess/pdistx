**Pyscriptpacker** provide the following:

## Single file distribution

Pyscriptpacker will go through all the source files within the requested module and pack them into a single file. The user can place the file anywhere, under any module and the result file still work pretty well thanks to **our custom loader code**.

Here is a simple example of a result file using Pyscriptpacker to pack this blender [:octicons-file-code-24: example addon](https://github.com/3dninjas/pyscriptpacker). 

??? example "Example result"
    ``` python hl_lines="251-272"
    _virtual_modules = {
        "addon.ui": {
            "is_package": False,
            "code": 'import bpy\n\n\nclass Panel(bpy.types.Panel):\n    bl_idname = \'T3DN_ExamplePanel\'\n    bl_label = \'3D Ninja Example\'\n    bl_category = \'3D Ninjas\'\n    bl_space_type = \'VIEW_3D\'\n    bl_region_type = \'UI\'\n\n    def draw(self, context):\n        layout = self.layout\n\n        scene = context.scene\n\n        # Create a simple row.\n        layout.label(text=" Simple Row:")\n\n        row = layout.row()\n        row.prop(scene, "frame_start")\n        row.prop(scene, "frame_end")\n\n        # Create an row where the buttons are aligned to each other.\n        layout.label(text=" Aligned Row:")\n\n        row = layout.row(align=True)\n        row.prop(scene, "frame_start")\n        row.prop(scene, "frame_end")\n\n        # Create two columns, by using a split layout.\n        split = layout.split()\n\n        # First column\n        col = split.column()\n        col.label(text="Column One:")\n        col.prop(scene, "frame_end")\n        col.prop(scene, "frame_start")\n\n        # Second column, aligned\n        col = split.column(align=True)\n        col.label(text="Column Two:")\n        col.prop(scene, "frame_start")\n        col.prop(scene, "frame_end")\n\n        # Big render button\n        layout.label(text="Big Button:")\n        row = layout.row()\n        row.scale_y = 3.0\n        row.operator("render.render")\n\n        # Different sizes in a row\n        layout.label(text="Different button sizes:")\n        row = layout.row(align=True)\n        row.operator("render.render")\n\n        sub = row.row()\n        sub.scale_x = 2.0\n        sub.operator("render.render")\n\n        row.operator("render.render")\n\n\nclasses = (Panel,)\n\n\ndef register():\n    for cls in classes:\n        bpy.utils.register_class(cls)\n\n\ndef unregister():\n    for cls in reversed(classes):\n        bpy.utils.unregister_class(cls)\n',
        },
        "addon": {
            "is_package": True,
            "code": 'from . import ui\n\nmodules = (ui,)\n\n\ndef register():\n    for module in modules:\n        module.register()\n\n\ndef unregister():\n    for module in reversed(modules):\n        module.unregister()\n',
        },
    }


    import json
    import hashlib
    import sys
    import imp
    import os
    import binascii
    try:
        import __builtin__ as builtins
    except ImportError:
        import builtins

    __packer_bundle_hash__ = hashlib.sha256(
        json.dumps(_virtual_modules, sort_keys=True).encode('utf-8')).hexdigest()
    __packer_bundle_token__ = binascii.hexlify(os.urandom(8))

    if os.getenv('PYSCRIPTPACKER_DEBUG') == 'true':
        print('Packer: init bundle_hash={} bundle_token={}'.format(
            __packer_bundle_hash__, __packer_bundle_token__))


    def _try_load_module(name, local_name, parent_name, override):

        # qualified names
        qf_name = '{}.{}'.format(__name__, name)
        qf_parent_name = '{}.{}'.format(
            __name__, parent_name) if parent_name else __name__

        # check if module is not loaded already and available
        virtual_module = _virtual_modules.get(name, None)
        if not virtual_module or qf_name in sys.modules:
            return
        if not override:
            if hasattr(sys.modules[qf_parent_name], local_name):
                return

        # debug
        if os.getenv('PYSCRIPTPACKER_DEBUG') == 'true':
            print(
                'Packer: loading name={}, qf_name={}, local_name={}, parent_name={}, qf_parent_name={}, override={}'
                .format(
                    name,
                    qf_name,
                    local_name,
                    parent_name,
                    qf_parent_name,
                    override,
                ))

        # create module object
        module = sys.modules[qf_name] = imp.new_module(qf_name)
        setattr(module, '__packer_bundle_hash__', __packer_bundle_hash__)
        setattr(module, '__packer_bundle_token__', __packer_bundle_token__)
        module.__name__ = qf_name
        if virtual_module['is_package']:
            module.__package__ = qf_name
            module.__path__ = [
                '{}/{}/{}'.format(__packer_bundle_hash__,
                                        __packer_bundle_token__, name)
            ]
        else:
            module.__package__ = sys.modules[qf_parent_name].__package__

        # import hook for modules using __import__ the wrong way
        def _packer_import_hook(name,
                                globals=None,
                                locals=None,
                                fromlist=(),
                                level=0):
            return _packer_import(
                name,
                globals if globals is not None else module.__dict__,
                locals if locals is not None else module.__dict__,
                fromlist,
                level,
            )

        setattr(module, '__import__', _packer_import_hook)

        # inject code
        code = compile(
            virtual_module['code'],
            __file__ + '/' + name.replace('.', '/') +
            ('/__init__' if virtual_module['is_package'] else '') + '.py',
            'exec',
        )
        exec(code, module.__dict__)

        # link to parent
        setattr(sys.modules[qf_parent_name], local_name, module)


    def _try_get_module_all_list(name):
        qf_name = '{}.{}'.format(__name__, name) if name else __name__
        module = sys.modules.get(qf_name, None)
        if module:
            all_list = getattr(module, '__all__', None)
            if all_list:
                return all_list
        return []


    _orig_import = builtins.__import__


    def _packer_import(name, globals=None, locals=None, fromlist=(), level=0):

        globals_or_empty = globals if globals else {}

        # determine load path
        if level > 0:
            load_path = globals_or_empty.get(
                '__package__',
                globals_or_empty['__name__'],
            ).split('.')
            if level > 1:
                load_path = load_path[:-(level - 1)]
        else:
            load_path = []
        load_path += name.split('.') if name else []

        # handle hoisted requests with rebased path
        if '.'.join(load_path) == __name__ or '.'.join(load_path).startswith(
                __name__ + '.'):
            load_path = load_path[len(__name__.split('.')):]

        # skip load requests not originating from the bundle
        elif (globals_or_empty.get('__packer_bundle_hash__', None) !=
            __packer_bundle_hash__) or (globals_or_empty.get(
                '__packer_bundle_token__', None) != __packer_bundle_token__):
            load_path = None

        # try to load and return module if load path is given
        if load_path is not None:

            # load modules along the path
            for depth in range(len(load_path)):
                _try_load_module(
                    '.'.join(load_path[0:depth + 1]),
                    load_path[depth],
                    '.'.join(load_path[0:depth]) if depth > 0 else None,
                    True,
                )

            # load modules referenced by the from list
            if fromlist:
                for from_item in fromlist:
                    if from_item == '*':
                        all_list = _try_get_module_all_list(
                            '.'.join(load_path) if load_path else None,)
                        for all_item in all_list:
                            _try_load_module(
                                '.'.join(load_path + [all_item]),
                                all_item,
                                '.'.join(load_path) if load_path else None,
                                False,
                            )
                    _try_load_module(
                        '.'.join(load_path + [from_item]),
                        from_item,
                        '.'.join(load_path) if load_path else None,
                        False,
                    )

            # try to return the requested module
            if load_path:
                if not fromlist:
                    return_name = '{}.{}'.format(__name__, load_path[0])
                else:
                    return_name = '{}.{}'.format(__name__, '.'.join(load_path))

                if return_name in sys.modules:
                    return sys.modules[return_name]

        # delegate import to original routine
        return _orig_import(name, globals, locals, fromlist, level)


    builtins.__import__ = _packer_import

    if sys.version_info >= (3, 0):

        # If we import this library in Python 2.x, the library can no longer be
        # imported by other modules. Weird behaviour, we would like to avoid.
        # So keep this import here!
        import importlib

        class _PackerLoader(importlib.abc.Loader):

            def __init__(self, code, is_package, name):
                self._code = code
                self._is_package = is_package
                self._name = name

            def create_module(self, spec):
                return None

            def exec_module(self, module):
                code = compile(
                    self._code,
                    __file__ + '/' + self._name.replace('.', '/') +
                    ('/__init__' if self._is_package else '') + '.py',
                    'exec',
                )
                exec(code, module.__dict__)

        class _PackerMetaFinder(importlib.abc.MetaPathFinder):

            def find_spec(self, fullname, path, target=None):

                # construct load path
                load_path = fullname.split('.')

                # handle hoisted requests with rebased path
                if '.'.join(load_path).startswith(__name__ + '.'):
                    load_path = load_path[len(__name__.split('.')):]

                # skip load requests not originating from the bundle
                elif not path or not path[0].startswith('{}/{}/'.format(
                        __packer_bundle_hash__, __packer_bundle_token__)):
                    return None

                # load module
                virtual_name = '.'.join(load_path)
                virtual_module = _virtual_modules.get(virtual_name, None)
                if not virtual_module:
                    return None

                # create spec
                return importlib.util.spec_from_loader(
                    virtual_name,
                    loader=_PackerLoader(virtual_module['code'],
                                        virtual_module['is_package'],
                                        virtual_name),
                    is_package=True if virtual_module['is_package'] else None,
                )

        sys.meta_path.insert(0, _PackerMetaFinder())
    
    bl_info = {
        "name": "Pyscriptpacker Example Addon",
        "author": "3D Ninjas",
        "version": (0, 0, 1),
        "blender": (2, 91, 0),
        "location": "",
        "description": "",
        "warning": "",
        "doc_url": "",
        "category": "Object"
    }


    from . import addon


    def register():
        addon.register()


    def unregister():
        addon.unregister()
    ```

You can read more about the example in [here](/example)

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
