import bmesh
from funcs.general_functions import *
from Topologies.Icosahedron import getNewBaseIcosahedron

LABEL = "Truncated Icosahedron"
OPERATOR = "mesh.create_truncated_icosahedron"


# create operator
class MESH_OT_CreateTruncatedIcosahedron(bpy.types.Operator):
    bl_idname = OPERATOR
    bl_label = LABEL

    def execute(self, context):
        (obj, mesh) = createNewEmptyObject(LABEL)

        # create Bmesh
        bm = getNewBaseIcosahedron(2)
        truncate(bm)
        bm.to_mesh(mesh)
        obj.select_set(True)

        # set properties
        props = mesh.SphereTopology
        props.sphere_radius = 2
        props.sphere_type = LABEL
        props.sphere_resolution = 1
        setSphereUpdated(props)
        props.sphere_do_update = True

        return {'FINISHED'}


def register():
    bpy.utils.register_class(MESH_OT_CreateTruncatedIcosahedron)


def unregister():
    bpy.utils.unregister_class(MESH_OT_CreateTruncatedIcosahedron)


############################################


# must keep this prototype
def updateSphereResolution(mesh):
    """
    rebuilds the sphere with new parameters in mesh.SphereTopology. Required if vertex structure changes, else use morphSphere

    :param mesh:
    """
    bm = bmesh.new()
    bm.from_mesh(mesh)

    mytool = mesh.SphereTopology
    res = mytool.sphere_resolution
    old_res = mytool.sphere_old_resolution
    radius = mytool.sphere_radius
    verts = bm.verts
    verts.ensure_lookup_table()

    if res < old_res:
        # get bmesh of default IcoSphere
        bm = getNewBaseIcosahedron(radius)
        iterations = res - 1
    elif res > old_res:
        iterations = res - old_res
    else:
        return

    # noinspection PyTypeChecker
    subdivide(bm, iterations, radius)

    bm.to_mesh(mesh)
    bm.free()
    setSphereUpdated(mytool)


# must keep this prototype
def morphSphere(mesh):
    """
    move pre-existing vertices around after a change in the radius, without changing the number of vertices/faces

    :param mesh:
    """
    bm = bmesh.new()
    bm.from_mesh(mesh)

    mytool = mesh.SphereTopology
    radius = mytool.sphere_radius
    verts = bm.verts

    # update all vertices
    for v in verts:
        normalizeVert(v, radius)

    bm.to_mesh(mesh)
    bm.free()
    setSphereUpdated(mytool)

