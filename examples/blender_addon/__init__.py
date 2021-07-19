bl_info = {
    'name': 'Example Addon',
    'author': '3D Ninjas',
    'version': (0, 0, 1),
    'blender': (2, 91, 0),
    'location': '',
    'description': '',
    'warning': '',
    'doc_url': '',
    'category': 'Object',
}

from . import addon


def register():
    addon.register()


def unregister():
    addon.unregister()
