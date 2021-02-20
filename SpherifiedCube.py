import bmesh
import numpy as np
from general_functions import *

LABEL = "Spherified Cube"
OPERATOR = "mesh.create_spherified_cube"

origin = [
    np.array([-1, -1, -1]),
    np.array([1, -1, -1]),
    np.array([1, -1, 1]),
    np.array([-1, -1, 1]),
    np.array([-1, 1, -1]),
    np.array([-1, -1, 1]),
]
right = [
    np.array([1, 0, 0]),
    np.array([0, 0, 1]),
    np.array([-1, 0, 0]),
    np.array([0, 0, -1]),
    np.array([1, 0, 0]),
    np.array([1, 0, 0]),
]
up = [
    np.array([0, 1, 0]),
    np.array([0, 1, 0]),
    np.array([0, 1, 0]),
    np.array([0, 1, 0]),
    np.array([0, 0, 1]),
    np.array([0, 0, -1]),
]


# create operator
class MESH_OT_CreateSpherifiedCube(bpy.types.Operator):
    bl_idname = "mesh.create_spherified_cube"
    bl_label = LABEL

    def execute(self, context):
        (obj, mesh) = createNewEmptyObject(LABEL)

        # create BMesh
        props = mesh.SphereTopology
        radius = props.sphere_radius = 2
        res = props.sphere_old_resolution = props.sphere_resolution = 4
        transform = props.sphere_transform = 1

        bm = bmesh.new()
        placeAllVertices(bm, res, radius, transform)
        obj.select_set(True)

        # bake bmesh into mesh
        bm.to_mesh(mesh)
        bm.free()

        # Set remaining settings
        props.sphere_type = LABEL
        setSphereUpdated(props)
        props.sphere_do_update = True

        return {'FINISHED'}


def register():
    bpy.utils.register_class(MESH_OT_CreateSpherifiedCube)


def unregister():
    bpy.utils.unregister_class(MESH_OT_CreateSpherifiedCube)


############################################


def placeAllVertices(bm, resolution, radius, transformRatio) -> None:
    """
    if given BMesh is not empty, assume it's a correct BMesh and update resolution, else create mesh from scratch
    ATTENTION: no checks are made on correctness of the BMesh

    :rtype: None
    :param bmesh bm:
    :param int resolution:
    :param float radius:
    :param float transformRatio:
    """

    k = resolution + 1
    for face in range(6):
        for j in range(k):
            for i in range(k):
                bm.verts.new(getTransformedCoordinates(face, i, j, resolution, radius, transformRatio))
                bm.verts.ensure_lookup_table()

    for face in range(6):
        for j in range(resolution):
            for i in range(resolution):
                a = (face * k + j) * k + i
                b = (face * k + j) * k + i + 1
                c = (face * k + j + 1) * k + i
                d = (face * k + j + 1) * k + i + 1
                bm.faces.new([bm.verts[a], bm.verts[c], bm.verts[d], bm.verts[b]])
                bm.faces.ensure_lookup_table()


# must keep this prototype
def updateSphereResolution(mesh):
    """
    rebuilds the sphere with new parameters in mesh.SphereTopology. Required if vertex structure changes, else use morphSphere

    :param mesh:
    """
    bm = bmesh.new()

    mytool = mesh.SphereTopology
    radius = mytool.sphere_radius
    transform = mytool.sphere_transform
    res = mytool.sphere_resolution

    placeAllVertices(bm, res, radius, transform)

    bm.to_mesh(mesh)
    bm.free()
    setSphereUpdated(mytool)


# must keep this prototype
def morphSphere(mesh):
    """
    move pre-existing Spherified Cube's vertices around after a change in the radius or transform, without changing the number of vertices/faces

    :param mesh:
    """
    bm = bmesh.new()
    bm.from_mesh(mesh)

    mytool = mesh.SphereTopology
    resolution = mytool.sphere_resolution
    radius = mytool.sphere_radius
    transform = mytool.sphere_transform

    bm.verts.ensure_lookup_table()
    v = 0
    k = resolution + 1
    for face in range(6):
        for j in range(k):
            for i in range(k):
                bm.verts[v].co = getTransformedCoordinates(face, i, j, resolution, radius, transform)
                v += 1

    bm.to_mesh(mesh)
    bm.free()
    setSphereUpdated(mytool)


def getTransformedCoordinates(face, i, j, resolution, radius, transform):
    step = 1 / resolution
    step3 = np.ones(3) * step
    j3 = np.ones(3) * j
    i3 = np.ones(3) * i
    cube_coords = origin[face] * radius + step3 * (i3 * right[face] + j3 * up[face]) * radius * 2
    sphere_coords = normalize(cube_coords, radius)
    return sphere_coords * transform + cube_coords * (1 - transform)
