import bpy
import bmesh
import random

'''This function/operator was made to generate a different color for each face based on the already present materials of the currently select model in Blender'''


class MESH_OT_randomizeColors(bpy.types.Operator):
    bl_idname = "mesh.randomize_colors"
    bl_label = "Randomize face materials"
    bl_description = "for each face of the current object, randomly select one material from the available ones in the material panel that has prefix \"RND_\""

    @classmethod
    def poll(self, context):
        return context.object is not None

    # noinspection PyTypeChecker
    def execute(self, context):
        obj = bpy.context.object
        all_materials = []
        for mat in obj.data.materials:
            if mat is not None and mat.name[:4] == "RND_":
                all_materials.append(mat)

        if len(all_materials) == 0:
            self.report({'ERROR'}, "No materials present with prefix \"RND_\"")
            return {'CANCELLED'}

        bpy.ops.object.mode_set(mode='EDIT')

        bm = bmesh.from_edit_mesh(obj.data)

        bm.select_mode = {'FACE'}
        prev_face = None
        for face in bm.faces:
            face.select_set(True)
            if prev_face is not None:
                prev_face.select_set(False)
            face.material_index = random.randint(0, len(all_materials) - 1)
            prev_face = face

        obj.data.update()
        bpy.ops.object.mode_set(mode='OBJECT')

        return {'FINISHED'}


def register():
    bpy.utils.register_class(MESH_OT_randomizeColors)


def unregister():
    bpy.utils.unregister_class(MESH_OT_randomizeColors)
