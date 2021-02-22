import bmesh
from funcs.general_functions import *

LABEL = "Icosahedron"
OPERATOR = "mesh.create_icosahedron"


# create operator
class MESH_OT_CreateIcosahedron(bpy.types.Operator):
    bl_idname = OPERATOR
    bl_label = LABEL

    def execute(self, context):
        (obj, mesh) = createNewEmptyObject(LABEL)

        # create Bmesh
        bm = getNewBaseIcosahedron(2)
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
    bpy.utils.register_class(MESH_OT_CreateIcosahedron)


def unregister():
    bpy.utils.unregister_class(MESH_OT_CreateIcosahedron)


############################################


def subdivide(bm, iterations, radius) -> None:
    """
    Subdivide <iterations> times the input icosahedron bmesh <bm>

    :rtype: None
    :param bmesh bm:
    :param int iterations:
    :param float radius:
    """

    for i in range(iterations):

        faceListCopy = list(bm.faces).copy()
        edgeListCopy = list(bm.edges).copy()

        medianPoints = {}
        bm.edges.ensure_lookup_table()
        for edge in bm.edges:
            # get median point position, normalize and create median vertex
            co = [edge.verts[0].co[i] + edge.verts[1].co[i] for i in range(3)]
            v = bm.verts.new(co)
            bm.verts.ensure_lookup_table()
            normalizeVert(v, radius)
            medianPoints[getEdgeTuple(edge)] = v

        points = [0] * 3
        for x, face in enumerate(faceListCopy):
            bm.faces.ensure_lookup_table()

            # get the 3 median points of the 3 edges
            for j, edge in enumerate(face.edges):
                points[j] = medianPoints[getEdgeTuple(edge)]
            # create 4 smaller faces for each face, delete old face
            bm.faces.new([face.verts[0], points[0], points[2]])
            bm.faces.ensure_lookup_table()
            bm.faces.new([face.verts[1], points[1], points[0]])
            bm.faces.ensure_lookup_table()
            bm.faces.new([face.verts[2], points[2], points[1]])
            bm.faces.ensure_lookup_table()
            bm.faces.new([points[0], points[1], points[2]])
            bm.faces.ensure_lookup_table()
            bm.faces.remove(face)

        for edge in edgeListCopy:
            bm.edges.remove(edge)
            bm.edges.ensure_lookup_table()


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


def getNewBaseIcosahedron(radius):
    """
    create basic 12-vertex Icosahedron

    :param radius:
    :return BMesh bm: the resulting icosahedron mesh
    """
    # get clean Bmesh container
    bm = bmesh.new()

    # place vertex one by one
    t = (1 + 5 ** 0.5) / 2  # golden ratio

    bm.verts.new(normalize([-1, t, 0], radius))
    bm.verts.new(normalize([1, t, 0], radius))
    bm.verts.new(normalize([-1, -t, 0], radius))
    bm.verts.new(normalize([1, -t, 0], radius))
    bm.verts.new(normalize([0, -1, t], radius))
    bm.verts.new(normalize([0, 1, t], radius))
    bm.verts.new(normalize([0, -1, -t], radius))
    bm.verts.new(normalize([0, 1, -t], radius))
    bm.verts.new(normalize([t, 0, -1], radius))
    bm.verts.new(normalize([t, 0, 1], radius))
    bm.verts.new(normalize([-t, 0, -1], radius))
    bm.verts.new(normalize([-t, 0, 1], radius))
    bm.verts.ensure_lookup_table()

    insertFace(bm, [0, 11, 5])
    insertFace(bm, [0, 5, 1])
    insertFace(bm, [0, 1, 7])
    insertFace(bm, [0, 7, 10])
    insertFace(bm, [0, 10, 11])
    insertFace(bm, [1, 5, 9])
    insertFace(bm, [5, 11, 4])
    insertFace(bm, [11, 10, 2])
    insertFace(bm, [10, 7, 6])
    insertFace(bm, [7, 1, 8])
    insertFace(bm, [3, 9, 4])
    insertFace(bm, [3, 4, 2])
    insertFace(bm, [3, 2, 6])
    insertFace(bm, [3, 6, 8])
    insertFace(bm, [3, 8, 9])
    insertFace(bm, [4, 9, 5])
    insertFace(bm, [2, 4, 11])
    insertFace(bm, [6, 2, 10])
    insertFace(bm, [8, 6, 7])
    insertFace(bm, [9, 8, 1])

    return bm


def getEdgeTuple(edge):
    a = edge.verts[0]
    b = edge.verts[1]
    return (a, b) if a.index < b.index else (b, a)
