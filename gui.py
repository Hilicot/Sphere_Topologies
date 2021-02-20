import bpy
import main
from Topologies import RandomSphere, FibonacciSphere, RadialSphere
from funcs import randomColors, VoronoiRegions

from bpy.props import (
    IntProperty,
    FloatProperty,
    PointerProperty,
    EnumProperty,
    BoolProperty
)

'''
            PROPERTIES
'''

enum_items = [("null", " --- ", "not part of the Sphere Topology module")] + [(t[0], t[0], "") for t in
                                                                              main.modules.items()]


class MyProperties(bpy.types.PropertyGroup):
    sphere_type: EnumProperty(
        items=enum_items,
        name="Type",
        default="null"
    )

    sphere_radius: FloatProperty(
        name="Radius",
        default=2,
        update=main.updateTransform
    )

    sphere_resolution: IntProperty(
        name="Resolution",
        description="resolution of the sphere",
        default=3,
        min=1,
        update=main.updateResolution
    )

    sphere_resolution2: IntProperty(
        name="Resolution2",
        description="numbers of parallels of the sphere",
        default=1,
        min=1,
        update=main.updateResolution
    )

    # To ensure correct update triggering, after each update this prop must be equal to resolution*resolution2
    sphere_old_resolution: IntProperty(
        name="Old Resolution",
        description="previous resolution*resolution2 of the sphere",
        default=1,
        min=1
    )

    sphere_transform: FloatProperty(
        name="Transformation",
        description="curvature of the Radial Sphere: = 0 is a plane, 1 is a sphere",
        default=1.0,
        min=0.0,
        max=1.0,
        update=main.updateTransform
    )

    sphere_transform2: FloatProperty(
        name="Transformation2",
        description="Delauney Completion (1 to show all faces, else the lower the number, the fewer faces are computed)",
        default=1.0,
        min=0.0,
        max=1.0,
        update=main.updateResolution
    )

    sphere_old_transradius: FloatProperty(
        name="Old Transradius",
        description="Old transform/radius sum (if different then current product the sphere needs update)",
        default=1.0,
        min=0.0,
    )

    sphere_do_update: BoolProperty(
        name="Update",
        default=False
    )


'''
####################
#           PANELS
####################
'''


class MESH_PT_sphere_topologies(bpy.types.Panel):
    bl_idname = "MESH_PT_sphere_topologies"
    bl_label = "Sphere Topologies"
    bl_space_type = "PROPERTIES"
    bl_region_type = "WINDOW"
    bl_context = "data"

    @classmethod
    def poll(self, context):
        return context.object is not None and context.object.type == 'MESH'

    def draw(self, context):
        layout = self.layout
        mytool = context.object.data.SphereTopology

        layout.prop(mytool, "sphere_radius")
        layout.prop(mytool, "sphere_resolution")
        if mytool.sphere_type == RadialSphere.LABEL:
            layout.prop(mytool, "sphere_resolution2")
        layout.prop(mytool, "sphere_transform")
        if mytool.sphere_type == RandomSphere.LABEL or mytool.sphere_type == FibonacciSphere.LABEL:
            layout.prop(mytool, "sphere_transform2")


'''
####################
#           ADD MENU entry
####################
'''


class MESH_MT_sphere_topology_menu(bpy.types.Menu):
    bl_idname = "MESH_MT_sphere_topology_menu"
    bl_label = "Extended Sphere Topologies"

    def draw(self, context):
        layout = self.layout
        for mod in main.modules.values():
            layout.operator(mod.OPERATOR)

        layout.separator()

        layout.operator("mesh.randomize_colors")
        layout.operator("mesh.transform_to_voronoi")


def menu_func(self, context):
    self.layout.menu("MESH_MT_sphere_topology_menu")


'''
                REGISTER
'''

classes = [
    MESH_MT_sphere_topology_menu,
    MESH_PT_sphere_topologies,
    MyProperties
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    randomColors.register()
    VoronoiRegions.register()
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)
    bpy.types.Mesh.SphereTopology = PointerProperty(type=MyProperties)


def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    randomColors.unregister()
    VoronoiRegions.unregister()
    bpy.types.VIEW3D_MT_add.remove(menu_func)
    del bpy.types.Mesh.SphereTopology
