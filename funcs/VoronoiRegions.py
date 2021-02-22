import bpy
import bmesh
import numpy as np
from funcs.general_functions import getCurrentBMesh


class IncorrectTopology(Exception):
    pass


# operator
class MESH_OT_TransformToVoronoi(bpy.types.Operator):
    """Transform current mesh topology using Voronoi regions"""
    bl_idname = "mesh.transform_to_voronoi"
    bl_label = "Convert to Voronoi regions"

    def execute(self, context):
        mesh = getCurrentBMesh()

        bm = bmesh.new()
        bm.from_mesh(mesh)

        bm = voronoiTransform(bm)

        bm.to_mesh(mesh)
        bm.free()

        self.report({'INFO'}, "transformed to Voronoi ")

        return {'FINISHED'}


def voronoiTransform(bm, discard_old=True):
    """
    return a different bmesh with the Voronoi regions of <bm>
    ATTENTION: to be compatible with non-spheres as well, it doesn't renormalize the new vertices, so the final mesh will be a bit smaller
    ATTENTION2: all faces in <bm> must be triangles

    :param Boolean discard_old: if True, free old <bm> reference
    :param Bmesh bm:
    :return Bmesh new_bm: a different Bmesh with the voronoi regions
    """
    new_bm = bm.copy()

    # calculate circumcenters of the faces
    circumcenters = dict()
    for face in bm.faces:
        if len(face.verts) != 3:
            new_bm.free()
            raise IncorrectTopology("The mesh must only contain triangles")
        a = np.array(face.verts[0].co)
        b = np.array(face.verts[1].co)
        c = np.array(face.verts[2].co)
        ac = c - a
        ab = b - a
        abXac = np.cross(ab, ac)

        circ_co = a + (np.cross(abXac, ab) * ac.dot(ac) + np.cross(ac, abXac) * ab.dot(ab)) / (2 * abXac.dot(abXac))
        circ = new_bm.verts.new(circ_co)
        circumcenters[face] = circ

    new_bm.verts.ensure_lookup_table()

    # for each vertex, create face with circumcenters of adjacent faces
    bm.normal_update()
    for v in bm.verts:
        face_verts = getOrderedVertices(v, circumcenters)
        if len(face_verts) > 2:
            new_bm.faces.new(face_verts)
    new_bm.faces.ensure_lookup_table()

    if discard_old:
        bm.free()

    return new_bm


def getOrderedVertices(v, circumcenters):
    """
    get all circumcenters of the adjacent faces to the vertex <v> and order them in a clockwise direction relative to <v>'s normal

    :param v:
    :param circumcenters:
    """

    faces = list(v.link_faces)
    circs = []

    # starting from a random face, visit all the neighbouring faces one by one to keep a constant direction
    face = faces.pop(0)
    verts_set = set(face.verts)
    circs.append(circumcenters[face])
    for i in range(len(v.link_faces) - 1):
        for f in faces:
            if len(verts_set.intersection(f.verts)) > 1:
                # if 2 faces have more than one vertex in common, they are adjacent
                verts_set = set(f.verts)
                circs.append(circumcenters[f])
                faces.remove(f)
                break

    # check if vertices are in counterclockwise order relative to <v>'s normal, else invert them
    normal = np.array(v.normal)
    v_c = np.array(v.co)
    a = np.array(circs[0].co) - v_c
    b = np.array(circs[1].co) - v_c
    if np.cross(a, b).dot(normal) < 0:
        circs = circs[::-1]

    return circs


def register():
    bpy.utils.register_class(MESH_OT_TransformToVoronoi)


def unregister():
    bpy.utils.unregister_class(MESH_OT_TransformToVoronoi)
