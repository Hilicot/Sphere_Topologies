import math
from .funcs.general_functions import *
from .funcs.DelaunayTriangulation import *


def getLabel():
    return "Fibonacci Sphere"


def getOperator():
    return "mesh.create_fibonacci_sphere"


# create operator
class MESH_OT_CreateFibonacciSphere(bpy.types.Operator):
    """Create new Fibonacci Sphere using stereographic projection and Delauney triangulation"""
    bl_idname = getOperator()
    bl_label = getLabel()

    def execute(self, context):
        (obj, mesh) = createNewEmptyObject(getLabel())
        props = mesh.SphereTopology
        props.sphere_resolution = 500
        props.sphere_transform2 = 1

        bm = bmesh.new()

        # create Fibonacci Sphere
        createFibonacciSphere(bm, props.sphere_radius, props.sphere_resolution)
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
    bpy.utils.register_class(MESH_OT_CreateFibonacciSphere)


def unregister():
    bpy.utils.unregister_class(MESH_OT_CreateFibonacciSphere)


############################################

def createFibonacciSphere(bm, radius, res):
    """
    create Fibonacci Sphere (vertices only)

    :param bm:
    :param radius:
    :param res:
    """
    if res <= 1:
        res = 2

    phi = math.pi * (3. - math.sqrt(5.))  # golden angle (radians)

    for i in range(res):
        theta = phi * i
        z = - 1 + (i / (res - 1)) * 2
        dist_z = math.sqrt(1 - z ** 2)
        x = math.cos(theta) * dist_z
        y = math.sin(theta) * dist_z
        coords = np.array([x, y, z])

        bm.verts.new(coords * radius)
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

    createFibonacciSphere(bm, radius, res)
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
