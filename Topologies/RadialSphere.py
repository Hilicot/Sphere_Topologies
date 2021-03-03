import bmesh
from math import sin, cos, pi
import numpy as np
from funcs.general_functions import *

LABEL = "Radial Sphere"
OPERATOR = "mesh.create_radial_sphere"


# create operator
class MESH_OT_CreateRadialSphere(bpy.types.Operator):
    bl_idname = OPERATOR
    bl_label = LABEL

    def execute(self, context):
        (obj, mesh) = createNewEmptyObject(LABEL)

        # create BMesh
        props = mesh.SphereTopology
        radius = props.sphere_radius = 2
        parallels = props.sphere_resolution = 8
        meridians = props.sphere_resolution2 = 16
        transform = props.sphere_transform = 1
        bm = createRadialSphere(parallels, meridians, radius, transform)
        obj.select_set(True)
        if bm is None:
            self.report({'WARNING'}, "BMesh creation failed")
            return {'CANCELLED'}

        # bake bmesh into mesh
        bm.to_mesh(mesh)
        bm.free()

        # Set remaining settings
        props.sphere_type = LABEL
        setSphereUpdated(props)
        props.sphere_do_update = True

        return {'FINISHED'}


def register():
    bpy.utils.register_class(MESH_OT_CreateRadialSphere)


def unregister():
    bpy.utils.unregister_class(MESH_OT_CreateRadialSphere)


############################################


def createRadialSphere(parallels, meridians, radius, transformRatio) -> bmesh:
    """
    create Radial Sphere that can be unfolded

    :param int parallels:
    :param int meridians:
    :param float radius:
    :param float transformRatio: float between 0 (plane) and 1 (sphere)
    :return bmesh:
    """

    bm = bmesh.new()

    # create vertices
    placeAllVertices(bm, parallels, meridians, radius, transformRatio)

    # create faces
    placeAllFaces(bm, parallels, meridians)

    return bm


def placeAllVertices(bm, parallels, meridians, radius, transformRatio) -> None:
    """
    Place the vertices to form a sphere, a plane, ora something in the middle, depending on <transformRatio>.
    Also, it creates vertices only if missing, else it only moves them in the correct position

    :rtype: None
    :param bmesh bm:
    :param int parallels:
    :param int meridians:
    :param float radius:
    :param float transformRatio:
    """

    parallels = parallels if parallels >= 3 else 3
    meridians = meridians if meridians >= 3 else 3

    smooth_coefficient = getSmoothCoefficient(transformRatio)
    index = 0
    for p in range(parallels):
        plane_z = (1 - (2 * p) / (parallels - 1))
        teta = plane_z * pi / 2
        height = sin(teta)
        for m in range(meridians):
            plane_y = (1 - (2 * m) / (meridians - 1))
            plane_coords = np.array([
                -radius,
                plane_y * radius,
                plane_z * radius
            ])
            phi = m / (meridians - 1) * 2 * pi
            sphere_coords = np.array([
                radius * cos(phi) * cos(teta * smooth_coefficient),
                radius * sin(phi) * cos(teta * smooth_coefficient),
                radius * height
            ])

            # create vert with coords that are the combination of the 2 forms
            defineVertex(bm, index, plane_coords * (1 - transformRatio) + sphere_coords * transformRatio)
            index += 1
    bm.verts.ensure_lookup_table()


def placeAllFaces(bm, parallels, meridians) -> None:
    """
    place all missing faces in the Radial Sphere
    ATTENTION: bm.faces MUST be empty

    :rtype: None
    :param bmesh bm:
    :param int parallels:
    :param int meridians:
    """
    verts = bm.verts
    faces = bm.faces

    for p in range(parallels - 1):
        base_vert = p * meridians
        for m in range(meridians - 1):
            faces.new([
                verts[base_vert + m],
                verts[base_vert + meridians + m],
                verts[base_vert + meridians + m + 1],
                verts[base_vert + m + 1]
            ])
    faces.ensure_lookup_table()


# must keep this prototype
def updateSphereResolution(mesh):
    """
    rebuilds the sphere with new parameters in mesh.SphereTopology. Required if vertex structure changes, else use morphSphere

    :param mesh:
    """
    bm = bmesh.new()
    bm.from_mesh(mesh)

    mytool = mesh.SphereTopology
    radius = mytool.sphere_radius
    transform = mytool.sphere_transform
    parallels = mytool.sphere_resolution
    meridians = mytool.sphere_resolution2
    verts = bm.verts
    faces = bm.faces
    verts.ensure_lookup_table()

    # remove all faces and edges(due to the Radial Sphere topology, faces must be rebuilt entirely when changing resolution)
    removeExcessBMElem(faces, 0)
    removeExcessBMElem(bm.edges, 0)

    # place/update all vertices, then remove the ones in excess, if present
    placeAllVertices(bm, parallels, meridians, radius, transform)
    removeExcessBMElem(verts, getNumberOfVertices(parallels, meridians))

    # place all new faces
    placeAllFaces(bm, parallels, meridians)

    bm.to_mesh(mesh)
    bm.free()
    setSphereUpdated(mytool)


# must keep this prototype
def morphSphere(mesh):
    """
    move pre-existing Radial Sphere's vertices around after a change in the radius or transform, without changing the number of vertices/faces

    :param mesh:
    """
    bm = bmesh.new()
    bm.from_mesh(mesh)

    mytool = mesh.SphereTopology
    parallels = mytool.sphere_resolution
    meridians = mytool.sphere_resolution2
    radius = mytool.sphere_radius
    transform = mytool.sphere_transform
    verts = bm.verts

    # update all vertices
    placeAllVertices(bm, parallels, meridians, radius, transform)
    removeExcessBMElem(verts, getNumberOfVertices(parallels, meridians))

    bm.to_mesh(mesh)
    bm.free()
    setSphereUpdated(mytool)


def getNumberOfFaces(parallels, meridians):
    return (parallels - 1) * meridians


def getNumberOfVertices(parallels, meridians):
    return parallels * (meridians + 1)


def getSmoothCoefficient(transformRatio):
    return transformRatio ** 2
