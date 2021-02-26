from math import cos, sin
from random import random
from .funcs.general_functions import *
from .funcs.DelaunayTriangulation import *


def getLabel():
    return "Random Sphere"


def getOperator():
    return "mesh.create_random_sphere"


# create operator
class MESH_OT_CreateRandomSphere(bpy.types.Operator):
    """Create new Sphere using stereographic projection and Delauney triangulation from a randomly generated Sphere"""
    bl_idname = getOperator()
    bl_label = getLabel()

    def execute(self, context):
        (obj, mesh) = createNewEmptyObject(getLabel())
        props = mesh.SphereTopology
        props.sphere_resolution = 500
        props.sphere_transform2 = 1

        bm = bmesh.new()

        # create Fibonacci Sphere
        createRandomSphere(bm, props.sphere_radius, props.sphere_resolution)
        # save original mesh
        mesh["verts"] = [v.co for v in bm.verts]
        delaunayTriangulate(mesh, bm)
        bm.to_mesh(mesh)

        bm.free()

        # Set remaining settings
        props.sphere_type = getLabel()
        setSphereUpdated(props)
        props.sphere_do_update = True

        self.report({'INFO'}, "created " + getLabel())

        return {'FINISHED'}


def register():
    bpy.utils.register_class(MESH_OT_CreateRandomSphere)


def unregister():
    bpy.utils.unregister_class(MESH_OT_CreateRandomSphere)


############################################

def createRandomSphere(bm, radius, res):
    """
    create Random Sphere (vertices only)

    :param bm:
    :param radius:
    :param res:
    """

    for i in range(res):
        # generate random rotation angle and latitude
        phi = random() * 2 * pi
        latitude = radius * (2 * random() - 1)
        dist = (radius ** 2 - latitude ** 2) ** 0.5

        bm.verts.new([
            cos(phi) * dist,
            sin(phi) * dist,
            latitude
        ])
        bm.verts.ensure_lookup_table()


# must keep this prototype
def updateSphereResolution(mesh):
    """
    rebuilds the sphere with new parameters in mesh.SphereTopology. Required if vertex structure changes, else use morphSphere

    :param mesh:
    """
    bm = bmesh.new()

    mytool = mesh.SphereTopology
    radius = mytool.sphere_radius
    res = mytool.sphere_resolution

    createRandomSphere(bm, radius, res)
    mesh["verts"] = [v.co for v in bm.verts]
    delaunayTriangulate(mesh, bm)

    bm.to_mesh(mesh)
    bm.free()
    setSphereUpdated(mytool)


# must keep this prototype
def morphSphere(mesh):
    """
    move pre-existing vertices around after a change in the radius or transform, without changing the number of vertices/faces

    :param mesh:
    """
    bm = bmesh.new()
    bm.from_mesh(mesh)

    mytool = mesh.SphereTopology
    radius = mytool.sphere_radius
    transform = mytool.sphere_transform

    stereographicProjection(bm.verts, mesh["verts"], radius, transform)

    bm.to_mesh(mesh)
    bm.free()
    setSphereUpdated(mytool)
