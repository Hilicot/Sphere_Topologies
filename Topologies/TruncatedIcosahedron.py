import numpy as np
from numpy.linalg import norm
from .funcs.general_functions import *
from .Topologies.Icosahedron import getNewBaseIcosahedron, subdivide
from .funcs.general_functions import getFlatAngle


def getLabel():
    return "Truncated Icosahedron"


def getOperator():
    return "mesh.create_truncated_icosahedron"


# create operator
class MESH_OT_CreateTruncatedIcosahedron(bpy.types.Operator):
    bl_idname = getOperator()
    bl_label = getLabel()

    def execute(self, context):
        (obj, mesh) = createNewEmptyObject(getLabel())

        # create Bmesh
        bm = getNewBaseIcosahedron(2)
        bm = truncateSolid(bm)
        bm.to_mesh(mesh)
        obj.select_set(True)

        # set properties
        props = mesh.SphereTopology
        props.sphere_radius = 2
        props.sphere_type = getLabel()
        props.sphere_resolution = 1
        setSphereUpdated(props)
        props.sphere_do_update = True

        return {'FINISHED'}


def register():
    bpy.utils.register_class(MESH_OT_CreateTruncatedIcosahedron)


def unregister():
    bpy.utils.unregister_class(MESH_OT_CreateTruncatedIcosahedron)


############################################

# ATTENTION! updateSphereResolution() doesn't normalize vertices to keep the same dimensions of the generating Icosahedron.
# this means that morphSphere() will have a "jump" the first time it is used

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
    radius = mytool.sphere_radius
    bm.verts.ensure_lookup_table()

    # get bmesh of default IcoSphere
    bm = getNewBaseIcosahedron(radius)
    iterations = res - 1

    # noinspection PyTypeChecker
    subdivide(bm, iterations, radius)
    bm = truncateSolid(bm)

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

    # update all vertices
    for v in bm.verts:
        normalizeVert(v, radius)

    bm.to_mesh(mesh)
    bm.free()
    setSphereUpdated(mytool)


def truncateSolid(bm_old) -> bmesh:
    bm = bmesh.new()
    bm_old.normal_update()

    pentagon_vertices = {v: [] for v in bm_old.verts}
    hexagon_vertices = {f: [] for f in bm_old.faces}
    for edge in bm_old.edges:
        a = np.array(edge.verts[0].co)
        b = np.array(edge.verts[1].co)
        v1 = bm.verts.new((2 * a + b) / 3)
        v2 = bm.verts.new((a + 2 * b) / 3)
        pentagon_vertices[edge.verts[0]].append(v1)
        pentagon_vertices[edge.verts[1]].append(v2)
        hexagon_vertices[edge.link_faces[0]] += [v1, v2]
        hexagon_vertices[edge.link_faces[1]] += [v1, v2]
    bm.verts.ensure_lookup_table()

    # for each pentagon and hexagon, sort vertices in anticlockwise order around the old vertex/face normal and create new face
    for old_elem, vertices in {**pentagon_vertices, **hexagon_vertices}.items():
        orderedVerts = sortAntiClockwise3D(old_elem.normal, vertices)
        bm.faces.new(orderedVerts)

    bm_old.free()
    return bm


def sortAntiClockwise3D(normal, verts):
    # if normal is vertical, use simple flat trigonometry
    if abs(normal[0]) < 0.0001 and abs(normal[1]) < 0.0001:
        return sorted(verts, key=lambda v: getFlatAngle(v.co))
    # convert to local coordinates on the 2D plane of the future face to sort using flat angles
    n = np.array(normal)
    z = n / norm(n)
    u = np.array([0, 0, 1])
    k = u - np.dot(u, z) * z
    x = k / norm(k)
    y = np.cross(z, x)
    return sorted(verts, key=lambda vert: getFlatAngle(convertToFlatCoordinates(vert.co, x, y)))


def convertToFlatCoordinates(coords, x, y):
    co = np.array(coords)
    return [np.dot(co, x), np.dot(co, y)]
