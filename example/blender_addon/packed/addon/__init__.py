
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
