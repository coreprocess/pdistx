import bpy
from .vars import __VARIANT__

classes = []

if __VARIANT__ in ['DEV', 'PRO']:

    class T3DN_OT_pdistx_pro(bpy.types.Operator):
        bl_idname = 't3dn.pdistx_pro'
        bl_label = 'Pro Operator'
        bl_description = 'Only for PROs!'
        bl_options = {'REGISTER', 'INTERNAL'}

        def execute(self, context: bpy.types.Context):
            return {'FINISHED'}

    classes.append(T3DN_OT_pdistx_pro)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
