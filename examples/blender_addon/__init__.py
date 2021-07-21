bl_info = {
    'name': '3DN Python Distribution Tool Example',
    'description': 'Getting started with the Python Distribution Tools',
    'author': '3D Ninjas',
    'version': (1, 0, 0),
    'blender': (2, 80, 0),
    'location': '3D View > Sidebar',
    'category': 'Development',
}

from pathlib import Path

import bpy

from . import ops
from .vars import __VARIANT__
from .vendor.t3dn_bip import previews

# Preview collection created in the register function.
collection = None


class T3DN_PT_pdist_panel(bpy.types.Panel):
    bl_label = '3DN PDIST Getting Started'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = '3D Ninjas'

    def draw(self, context):
        # The layout is part of the panel class.
        layout = self.layout

        # Draw operator for PRO users
        if __VARIANT__ in ['DEV', 'PRO']:
            layout.operator('t3dn.pdist_pro')

        # When drawing a preview, you'll need its icon_id.
        icon_id = collection['image'].icon_id

        # Scale 6.8 comes out at 128x128 pixels if your UI scale is 1.
        layout.template_icon(icon_value=icon_id, scale=6.8)


def register():
    # Register operators
    ops.register()

    # Create a preview collection to load images.
    global collection
    collection = previews.new()

    # Load images
    images = Path(__file__).parent.joinpath('images').resolve()
    if __VARIANT__ in ['DEV', 'PRO']:
        collection.load('image', str(images.joinpath('pro.bip')), 'IMAGE')
    if __VARIANT__ in ['FREE']:
        collection.load('image', str(images.joinpath('free.bip')), 'IMAGE')

    # Register the panel so it shows up in the sidebar.
    bpy.utils.register_class(T3DN_PT_pdist_panel)


def unregister():
    # Unregister the panel to free resources and avoid errors.
    bpy.utils.unregister_class(T3DN_PT_pdist_panel)

    # Discard all loaded previews and remove the collection.
    previews.remove(collection)

    # Unregister operators
    ops.unregister()
