import bpy

from . import funcs
from .Topologies import *
from bpy.props import (
    IntProperty,
    FloatProperty,
    PointerProperty,
    EnumProperty,
    BoolProperty
)


def getModules():
    return {
        RadialSphere.getLabel(): RadialSphere,
        SpherifiedCube.getLabel(): SpherifiedCube,
        Icosahedron.getLabel(): Icosahedron,
        TruncatedIcosahedron.getLabel(): TruncatedIcosahedron,
        RandomSphere.getLabel(): RandomSphere,
        FibonacciSphere.getLabel(): FibonacciSphere
    }


def testAndSetPreviousFrame(previous_frame):
    # return true if current frame is equal to the previous
    sc = bpy.context.scene
    if "previous_frame" in sc.keys():
        val = sc["previous_frame"]
    else:
        val = -1
    sc["previous_frame"] = previous_frame
    return previous_frame == val


def trigger_update_on_frame_change(scene):
    if not testAndSetPreviousFrame(scene.frame_current):
        for obj in scene.objects:
            if obj.type == 'MESH' and obj.data.SphereTopology.sphere_type != "null":
                funcs.general_functions.sphereUpdateIfNeeded(obj.data)


# function triggered by manual update of Resolution properties
def updateResolution(self=None, context=bpy.context):
    """
    Called when Resolution property changes.
    Calls the updateSphereResolution function of the appropriate module

    :param self:
    :param context:
    :return None:
    """
    mesh = funcs.general_functions.getCurrentBMesh()

    if mesh is None or not mesh.SphereTopology.sphere_do_update:
        return

    _type = mesh.SphereTopology.sphere_type
    if _type == "null":
        print("Mesh was not created by the Sphere Topology module")
    else:
        mod = getModules()[_type]
        mod.updateSphereResolution(mesh)


# function triggered by manual update of transform/radius properties
def updateTransform(self=None, context=bpy.context):
    """
    Called when Radius/Transform properties change.
    Calls the morphSphere function of the appropriate module

    :param self:
    :param context:
    :return None:
    """
    mesh = funcs.general_functions.getCurrentBMesh()
    if mesh is None or not mesh.SphereTopology.sphere_do_update:
        return

    _type = mesh.SphereTopology.sphere_type
    if _type == "null":
        print("Mesh was not created by the Sphere Topology module")
    else:
        mod = getModules()[_type]
        mod.morphSphere(mesh)


"""
################################################
## GUI
###############################################
"""

enum_items = [("null", " --- ", "not part of the Sphere Topology module")] + [(t[0], t[0], "") for t in
                                                                              getModules().items()]


class MyProperties(bpy.types.PropertyGroup):
    # noinspection PyTypeChecker
    sphere_type: EnumProperty(
        items=enum_items,
        name="Type",
        default="null"
    )

    sphere_radius: FloatProperty(
        name="Radius",
        default=2,
        update=updateTransform()
    )

    sphere_resolution: IntProperty(
        name="Resolution",
        description="resolution of the sphere",
        default=3,
        min=1,
        update=updateResolution()
    )

    sphere_resolution2: IntProperty(
        name="Resolution2",
        description="numbers of parallels of the sphere",
        default=1,
        min=1,
        update=updateResolution()
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
        update=updateTransform()
    )

    sphere_transform2: FloatProperty(
        name="Transformation2",
        description="Delauney Completion (1 to show all faces, else the lower the number, the fewer faces are computed)",
        default=0.0,
        min=0.0,
        max=1.0,
        update=updateResolution()
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
        if mytool.sphere_type == Topologies.RadialSphere.getLabel():
            layout.prop(mytool, "sphere_resolution2")
        layout.prop(mytool, "sphere_transform")
        if mytool.sphere_type == Topologies.RandomSphere.getLabel() or mytool.sphere_type == Topologies.FibonacciSphere.getLabel():
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
        for mod in getModules().values():
            layout.operator(mod.OPERATOR)

        layout.separator()

        layout.operator("mesh.randomize_colors")
        layout.operator("mesh.transform_to_voronoi")


def menu_func(self, context):
    self.layout.menu("MESH_MT_sphere_topology_menu")


'''
####################
#           REGISTER
####################
'''

classes = [
    MESH_MT_sphere_topology_menu,
    MESH_PT_sphere_topologies,
    MyProperties
]


def register():
    for mod in getModules().values():
        mod.register()

    for cls in classes:
        bpy.utils.register_class(cls)

    funcs.randomColors.register()
    funcs.VoronoiRegions.register()
    bpy.types.VIEW3D_MT_mesh_add.append(menu_func)
    bpy.types.Mesh.SphereTopology = PointerProperty(type=MyProperties)

    bpy.app.handlers.frame_change_post.append(trigger_update_on_frame_change)


def unregister():
    for mod in getModules().values():
        mod.unregister()
    for cls in classes:
        bpy.utils.unregister_class(cls)

    funcs.randomColors.unregister()
    funcs.VoronoiRegions.unregister()
    bpy.types.VIEW3D_MT_add.remove(menu_func)
    del bpy.types.Mesh.SphereTopology

    bpy.app.handlers.frame_change_pre.remove(trigger_update_on_frame_change)


if __name__ == "main":
    register()
